import json
import os
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Scanning candidates...")
count = 0
examples = []
honeypot_candidates = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        count += 1
        
        # Simple detector for "expert in 10 skills with 0 years used"
        expert_zero_yrs = 0
        for s in c.get("skills", []):
            if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0:
                expert_zero_yrs += 1
                
        # Simple detector for impossible company dates
        # Check start/end dates in career history vs company age or duration
        date_impossible = False
        for job in c.get("career_history", []):
            start = job.get("start_date")
            end = job.get("end_date")
            duration_months = job.get("duration_months", 0)
            if start and end:
                try:
                    s_dt = datetime.strptime(start, "%Y-%m-%d")
                    e_dt = datetime.strptime(end, "%Y-%m-%d")
                    calc_months = (e_dt.year - s_dt.year) * 12 + (e_dt.month - s_dt.month)
                    if abs(calc_months - duration_months) > 2:
                        date_impossible = True
                except:
                    pass
            # Unrealistic experience years vs date difference
            
        # Unrealistic title progression
        unrealistic_progression = False
        # If there are titles like Principal or Staff with very low total experience or short duration
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        
        if expert_zero_yrs >= 10 or date_impossible:
            honeypot_candidates.append((c["candidate_id"], expert_zero_yrs, date_impossible))
            if len(honeypot_candidates) < 10:
                print(f"Honeypot candidate: {c['candidate_id']} | expert_zero_yrs: {expert_zero_yrs} | date_impossible: {date_impossible}")

        if count < 3:
            examples.append(c)

print(f"Total candidates: {count}")
print(f"Found {len(honeypot_candidates)} potential honeypots using simple heuristics.")
