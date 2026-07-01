import re
from datetime import datetime

CURRENT_DATE = datetime(2026, 7, 1)

# Title hierarchy mapping
TITLE_LEVELS = {
    "intern": 1, "trainee": 1, "junior": 2, "associate": 2,
    "engineer": 3, "developer": 3, "analyst": 3, "programmer": 3,
    "senior": 4, "lead": 4, "principal": 5, "staff": 5,
    "manager": 4, "director": 5, "vp": 5, "founder": 5, "co-founder": 5
}

CONSULTING_COMPANIES = {
    "tcs", "tata consultancy services", "infosys", "wipro", "cognizant",
    "capgemini", "accenture", "hcl", "tech mahindra", "genpact", "mphasis"
}

def get_title_level(title_normalized):
    title_normalized = title_normalized.lower()
    highest_level = 3  # Default to Mid/Engineer level
    if "intern" in title_normalized or "trainee" in title_normalized:
        return 1
    if "junior" in title_normalized or "associate" in title_normalized:
        return 2
    if "principal" in title_normalized or "staff" in title_normalized or "director" in title_normalized or "vp" in title_normalized:
        return 5
    if "senior" in title_normalized or "sr." in title_normalized or "lead" in title_normalized or "head" in title_normalized or "manager" in title_normalized:
        return 4
    return highest_level

def calculate_career_growth(career_history):
    if not career_history:
        return 0.5
    
    levels = [get_title_level(job["title"]) for job in career_history]
    # Reverse to go chronologically if stored from current to past
    levels_chronological = levels[::-1]
    
    if len(levels_chronological) <= 1:
        return 0.6 if levels_chronological and levels_chronological[0] >= 3 else 0.4
        
    # Check if there is progression (levels going up)
    growth_steps = 0
    total_steps = len(levels_chronological) - 1
    for i in range(total_steps):
        if levels_chronological[i+1] > levels_chronological[i]:
            growth_steps += 1
        elif levels_chronological[i+1] < levels_chronological[i]:
            growth_steps -= 0.5  # Demotion penalty
            
    normalized_growth = 0.5 + (growth_steps / max(1, total_steps)) * 0.5
    return min(1.0, max(0.0, normalized_growth))

def calculate_stability_score(career_history):
    if not career_history:
        return 0.5
        
    num_jobs = len(career_history)
    total_months = sum(job["duration_months"] for job in career_history)
    avg_duration_months = total_months / num_jobs
    
    # Target average duration of 24+ months (2 years) for a score of 1.0
    stability = min(1.0, avg_duration_months / 36.0)
    
    # Check for title-chaser penalty
    # Switching companies frequently (average duration < 18 months and >= 3 jobs)
    if avg_duration_months < 18.0 and num_jobs >= 3:
        stability *= 0.5
        
    return stability

def calculate_domain_relevance(cand):
    """
    Checks the candidate's experience and skills for relevance to AI/ML product roles.
    """
    score = 0.0
    
    # 1. Check skills
    skills = cand.get("skills", [])
    ai_skills_count = 0
    ai_keywords = [
        "machine learning", "deep learning", "nlp", "computer vision", 
        "embeddings", "vector", "search", "retrieval", "llm", "fine-tuning", 
        "lora", "qlora", "peft", "pytorch", "tensorflow", "scikit-learn", 
        "xgboost", "bge", "sentence-transformers", "faiss", "pinecone", 
        "qdrant", "weaviate", "milvus", "opensearch", "elasticsearch"
    ]
    
    for s in skills:
        name = s["name"].lower()
        if any(kw in name for kw in ai_keywords):
            # Weigh by proficiency
            prof = s["proficiency"]
            weight = 1.0 if prof == "expert" else 0.8 if prof == "advanced" else 0.5 if prof == "intermediate" else 0.2
            ai_skills_count += weight
            
    if ai_skills_count > 0:
        score += min(0.4, ai_skills_count * 0.1) # Max 0.4 from skills
        
    # 2. Check career history
    history = cand.get("career_history", [])
    ml_roles_months = 0
    product_roles_months = 0
    total_months = 0
    
    consulting_months = 0
    
    for job in history:
        title = job["title"].lower()
        desc = job["description"].lower()
        company = job["company"].lower()
        duration = job["duration_months"]
        total_months += duration
        
        # Check if consulting
        is_consulting = any(c in company for c in CONSULTING_COMPANIES)
        if is_consulting:
            consulting_months += duration
        else:
            product_roles_months += duration
            
        # Check if ML/AI role
        is_ml_role = any(kw in title for kw in ["ai", "machine learning", "ml", "data scientist", "nlp", "computer vision", "retrieval", "search", "recommendation"])
        # Check description for ML context
        has_ml_desc = any(kw in desc for kw in ai_keywords)
        
        if is_ml_role or has_ml_desc:
            ml_roles_months += duration
            
    if total_months > 0:
        ml_ratio = ml_roles_months / total_months
        score += min(0.4, ml_ratio * 0.5) # Max 0.4 from ML experience
        
        # Product company preference
        product_ratio = product_roles_months / total_months
        score += min(0.2, product_ratio * 0.2) # Max 0.2 from product experience
        
    return min(1.0, score)

def build_semantic_text(cand):
    """
    Builds a clean, dense text representation of the candidate profile for embedding.
    """
    profile = cand.get("profile", {})
    skills = cand.get("skills", [])
    history = cand.get("career_history", [])
    
    # Headline and summary
    text_parts = [
        f"Headline: {profile.get('headline', '')}",
        f"Summary: {profile.get('summary', '')}",
        f"Current Role: {profile.get('current_title', '')} at {profile.get('current_company', '')}"
    ]
    
    # Skills list
    skills_str = ", ".join([f"{s['name']} ({s['proficiency']})" for s in skills])
    text_parts.append(f"Skills: {skills_str}")
    
    # History overview
    history_parts = []
    for job in history[:3]: # Include top 3 jobs to stay within token limits
        history_parts.append(f"{job['title']} at {job['company']} ({job['duration_months']} months)")
    if history_parts:
        text_parts.append("Work History: " + " | ".join(history_parts))
        
    return " ".join(text_parts)

def extract_features(cand):
    """
    Extracts structured features and semantic profile text for a candidate.
    """
    profile = cand.get("profile", {})
    history = cand.get("career_history", [])
    signals = cand.get("redrob_signals", {})
    
    # Experience years
    total_months = sum(job["duration_months"] for job in history)
    exp_years = total_months / 12.0
    
    # Career growth
    growth_score = calculate_career_growth(history)
    
    # Stability
    stability_score = calculate_stability_score(history)
    
    # Domain relevance
    domain_relevance = calculate_domain_relevance(cand)
    
    # Behavioral score calculation
    behavioral_score = calculate_behavioral_score(signals)
    
    # Semantic text
    semantic_text = build_semantic_text(cand)
    
    return {
        "candidate_id": cand["candidate_id"],
        "exp_years": exp_years,
        "growth_score": growth_score,
        "stability_score": stability_score,
        "domain_relevance": domain_relevance,
        "behavioral_score": behavioral_score,
        "semantic_text": semantic_text
    }

def calculate_behavioral_score(signals):
    """
    Normalizes and pools the 23 behavioral signals into a single score.
    """
    score = 0.5 # Start at baseline
    
    # Profile completeness (0-100)
    completeness = signals.get("profile_completeness_score", 0)
    score += (completeness - 50) / 100 * 0.1 # +/- 0.05
    
    # Recruiter response rate (0-1)
    response_rate = signals.get("recruiter_response_rate", 0)
    score += (response_rate - 0.5) * 0.1 # +/- 0.05
    
    # Inactivity penalty: check last active date
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            la_dt = datetime.strptime(last_active, "%Y-%m-%d")
            days_inactive = (CURRENT_DATE - la_dt).days
            if days_inactive > 180: # 6 months
                score -= 0.15 # Inactive penalty
            elif days_inactive < 30: # 1 month
                score += 0.05 # Recently active bonus
        except:
            pass
            
    # GitHub activity score (-1 to 100)
    github = signals.get("github_activity_score", -1)
    if github > 0:
        score += (github / 100) * 0.10 # Up to +0.10 for active GitHub
        
    # Open to work flag
    if signals.get("open_to_work_flag", False):
        score += 0.05
        
    # Stated notice period (0-180 days)
    # Notice period <= 30 days is positive, notice period > 90 days is negative
    notice = signals.get("notice_period_days", 60)
    if notice <= 30:
        score += 0.05
    elif notice > 90:
        score -= 0.05
        
    # Interview completion rate (0-1)
    interview_rate = signals.get("interview_completion_rate", 1.0)
    score += (interview_rate - 0.7) * 0.05 # +/- 0.02
    
    # Verification checks
    if signals.get("verified_email", False):
        score += 0.01
    if signals.get("verified_phone", False):
        score += 0.01
    if signals.get("linkedin_connected", False):
        score += 0.01
        
    return min(1.0, max(0.0, score))
