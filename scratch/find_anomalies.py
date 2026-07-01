import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Scanning for anomalies in all 100,000 candidates...")

anomaly_counts = {
    "expert_zero_duration_skills": 0,
    "job_duration_date_mismatch": 0,
    "total_exp_vs_career_span_mismatch": 0,
    "education_duration_mismatch": 0,
    "intern_to_principal_fast": 0,
    "any_anomaly": 0
}

anomalous_candidates = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        has_anomaly = False
        reasons = []
        
        # 1. Expert skills with 0 duration
        expert_zero_dur = [s for s in c.get("skills", []) if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
        if len(expert_zero_dur) >= 10:
            anomaly_counts["expert_zero_duration_skills"] += 1
            has_anomaly = True
            reasons.append(f"expert_zero_duration_skills ({len(expert_zero_dur)})")
            
        # 2. Job duration vs start/end date mismatch
        job_mismatch = False
        for job in c.get("career_history", []):
            start = job.get("start_date")
            end = job.get("end_date")
            duration_months = job.get("duration_months", 0)
            if start:
                try:
                    s_dt = datetime.strptime(start, "%Y-%m-%d")
                    if end:
                        e_dt = datetime.strptime(end, "%Y-%m-%d")
                    else:
                        e_dt = datetime(2026, 7, 1) # Use current time from prompt metadata
                    
                    # Calculate actual months between start and end
                    actual_months = (e_dt.year - s_dt.year) * 12 + (e_dt.month - s_dt.month)
                    # If duration_months is significantly greater than actual months
                    if duration_months > actual_months + 3:
                        job_mismatch = True
                        reasons.append(f"job_duration_mismatch ({job['company']}: claimed {duration_months} months, date range allows {actual_months})")
                except Exception as e:
                    pass
        if job_mismatch:
            anomaly_counts["job_duration_date_mismatch"] += 1
            has_anomaly = True
            
        # 3. Total experience vs career span mismatch
        # e.g., years of experience is 10, but the entire history spans only 3 years
        years_of_experience = c.get("profile", {}).get("years_of_experience", 0)
        history = c.get("career_history", [])
        if history:
            start_dates = [job.get("start_date") for job in history if job.get("start_date")]
            if start_dates:
                try:
                    first_start = min(datetime.strptime(sd, "%Y-%m-%d") for sd in start_dates)
                    last_end_dates = [datetime.strptime(job.get("end_date"), "%Y-%m-%d") for job in history if job.get("end_date")]
                    last_end = max(last_end_dates) if last_end_dates else datetime(2026, 7, 1)
                    career_span_years = (last_end - first_start).days / 365.25
                    if years_of_experience > career_span_years + 1.5:
                        anomaly_counts["total_exp_vs_career_span_mismatch"] += 1
                        has_anomaly = True
                        reasons.append(f"total_exp_vs_career_span_mismatch (claims {years_of_experience} yrs, career span is {career_span_years:.1f} yrs)")
                except Exception as e:
                    pass
                    
        # 4. Education duration mismatch (e.g. B.Tech / B.E. / M.Sc finished in < 1 year or starts/ends in weird ways)
        # 5. Intern to Principal fast progression
        # e.g. Intern in 2024, Principal in 2025
        # Let's inspect some of the titles
        titles = [job.get("title", "").lower() for job in history]
        if len(titles) >= 2:
            # Check if they went from "intern" or "junior" to "principal" or "director" or "staff" in less than 2 years
            has_intern = any("intern" in t for t in titles)
            has_principal = any("principal" in t or "staff" in t or "director" in t for t in titles)
            if has_intern and has_principal:
                # Find dates of these roles
                intern_date = None
                principal_date = None
                for job in history:
                    t = job.get("title", "").lower()
                    sd = job.get("start_date")
                    if sd:
                        dt = datetime.strptime(sd, "%Y-%m-%d")
                        if "intern" in t:
                            intern_date = dt
                        if "principal" in t or "staff" in t or "director" in t:
                            principal_date = dt
                if intern_date and principal_date:
                    diff_years = abs((principal_date - intern_date).days) / 365.25
                    if diff_years < 2.0:
                        anomaly_counts["intern_to_principal_fast"] += 1
                        has_anomaly = True
                        reasons.append(f"intern_to_principal_fast (promoted in {diff_years:.1f} yrs)")

        if has_anomaly:
            anomaly_counts["any_anomaly"] += 1
            anomalous_candidates.append({
                "candidate_id": cid,
                "reasons": reasons
            })
            if len(anomalous_candidates) <= 20:
                print(f"Candidate {cid} is anomalous: {reasons}")

print(f"Anomaly counts: {anomaly_counts}")
print(f"Total anomalous candidates: {len(anomalous_candidates)}")
