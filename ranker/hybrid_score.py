def calculate_hybrid_score(cand_features, semantic_score, skill_score, behavior_score, is_trap):
    """
    Combines individual scores into a single final score.
    If the candidate is flagged as a trap/honeypot, the score is forced to 0.0.
    """
    if is_trap:
        return 0.0
        
    growth_score = cand_features.get("growth_score", 0.5)
    stability_score = cand_features.get("stability_score", 0.5)
    growth_stability_score = 0.5 * growth_score + 0.5 * stability_score
    
    # Weights
    w_semantic = 0.35
    w_skill = 0.35
    w_behavior = 0.20
    w_growth_stability = 0.10
    
    score = (
        w_semantic * semantic_score +
        w_skill * skill_score +
        w_behavior * behavior_score +
        w_growth_stability * growth_stability_score
    )
    
    # Small boost for matching role titles (e.g. current title is Senior AI / Lead AI / Founding AI Engineer)
    # We can check the domain relevance and apply a small boost
    domain_relevance = cand_features.get("domain_relevance", 0.0)
    score += domain_relevance * 0.05
    
    return min(1.0, max(0.0, score))
