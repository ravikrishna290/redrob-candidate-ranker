import time
from sentence_transformers import SentenceTransformer, CrossEncoder

print("Downloading/loading BAAI/bge-small-en-v1.5...")
t0 = time.time()
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print(f"Loaded embedding model in {time.time() - t0:.2f} seconds.")

print("Downloading/loading cross-encoder/ms-marco-MiniLM-L-6-v2...")
t0 = time.time()
rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print(f"Loaded rerank model in {time.time() - t0:.2f} seconds.")
