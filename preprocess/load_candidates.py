import json
import gzip
import os

def stream_candidates(filepath):
    """
    Yields candidate records one by one from a .jsonl or .jsonl.gz file.
    """
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
    else:
        # Check if the file is a JSON array
        with open(filepath, 'r', encoding='utf-8') as f:
            first_char = f.read(1).strip()
            while not first_char and len(first_char) > 0:
                first_char = f.read(1).strip()
            
            f.seek(0)
            if first_char == '[':
                # Load as list
                data = json.load(f)
                for item in data:
                    yield item
            else:
                for line in f:
                    if line.strip():
                        yield json.loads(line)

if __name__ == "__main__":
    # Quick sanity test
    default_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
    if os.path.exists(default_path):
        print("Streaming first 2 candidates for test...")
        for idx, cand in enumerate(stream_candidates(default_path)):
            if idx >= 2:
                break
            print(f"Candidate ID: {cand['candidate_id']} | Name: {cand['profile']['anonymized_name']}")
    else:
        print("Candidates file not found at default path.")
