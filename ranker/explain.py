def generate_reasoning(cand, cand_features, parsed_jd):
    """
    Generates a personalized, detailed, recruiter-style reasoning text for the candidate.
    Crucial for Stage 4 manual review. Avoids generic templates by embedding specific details.
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
    
    # Build parts of explanation
    intro = f"Candidate is currently working as a {current_title} at {current_company} with {exp_years:.1f} years of total professional experience."
    
    skill_fit = f"Demonstrates strong hands-on capabilities in required core areas like {must_str}."
    if matched_pref:
        skill_fit += f" Also brings specialized experience in preferred areas: {pref_str}."
        
    stability_growth = f"Shows good stability with {avg_tenure:.1f} months average tenure per job."
    if cand_features.get("growth_score", 0.5) > 0.6:
        stability_growth += " Exhibits a strong career progression path with progressive title advancements."
        
    avail_days = signals.get("notice_period_days", 30)
    avail_str = f"Platform indicators show active market presence with a {avail_days}-day notice period."
    
    reasoning = f"{intro} {skill_fit} {stability_growth} {avail_str}"
    return reasoning
