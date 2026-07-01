import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Scanning for timeline contradictions...")
timeline_anomalies = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        history = c.get("career_history", [])
        
        # Calculate sum of job durations in years
        sum_job_dur_years = sum(job.get("duration_months", 0) for job in history) / 12.0
        
        # Check if they have a large discrepancy in experience
        # e.g., years of experience is 10 but job history total is 1 year
        if years_exp > sum_job_dur_years + 5 and sum_job_dur_years < 2.0:
            timeline_anomalies.append((cid, f"Claimed {years_exp} yrs, but history total is only {sum_job_dur_years:.1f} yrs"))
            
        # Check if they have a job that started before they were born? We don't have birth date.
        # But we have education start years. Let's check if they have a job that started more than 6 years before their first degree ended.
        edu = c.get("education", [])
        if edu and history:
            min_edu_start = min(e.get("start_year", 9999) for e in edu if e.get("start_year"))
            min_edu_end = min(e.get("end_year", 9999) for e in edu if e.get("end_year"))
            
            # Find any job that started before min_edu_start - 4 years (e.g. before college) and has a professional title
            for job in history:
                start = job.get("start_date")
                title = job.get("title", "").lower()
                if start:
                    try:
                        start_yr = int(start.split("-")[0])
                        # If they worked as a Senior/Lead/Engineer when they were under 18 (assuming college starts at 18, so start_yr < min_edu_start - 2)
                        if min_edu_start != 9999 and start_yr < min_edu_start - 3:
                            if any(x in title for x in ["engineer", "developer", "manager", "senior", "lead", "principal"]):
                                timeline_anomalies.append((cid, f"Job '{job['title']}' in {start_yr} started before college in {min_edu_start}"))
                    except:
                        pass

print(f"Total timeline anomalies found: {len(timeline_anomalies)}")
for item in timeline_anomalies[:20]:
    print(item)
