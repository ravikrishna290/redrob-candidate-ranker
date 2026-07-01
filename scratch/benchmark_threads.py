import os
import sys
import time
import torch
from sentence_transformers import CrossEncoder

def main():
    model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
    
    # Create 500 dummy pairs
    pairs = [("Senior AI Engineer - Founding Team", "Candidate is a Senior ML developer with experience in PyTorch and vector databases like FAISS and Pinecone. Notice period 30 days.")] * 500
    
    # Try different thread counts
    for num_threads in [1, 2, 4, 6, 8, 12]:
        torch.set_num_threads(num_threads)
        
        # Warmup
        model.predict(pairs[:10], batch_size=32, show_progress_bar=False)
        
        t0 = time.time()
        model.predict(pairs, batch_size=64, show_progress_bar=False)
        duration = time.time() - t0
        print(f"Threads: {num_threads} -> Time: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
