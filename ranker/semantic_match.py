import numpy as np
from sentence_transformers import SentenceTransformer

def get_jd_query_text(parsed_jd):
    """
    Constructs a dense search query from the parsed job description.
    """
    role = parsed_jd.get("role_title", "Senior AI Engineer")
    must_have = ", ".join(parsed_jd.get("must_have_skills", []))
    preferred = ", ".join(parsed_jd.get("preferred_skills", []))
    
    query = f"{role}. Core requirements: {must_have}. Preferred: {preferred}."
    return query

def compute_semantic_scores(candidates_embeddings, query_text, model=None):
    """
    Computes cosine similarity between the query text and all candidate embeddings.
    """
    if model is None:
        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
        
    # Add prefix for retrieval query as required by BAAI/bge-small-en-v1.5
    query_prefix = "Represent this sentence for searching relevant passages: "
    full_query = query_prefix + query_text
    
    # Compute query embedding
    query_embedding = model.encode(full_query, convert_to_numpy=True)
    
    # Normalize embeddings for cosine similarity
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    cand_norms = np.linalg.norm(candidates_embeddings, axis=1, keepdims=True)
    
    # Avoid division by zero
    cand_norms[cand_norms == 0] = 1.0
    normalized_cands = candidates_embeddings / cand_norms
    
    # Calculate cosine similarities
    similarities = np.dot(normalized_cands, query_norm)
    
    # Normalize scores to [0, 1] range (since cosine sim for BGE is usually positive and concentrated)
    # Mapping [0.4, 0.9] -> [0, 1] is typical, but let's do simple min-max scaling or clip
    min_val = similarities.min()
    max_val = similarities.max()
    if max_val > min_val:
        scores = (similarities - min_val) / (max_val - min_val)
    else:
        scores = np.zeros_like(similarities)
        
    return scores, similarities
