import time
import numpy as np
from sentence_transformers import CrossEncoder

def rerank_candidates(top_candidates, query_text, rerank_model=None):
    """
    Reranks the top candidates using cross-encoder/ms-marco-MiniLM-L-6-v2.
    Arguments:
        top_candidates (list of dicts): Must contain 'candidate_id', 'hybrid_score', 'semantic_text'
        query_text (str): Job description search query
        rerank_model (CrossEncoder): Optional pre-loaded cross-encoder
    Returns:
        reranked_candidates (list of dicts): Candidates sorted by the final reranked score in non-increasing order.
    """
    if not top_candidates:
        return []
        
    if rerank_model is None:
        print("Loading CrossEncoder model...")
        t0 = time.time()
        rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cpu")
        print(f"CrossEncoder loaded in {time.time() - t0:.2f} seconds.")
        
    pairs = [(query_text, c["semantic_text"]) for c in top_candidates]
    
    t0 = time.time()
    # Predict relevance scores
    ce_scores = rerank_model.predict(pairs, batch_size=32, show_progress_bar=False)
    print(f"Reranked {len(top_candidates)} candidates in {time.time() - t0:.2f} seconds.")
    
    # Normalize cross-encoder scores to [0, 1] range
    min_val = ce_scores.min()
    max_val = ce_scores.max()
    if max_val > min_val:
        norm_ce_scores = (ce_scores - min_val) / (max_val - min_val)
    else:
        norm_ce_scores = np.zeros_like(ce_scores)
        
    # Interpolate scores
    for idx, c in enumerate(top_candidates):
        c["ce_score"] = float(ce_scores[idx])
        c["norm_ce_score"] = float(norm_ce_scores[idx])
        # 50% hybrid score + 50% cross-encoder score
        c["final_score"] = 0.5 * c["hybrid_score"] + 0.5 * c["norm_ce_score"]
        
    # Sort candidates by final score (descending) and candidate_id (ascending) to break ties
    # This aligns perfectly with the sorting rules in validate_submission.py
    reranked = sorted(
        top_candidates,
        key=lambda x: (-x["final_score"], x["candidate_id"])
    )
    
    return reranked
