import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Analyzing skills and career history...")
with open(candidates_path, "r", encoding="utf-8") as f:
    for i in range(100):
        line = f.readline()
        if not line:
            break
        c = json.loads(line)
        
        # Look at skills with expert proficiency
        expert_skills = [s for s in c.get("skills", []) if s.get("proficiency") == "expert"]
        expert_zero_dur = [s for s in expert_skills if s.get("duration_months", 0) == 0]
        
        # Look at career history dates
        for job in c.get("career_history", []):
            start = job.get("start_date")
            end = job.get("end_date")
            duration_months = job.get("duration_months", 0)
            # check start date year
            if start:
                start_yr = int(start.split("-")[0])
                if start_yr < 1980 or start_yr > 2026:
                    print(f"Candidate {c['candidate_id']} has weird start year: {start_yr}")
            if end:
                end_yr = int(end.split("-")[0])
                if end_yr < 1980 or end_yr > 2026:
                    print(f"Candidate {c['candidate_id']} has weird end year: {end_yr}")

        if len(expert_zero_dur) > 0:
            print(f"Candidate {c['candidate_id']} has {len(expert_skills)} expert skills, of which {len(expert_zero_dur)} have 0 duration")
            print([s['name'] for s in expert_zero_dur])
