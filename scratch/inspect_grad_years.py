import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Finding candidates with experience exceeding years since graduation...")
grad_anomalies = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        edu = c.get("education", [])
        
        # Find the earliest end year of their first college degree (B.E./B.Tech/B.Sc/etc.)
        # Usually graduation is the end_year of their education
        end_years = [e.get("end_year") for e in edu if e.get("end_year")]
        if end_years:
            min_end_year = min(end_years)
            # If years of experience is greater than the years elapsed since graduation + 2 (some buffer for working before/during college)
            elapsed_years = 2026 - min_end_year
            if years_exp > elapsed_years + 3 and elapsed_years >= 0:
                grad_anomalies.append((cid, f"Years of experience: {years_exp}, graduated in {min_end_year} ({elapsed_years} years elapsed)"))

print(f"Total graduation anomalies: {len(grad_anomalies)}")
for item in grad_anomalies[:20]:
    print(item)
