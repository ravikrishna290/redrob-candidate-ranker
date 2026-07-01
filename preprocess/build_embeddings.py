import os
import sys
import json
import time
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Add parent directory to path so we can import preprocess modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocess.load_candidates import stream_candidates
from preprocess.normalize_candidates import normalize_candidate
from preprocess.extract_features import extract_features

def main():
    candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
    output_dir = r"d:\Redrob AI hackathon\redrob-ai\scratch"
    os.makedirs(output_dir, exist_ok=True)
    
    features_out_path = os.path.join(output_dir, "candidate_features.jsonl")
    embeddings_out_path = os.path.join(output_dir, "candidate_embeddings.npy")
    
    print(f"Loading embedding model BAAI/bge-small-en-v1.5...")
    t0 = time.time()
    # Ensure CPU is used and specify cache folder if needed
    model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    print(f"Loaded embedding model in {time.time() - t0:.2f} seconds.")
    
    print("Starting precomputation pipeline...")
    batch_size = 1000
    current_batch_texts = []
    current_batch_features = []
    
    all_embeddings = []
    
    # Open features output file
    with open(features_out_path, "w", encoding="utf-8") as feat_file:
        t_start = time.time()
        count = 0
        
        for cand in stream_candidates(candidates_path):
            count += 1
            
            # Normalize and extract features
            norm_cand = normalize_candidate(cand)
            feat = extract_features(norm_cand)
            
            current_batch_features.append(feat)
            current_batch_texts.append(feat["semantic_text"])
            
            # Write feature to JSONL (excluding semantic_text to save disk space if desired, or keep it)
            # We keep it because we might need it for explanation generation or cross-encoder reranking!
            feat_file.write(json.dumps(feat) + "\n")
            
            # If batch is full, encode and reset
            if len(current_batch_texts) >= batch_size:
                t_b0 = time.time()
                # Encode batch
                embeddings = model.encode(
                    current_batch_texts, 
                    batch_size=128, 
                    show_progress_bar=False, 
                    convert_to_numpy=True
                )
                all_embeddings.append(embeddings)
                t_b1 = time.time()
                
                print(f"Processed {count} candidates... (Last batch encode rate: {len(current_batch_texts)/(t_b1-t_b0):.1f} samples/sec)")
                current_batch_texts = []
                current_batch_features = []
                
        # Process remaining
        if current_batch_texts:
            embeddings = model.encode(
                current_batch_texts, 
                batch_size=128, 
                show_progress_bar=False, 
                convert_to_numpy=True
            )
            all_embeddings.append(embeddings)
            print(f"Processed final batch of {len(current_batch_texts)} candidates.")
            
    # Concatenate and save embeddings
    print("Concatenating and saving embeddings...")
    final_embeddings = np.concatenate(all_embeddings, axis=0)
    np.save(embeddings_out_path, final_embeddings)
    
    t_end = time.time()
    print(f"Successfully finished preprocessing 100,000 candidates in {(t_end - t_start)/60:.2f} minutes!")
    print(f"Features saved to: {features_out_path}")
    print(f"Embeddings saved to: {embeddings_out_path}")

if __name__ == "__main__":
    main()
