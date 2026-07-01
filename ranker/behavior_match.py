def calculate_behavior_fit(cand_features, parsed_jd, raw_signals):
    """
    Computes experience fit, location fit, salary fit, and returns a combined score.
    """
    score = 0.5 # Baseline
    
    # 1. Experience Fit
    exp_years = cand_features.get("exp_years", 0)
    min_exp = parsed_jd.get("min_experience", 4.0)
    max_exp = parsed_jd.get("max_experience", 15.0)
    
    if exp_years < min_exp:
        # Penalty for under-experience (smooth)
        score -= min(0.3, (min_exp - exp_years) * 0.1)
    elif min_exp <= exp_years <= 9.0:
        # Sweet spot bonus (5-9 years)
        score += 0.15
    elif 9.0 < exp_years <= max_exp:
        # Senior experience (still good, but maybe slightly higher cost/less shipping bias depending on career history)
        score += 0.05
    else:
        # Over-experienced (may be too senior for founding team coder role unless they are Hands-on)
        score -= min(0.2, (exp_years - max_exp) * 0.02)
        
    # 2. Location & Work Mode Fit
    preferred_locs = parsed_jd.get("target_locations", [])
    cand_location = raw_signals.get("location", "").lower()
    cand_country = raw_signals.get("country", "").lower()
    
    # Check if candidate is in India
    in_india = cand_country == "india" or any(loc in cand_location for loc in ["india", "bangalore", "bengaluru", "pune", "noida", "hyderabad", "mumbai", "delhi", "gurgaon", "chennai"])
    
    if in_india:
        score += 0.05
        # Check specific tech hubs
        if any(loc in cand_location for loc in preferred_locs):
            score += 0.05
    else:
        score -= 0.1 # Remote/non-India penalty if they want local founding team
        
    # 3. Willing to relocate / Preferred work mode
    work_mode = raw_signals.get("preferred_work_mode", "").lower()
    relocate = raw_signals.get("willing_to_relocate", False)
    
    if work_mode == "hybrid" or work_mode == "on-site":
        score += 0.03
    if relocate:
        score += 0.02
        
    # 4. Combine with the precomputed behavioral score (GitHub, response rate, etc.)
    base_behav = cand_features.get("behavioral_score", 0.5)
    
    # 5. Final combined fit
    # 40% experience fit, 20% location/work-mode, 40% platform behavioral signals
    final_score = 0.4 * ((score + 0.5) / 2.0) + 0.2 * (1.0 if in_india else 0.0) + 0.4 * base_behav
    return min(1.0, max(0.0, final_score))
