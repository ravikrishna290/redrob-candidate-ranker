import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
CURRENT_DATE = datetime(2026, 7, 1)

anomalies = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        # 1. Job start date > job end date
        for job in c.get("career_history", []):
            start = job.get("start_date")
            end = job.get("end_date")
            if start and end:
                try:
                    s_dt = datetime.strptime(start, "%Y-%m-%d")
                    e_dt = datetime.strptime(end, "%Y-%m-%d")
                    if s_dt > e_dt:
                        anomalies.append((cid, "job_start_after_end", f"{start} to {end}"))
                except:
                    pass
            
            # 2. Start date in the future
            if start:
                try:
                    s_dt = datetime.strptime(start, "%Y-%m-%d")
                    if s_dt > CURRENT_DATE:
                        anomalies.append((cid, "job_starts_in_future", start))
                except:
                    pass
                    
        # 3. Education start > end year
        for edu in c.get("education", []):
            sy = edu.get("start_year")
            ey = edu.get("end_year")
            if sy and ey and sy > ey:
                anomalies.append((cid, "education_start_after_end", f"{sy} to {ey}"))
                
print(f"Total timeline anomalies found: {len(anomalies)}")
for a in anomalies[:20]:
    print(a)
