import os
import sys
import argparse
import json
import time
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import torch

# Optimize CPU threads for PyTorch models
torch.set_num_threads(min(8, os.cpu_count() or 4))

# Add the current folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ranker.jd_parser import parse_jd
from ranker.semantic_match import compute_semantic_scores, get_jd_query_text
from ranker.skill_match import calculate_skill_match_score
from ranker.behavior_match import calculate_behavior_fit
from ranker.trap_detector import detect_traps
from ranker.hybrid_score import calculate_hybrid_score
from ranker.reranker import rerank_candidates
from ranker.explain import generate_reasoning
from preprocess.load_candidates import stream_candidates

def read_docx_text(path):
    """
    Reads text content from a .docx file using standard library zipfile.
    Fallback to standard text reading if zipfile fails.
    """
    try:
        with zipfile.ZipFile(path) as docx:
            tree = ET.fromstring(docx.read('word/document.xml'))
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for paragraph in tree.iter(f"{{{namespace['w']}}}p"):
                texts = [node.text for node in paragraph.iter(f"{{{namespace['w']}}}t") if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        # Fallback to standard text reading
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def main():
    parser = argparse.ArgumentParser(description="Redrob AI Candidate Ranker")
    parser.add_argument("--jd", type=str, required=True, help="Path to Job Description file (.docx or .txt)")
    parser.add_argument("--candidates", type=str, required=True, help="Path to candidates.jsonl file")
    parser.add_argument("--output", type=str, required=True, help="Path to save output CSV file")
    parser.add_argument("--features", type=str, default=None, help="Optional path to candidate_features.jsonl")
    parser.add_argument("--embeddings", type=str, default=None, help="Optional path to candidate_embeddings.npy")
    args = parser.parse_args()
    
    t_start = time.time()
    
    # 1. Load Job Description
    print(f"Reading job description from {args.jd}...")
    if args.jd.endswith(".docx"):
        jd_text = read_docx_text(args.jd)
    else:
        with open(args.jd, "r", encoding="utf-8", errors="ignore") as f:
            jd_text = f.read()
            
    parsed_jd = parse_jd(jd_text)
    print(f"Parsed Job Title: {parsed_jd['role_title']}")
    print(f"Required Must-Haves: {parsed_jd['must_have_skills'][:4]}...")
    
    # 2. Load precomputed features and embeddings
    script_dir = os.path.dirname(os.path.abspath(__file__))
    precomputed_dir = os.path.join(script_dir, "scratch")
    
    features_path = args.features if args.features else os.path.join(precomputed_dir, "candidate_features.jsonl")
    embeddings_path = args.embeddings if args.embeddings else os.path.join(precomputed_dir, "candidate_embeddings.npy")
    
    print(f"Loading precomputed candidate features from {features_path}...")
    t0 = time.time()
    candidates_features = {}
    with open(features_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                feat = json.loads(line)
                candidates_features[feat["candidate_id"]] = feat
    print(f"Loaded features in {time.time() - t0:.2f} seconds.")
    
    print(f"Loading precomputed candidate embeddings from {embeddings_path}...")
    t0 = time.time()
    embeddings = np.load(embeddings_path)
    print(f"Loaded embeddings matrix of shape {embeddings.shape} in {time.time() - t0:.2f} seconds.")
    
    # 3. Load raw candidates (needed for skills and career history verification)
    print(f"Streaming raw candidates from {args.candidates} to map with features...")
    t0 = time.time()
    raw_candidates = {}
    
    for c in stream_candidates(args.candidates):
        raw_candidates[c["candidate_id"]] = c
    print(f"Loaded raw candidates in {time.time() - t0:.2f} seconds.")
    
    # 4. Compute semantic similarity scores
    print("Computing semantic similarity scores...")
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    
    query_text = get_jd_query_text(parsed_jd)
    semantic_scores, raw_similarities = compute_semantic_scores(embeddings, query_text, embedding_model)
    
    # 5. Hybrid scoring and trap detection for all candidates
    print("Running hybrid scoring and trap detection...")
    t0 = time.time()
    
    candidate_keys = list(candidates_features.keys())
    scored_candidates = []
    
    for idx, cid in enumerate(candidate_keys):
        feat = candidates_features[cid]
        raw_cand = raw_candidates.get(cid)
        if not raw_cand:
            continue
            
        # Detect traps
        is_trap, trap_reasons = detect_traps(raw_cand)
        
        # Calculate skills score
        skill_score = calculate_skill_match_score(raw_cand.get("skills", []), parsed_jd)
        
        # Calculate behavior fit
        behavior_score = calculate_behavior_fit(feat, parsed_jd, raw_cand.get("redrob_signals", {}))
        
        # Get semantic score
        sem_score = float(semantic_scores[idx])
        
        # Calculate final hybrid score
        hybrid_score = calculate_hybrid_score(feat, sem_score, skill_score, behavior_score, is_trap)
        
        scored_candidates.append({
            "candidate_id": cid,
            "hybrid_score": hybrid_score,
            "semantic_text": feat["semantic_text"],
            "raw_cand": raw_cand,
            "feat": feat
        })
        
    print(f"Scored {len(scored_candidates)} candidates in {time.time() - t0:.2f} seconds.")
    
    # 6. Retrieve top 500 candidates by hybrid score
    # To break ties consistently, sort by hybrid_score desc, then candidate_id asc
    scored_candidates = sorted(
        scored_candidates,
        key=lambda x: (-x["hybrid_score"], x["candidate_id"])
    )
    
    top_k_candidates = scored_candidates[:500]
    print(f"Selected top 500 candidates for CrossEncoder reranking.")
    
    # 7. CrossEncoder Reranking
    from sentence_transformers import CrossEncoder
    rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
    
    reranked_candidates = rerank_candidates(top_k_candidates, query_text, rerank_model)
    
    # 8. Select top 100, generate reasoning, and prepare CSV
    print("Generating reasoning for final top 100 candidates...")
    final_100 = reranked_candidates[:100]
    
    output_rows = []
    for rank, c in enumerate(final_100, 1):
        cid = c["candidate_id"]
        score = c["final_score"]
        raw_cand = c["raw_cand"]
        feat = c["feat"]
        
        reasoning = generate_reasoning(raw_cand, feat, parsed_jd)
        
        output_rows.append({
            "candidate_id": cid,
            "rank": rank,
            "score": round(score, 6),
            "reasoning": reasoning
        })
        
    # Write to CSV or Excel depending on output path extension
    df = pd.DataFrame(output_rows)
    # Ensure correct columns
    df = df[["candidate_id", "rank", "score", "reasoning"]]
    if args.output.lower().endswith(".xlsx"):
        df.to_excel(args.output, index=False)
    else:
        df.to_csv(args.output, index=False)
    print(f"Successfully saved ranked results to {args.output}")
    print(f"Total pipeline runtime: {time.time() - t_start:.2f} seconds.")

if __name__ == "__main__":
    main()
