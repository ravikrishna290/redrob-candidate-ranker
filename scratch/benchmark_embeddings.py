import time
import json
from sentence_transformers import SentenceTransformer

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

texts = []
with open(candidates_path, "r", encoding="utf-8") as f:
    for i in range(100):
        line = f.readline()
        if not line:
            break
        c = json.loads(line)
        p = c.get("profile", {})
        texts.append(f"{p.get('headline', '')} {p.get('summary', '')}")

print(f"Encoding {len(texts)} samples on CPU...")
t0 = time.time()
embeddings = embedding_model.encode(texts, batch_size=32, show_progress_bar=False)
t1 = time.time()
elapsed = t1 - t0
print(f"Encoded in {elapsed:.2f} seconds. Rate: {len(texts)/elapsed:.2f} samples/second.")
