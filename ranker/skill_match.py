# Mapping of skill categories to candidate skills that satisfy them
SKILL_EXPANSIONS = {
    "embeddings-based retrieval systems": ["embeddings", "sentence-transformers", "retrieval", "search", "dense retrieval", "bge", "e5"],
    "vector databases": ["pinecone", "milvus", "qdrant", "weaviate", "faiss", "chromadb", "vector search"],
    "hybrid search": ["elasticsearch", "opensearch", "bm25", "hybrid search", "hybrid retrieval"],
    "evaluation frameworks": ["ndcg", "mrr", "map", "a/b testing", "evaluation", "offline-to-online correlation", "ranking metrics"],
    "llm fine-tuning": ["lora", "qlora", "peft", "fine-tuning", "sft", "rlhf", "llama", "mistral"],
    "learning-to-rank": ["xgboost", "learning-to-rank", "learning to rank", "lightgbm", "cohere rerank"]
}

def calculate_skill_match_score(candidate_skills, parsed_jd):
    """
    Computes a modular skill match score between candidate skills and JD requirements.
    """
    cand_skill_map = {s["name"].lower(): s for s in candidate_skills}
    
    must_have_required = parsed_jd.get("must_have_skills", [])
    preferred_required = parsed_jd.get("preferred_skills", [])
    
    # 1. Score Must-Haves
    must_have_score = 0.0
    must_have_count = 0
    
    for req in must_have_required:
        # Check direct match
        matched = False
        prof_multiplier = 0.0
        
        # Direct check
        if req in cand_skill_map:
            matched = True
            prof = cand_skill_map[req]["proficiency"]
            prof_multiplier = 1.0 if prof == "expert" else 0.8 if prof == "advanced" else 0.5 if prof == "intermediate" else 0.2
        else:
            # Check expansion synonyms
            expansions = SKILL_EXPANSIONS.get(req, [req])
            for exp in expansions:
                if exp in cand_skill_map:
                    matched = True
                    prof = cand_skill_map[exp]["proficiency"]
                    # Take highest proficiency among matches
                    m = 1.0 if prof == "expert" else 0.8 if prof == "advanced" else 0.5 if prof == "intermediate" else 0.2
                    prof_multiplier = max(prof_multiplier, m)
                    
        if matched:
            must_have_score += prof_multiplier
            must_have_count += 1
            
    must_have_ratio = must_have_score / len(must_have_required) if must_have_required else 1.0
    
    # 2. Score Preferred
    preferred_score = 0.0
    preferred_count = 0
    
    for req in preferred_required:
        matched = False
        prof_multiplier = 0.0
        
        if req in cand_skill_map:
            matched = True
            prof = cand_skill_map[req]["proficiency"]
            prof_multiplier = 1.0 if prof == "expert" else 0.8 if prof == "advanced" else 0.5 if prof == "intermediate" else 0.2
        else:
            expansions = SKILL_EXPANSIONS.get(req, [req])
            for exp in expansions:
                if exp in cand_skill_map:
                    matched = True
                    prof = cand_skill_map[exp]["proficiency"]
                    m = 1.0 if prof == "expert" else 0.8 if prof == "advanced" else 0.5 if prof == "intermediate" else 0.2
                    prof_multiplier = max(prof_multiplier, m)
                    
        if matched:
            preferred_score += prof_multiplier
            preferred_count += 1
            
    preferred_ratio = preferred_score / len(preferred_required) if preferred_required else 1.0
    
    # Combine must-have and preferred: 70% must-have, 30% preferred
    final_skill_score = 0.7 * must_have_ratio + 0.3 * preferred_ratio
    return final_skill_score
