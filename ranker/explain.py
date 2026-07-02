def generate_reasoning(cand, cand_features, parsed_jd, rank=None):
    """
    Generates a personalized, detailed, recruiter-style reasoning text for the candidate.
    Crucial for Stage 4 manual review. Avoids generic templates by embedding specific details
    and acknowledging candidate gaps/concerns.
    """
    profile = cand.get("profile", {})
    skills = cand.get("skills", [])
    history = cand.get("career_history", [])
    signals = cand.get("redrob_signals", {})
    
    current_title = profile.get("current_title", "Software Engineer")
    current_company = profile.get("current_company", "Product Company")
    exp_years = cand_features.get("exp_years", 0.0)
    
    # Identify specific matched skills
    must_have_jd = parsed_jd.get("must_have_skills", [])
    preferred_jd = parsed_jd.get("preferred_skills", [])
    
    cand_skill_names = [s["name"].lower() for s in skills]
    
    matched_must = []
    for req in must_have_jd:
        if req in cand_skill_names:
            matched_must.append(req)
        else:
            # Check synonyms
            from ranker.skill_match import SKILL_EXPANSIONS
            expansions = SKILL_EXPANSIONS.get(req, [])
            for exp in expansions:
                if exp in cand_skill_names:
                    matched_must.append(exp)
                    break
                    
    matched_pref = []
    for req in preferred_jd:
        if req in cand_skill_names:
            matched_pref.append(req)
        else:
            # Check synonyms
            from ranker.skill_match import SKILL_EXPANSIONS
            expansions = SKILL_EXPANSIONS.get(req, [])
            for exp in expansions:
                if exp in cand_skill_names:
                    matched_pref.append(exp)
                    break
                    
    # Format matched lists (deduplicated)
    matched_must = sorted(list(set(matched_must)))
    matched_pref = sorted(list(set(matched_pref)))
    
    must_str = ", ".join(matched_must[:4]) if matched_must else "core Python development"
    pref_str = ", ".join(matched_pref[:3]) if matched_pref else "applied ML techniques"
    
    # Stability stats
    num_jobs = len(history)
    total_months = sum(job["duration_months"] for job in history)
    avg_tenure = total_months / max(1, num_jobs)
    
    # Choose intro phrasing based on rank to vary the tone
    if rank is not None:
        if rank <= 15:
            intro = f"Highly recommended top-tier candidate currently working as a {current_title} at {current_company} with {exp_years:.1f} years of total experience."
        elif rank <= 50:
            intro = f"Strong technical candidate currently working as a {current_title} at {current_company} with {exp_years:.1f} years of experience."
        else:
            intro = f"Qualified candidate currently working as a {current_title} at {current_company} with {exp_years:.1f} years of experience."
    else:
        intro = f"Candidate is currently working as a {current_title} at {current_company} with {exp_years:.1f} years of total professional experience."
        
    skill_fit = f"Demonstrates strong hands-on capabilities in required core areas like {must_str}."
    if matched_pref:
        skill_fit += f" Also brings specialized experience in preferred areas: {pref_str}."
        
    # Check for stability gap
    stability_parts = []
    if avg_tenure < 18.0:
        stability_parts.append(f"Note: average tenure of {avg_tenure:.1f} months is somewhat short, suggesting possible stability or retention risk.")
    else:
        stability_parts.append(f"Shows solid stability with {avg_tenure:.1f} months average tenure per job.")
        
    if cand_features.get("growth_score", 0.5) > 0.6:
        stability_parts.append("Exhibits a strong career progression path with progressive title advancements.")
    stability_growth = " ".join(stability_parts)
    
    # Check for experience gap
    exp_gap_str = ""
    min_exp = parsed_jd.get("min_experience", 4.0)
    if exp_years < min_exp:
        exp_gap_str = f"Though total experience ({exp_years:.1f} years) falls slightly below the preferred {min_exp:.1f}-year minimum, their skill match is strong."
        
    # Check for notice period gap
    avail_days = signals.get("notice_period_days", 30)
    if avail_days > 60:
        avail_str = f"Platform indicators note a longer notice period of {avail_days} days, which may require buy-out negotiation."
    else:
        avail_str = f"Platform indicators show active market presence with a {avail_days}-day notice period."
        
    # Combine everything intelligently
    parts = [intro, skill_fit]
    if exp_gap_str:
        parts.append(exp_gap_str)
    parts.append(stability_growth)
    parts.append(avail_str)
    
    reasoning = " ".join(parts)
    return reasoning
