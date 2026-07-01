import os
import sys
import json
import time
import numpy as np
import pandas as pd
import subprocess
from sentence_transformers import SentenceTransformer

# Add parent directory to path so we can import preprocess modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocess.load_candidates import stream_candidates
from preprocess.normalize_candidates import normalize_candidate
from preprocess.extract_features import extract_features

def main():
    sample_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\sample_candidates.json"
    jd_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\job_description.docx"
    
    scratch_dir = r"d:\Redrob AI hackathon\redrob-ai\scratch"
    os.makedirs(scratch_dir, exist_ok=True)
    
    temp_features_path = os.path.join(scratch_dir, "sample_features.jsonl")
    temp_embeddings_path = os.path.join(scratch_dir, "sample_embeddings.npy")
    
    # 1. Precompute on sample candidates if not already computed
    if not os.path.exists(temp_features_path) or not os.path.exists(temp_embeddings_path):
        print("1. Precomputing features and embeddings on sample_candidates.json...")
        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
        
        texts = []
        features = []
        
        for cand in stream_candidates(sample_path):
            norm_cand = normalize_candidate(cand)
            feat = extract_features(norm_cand)
            features.append(feat)
            texts.append(feat["semantic_text"])
            
        print(f"Loaded and extracted features for {len(features)} sample candidates.")
        
        with open(temp_features_path, "w", encoding="utf-8") as f:
            for feat in features:
                f.write(json.dumps(feat) + "\n")
                
        t0 = time.time()
        embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
        print(f"Encoded in {time.time() - t0:.2f} seconds.")
        np.save(temp_embeddings_path, embeddings)
    else:
        print("Precomputed sample features and embeddings already exist. Skipping.")
        
    # 2. Run ranking pipeline (main.py)
    output_csv = os.path.join(scratch_dir, "sample_output.csv")
    print(f"2. Running main.py on sample candidates. Output: {output_csv}")
    
    cmd = [
        "python", "redrob-ai/main.py",
        "--jd", jd_path,
        "--candidates", sample_path,
        "--output", output_csv,
        "--features", temp_features_path,
        "--embeddings", temp_embeddings_path
    ]
    
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"main.py execution finished in {time.time() - t0:.2f} seconds.")
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
        
    # 3. Read generated CSV, pad to 100 rows, and write to team_test.csv
    test_csv = os.path.join(scratch_dir, "team_test.csv")
    print(f"Padding {output_csv} to 100 rows and saving to {test_csv}...")
    
    df = pd.read_csv(output_csv)
    n_rows = len(df)
    
    if n_rows < 100:
        # Create dummy rows
        last_score = df.iloc[-1]["score"] if n_rows > 0 else 0.5
        dummies = []
        for i in range(n_rows + 1, 101):
            # decrement score slightly to maintain non-increasing order
            last_score -= 0.001
            # pad candidate ID with 7 digits (e.g. CAND_9900000)
            dummies.append({
                "candidate_id": f"CAND_{9900000 + i:07d}",
                "rank": i,
                "score": round(max(0.0, last_score), 6),
                "reasoning": f"Dummy candidate padded to reach 100 validation rows. Index: {i}."
            })
        df_padded = pd.concat([df, pd.DataFrame(dummies)], ignore_index=True)
    else:
        df_padded = df.iloc[:100]
        
    df_padded.to_csv(test_csv, index=False)
    print(f"Saved padded CSV to {test_csv}.")
    
    # 4. Validate the output using validate_submission.py
    validator_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\validate_submission.py"
    print(f"4. Running validate_submission.py on {test_csv}...")
    
    val_cmd = [
        "python", validator_path,
        test_csv
    ]
    
    val_result = subprocess.run(val_cmd, capture_output=True, text=True)
    print("Validator Output:")
    print(val_result.stdout)
    if val_result.stderr:
        print("Validator Errors:")
        print(val_result.stderr)

if __name__ == "__main__":
    main()
