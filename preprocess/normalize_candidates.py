import re
from datetime import datetime

CURRENT_DATE = datetime(2026, 7, 1)

def parse_date(date_str, default_date=CURRENT_DATE):
    if not date_str:
        return default_date
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except:
        return default_date

def normalize_title(title):
    if not title:
        return ""
    # Lowercase and clean spaces
    title = title.lower().strip()
    # Normalize common variations
    title = re.sub(r'\s+', ' ', title)
    return title

def normalize_skill_name(skill_name):
    if not skill_name:
        return ""
    # Lowercase and clean spaces
    skill_name = skill_name.lower().strip()
    # Normalize common variations
    if skill_name in ["ml", "machinelearning"]:
        return "machine learning"
    if skill_name in ["dl", "deeplearning"]:
        return "deep learning"
    if skill_name in ["nlp", "naturallanguageprocessing"]:
        return "nlp"
    if skill_name in ["cv", "computervision"]:
        return "computer vision"
    return skill_name

def normalize_candidate(cand):
    """
    Normalizes candidate fields for downstream processing.
    """
    normalized = {}
    
    # Copy basic attributes
    normalized["candidate_id"] = cand.get("candidate_id", "")
    
    # Profile normalization
    profile = cand.get("profile", {})
    normalized_profile = {
        "anonymized_name": profile.get("anonymized_name", ""),
        "headline": profile.get("headline", "").strip(),
        "summary": profile.get("summary", "").strip(),
        "location": profile.get("location", "").strip(),
        "country": profile.get("country", "").strip(),
        "years_of_experience": float(profile.get("years_of_experience", 0)),
        "current_title": normalize_title(profile.get("current_title", "")),
        "current_company": profile.get("current_company", "").strip(),
        "current_company_size": profile.get("current_company_size", ""),
        "current_industry": profile.get("current_industry", "")
    }
    normalized["profile"] = normalized_profile
    
    # Career history normalization
    career_history = cand.get("career_history", [])
    normalized_history = []
    for job in career_history:
        start_date_str = job.get("start_date")
        end_date_str = job.get("end_date")
        is_current = job.get("is_current", False)
        
        start_dt = parse_date(start_date_str)
        end_dt = parse_date(end_date_str, CURRENT_DATE if is_current else None)
        if end_dt is None:
            # If not current and end date is missing, default to start date + duration
            duration = job.get("duration_months", 0)
            from datetime import timedelta
            end_dt = start_dt + timedelta(days=duration * 30.4)
            
        normalized_job = {
            "company": job.get("company", "").strip(),
            "title": normalize_title(job.get("title", "")),
            "start_date": start_date_str,
            "end_date": end_date_str,
            "duration_months": int(job.get("duration_months", 0)),
            "is_current": bool(is_current),
            "industry": job.get("industry", ""),
            "company_size": job.get("company_size", ""),
            "description": job.get("description", "").strip(),
            "parsed_start_dt": start_dt,
            "parsed_end_dt": end_dt
        }
        normalized_history.append(normalized_job)
    normalized["career_history"] = normalized_history
    
    # Skills normalization
    skills = cand.get("skills", [])
    normalized_skills = []
    for s in skills:
        normalized_skill = {
            "name": normalize_skill_name(s.get("name", "")),
            "proficiency": s.get("proficiency", "beginner").lower().strip(),
            "endorsements": int(s.get("endorsements", 0)),
            "duration_months": int(s.get("duration_months", 0))
        }
        normalized_skills.append(normalized_skill)
    normalized["skills"] = normalized_skills
    
    # Education normalization
    education = cand.get("education", [])
    normalized_edu = []
    for edu_item in education:
        normalized_item = {
            "institution": edu_item.get("institution", "").strip(),
            "degree": edu_item.get("degree", "").strip(),
            "field_of_study": edu_item.get("field_of_study", "").strip(),
            "start_year": int(edu_item.get("start_year", 0)) if edu_item.get("start_year") else None,
            "end_year": int(edu_item.get("end_year", 0)) if edu_item.get("end_year") else None,
            "grade": edu_item.get("grade", ""),
            "tier": edu_item.get("tier", "unknown")
        }
        normalized_edu.append(normalized_item)
    normalized["education"] = normalized_edu
    
    # Redrob signals normalization
    signals = cand.get("redrob_signals", {})
    normalized_signals = {
        "profile_completeness_score": float(signals.get("profile_completeness_score", 0)),
        "signup_date": signals.get("signup_date"),
        "last_active_date": signals.get("last_active_date"),
        "open_to_work_flag": bool(signals.get("open_to_work_flag", False)),
        "profile_views_received_30d": int(signals.get("profile_views_received_30d", 0)),
        "applications_submitted_30d": int(signals.get("applications_submitted_30d", 0)),
        "recruiter_response_rate": float(signals.get("recruiter_response_rate", 0)),
        "avg_response_time_hours": float(signals.get("avg_response_time_hours", 0)),
        "skill_assessment_scores": {normalize_skill_name(k): float(v) for k, v in signals.get("skill_assessment_scores", {}).items()},
        "connection_count": int(signals.get("connection_count", 0)),
        "endorsements_received": int(signals.get("endorsements_received", 0)),
        "notice_period_days": int(signals.get("notice_period_days", 0)),
        "expected_salary_range_inr_lpa": {
            "min": float(signals.get("expected_salary_range_inr_lpa", {}).get("min", 0)),
            "max": float(signals.get("expected_salary_range_inr_lpa", {}).get("max", 0))
        },
        "preferred_work_mode": signals.get("preferred_work_mode", "flexible"),
        "willing_to_relocate": bool(signals.get("willing_to_relocate", False)),
        "github_activity_score": float(signals.get("github_activity_score", -1)),
        "search_appearance_30d": int(signals.get("search_appearance_30d", 0)),
        "saved_by_recruiters_30d": int(signals.get("saved_by_recruiters_30d", 0)),
        "interview_completion_rate": float(signals.get("interview_completion_rate", 0)),
        "offer_acceptance_rate": float(signals.get("offer_acceptance_rate", -1)),
        "verified_email": bool(signals.get("verified_email", False)),
        "verified_phone": bool(signals.get("verified_phone", False)),
        "linkedin_connected": bool(signals.get("linkedin_connected", False))
    }
    normalized["redrob_signals"] = normalized_signals
    
    return normalized
