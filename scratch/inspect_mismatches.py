import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Finding job duration date mismatches...")
with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
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
                        e_dt = datetime(2026, 7, 1)
                    
                    actual_months = (e_dt.year - s_dt.year) * 12 + (e_dt.month - s_dt.month)
                    # If claimed duration is way larger than actual months
                    if duration_months > actual_months + 3:
                        print(f"Honeypot Candidate: {cid} | Job: {job['company']} | Claimed: {duration_months} mos, date range: {start} to {end or 'current'} ({actual_months} mos)")
                except:
                    pass
