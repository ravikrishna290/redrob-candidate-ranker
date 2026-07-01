import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Finding all potential honeypots...")
honeypots = set()

# We'll check each rule and collect candidate IDs
rules_counts = {
    "date_mismatch": 0,
    "skills_inflation": 0,
    "progression_impossibility": 0,
}

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        # Rule A: Date Mismatch in jobs
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
                        e_dt = datetime(2026, 7, 1)
                    actual_months = (e_dt.year - s_dt.year) * 12 + (e_dt.month - s_dt.month)
                    # Claimed duration > 2x actual duration and difference is > 12 months
                    if duration_months > actual_months + 6 and duration_months > actual_months * 1.5:
                        job_mismatch = True
                except:
                    pass
        if job_mismatch:
            rules_counts["date_mismatch"] += 1
            honeypots.add(cid)
            
        # Rule B: Skill Inflation (Expert/Advanced skills with 0 duration)
        # Check if the candidate has expert skills with 0 duration, or advanced skills with 0 duration
        expert_zero = [s for s in c.get("skills", []) if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
        advanced_zero = [s for s in c.get("skills", []) if s.get("proficiency") == "advanced" and s.get("duration_months", 0) == 0]
        if len(expert_zero) >= 3 or (len(expert_zero) + len(advanced_zero)) >= 6:
            rules_counts["skills_inflation"] += 1
            honeypots.add(cid)
            
        # Rule C: Impossible Timeline Progression
        # e.g., total experience < 1 year but they have senior or principal title, or progression from intern to principal is extremely fast
        # Let's inspect if any candidate has years_of_experience < 1.0 but their current title or past title is "Principal", "Director", "Lead", "Senior"
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        history = c.get("career_history", [])
        for job in history:
            title = job.get("title", "").lower()
            if years_exp < 1.5:
                if any(x in title for x in ["principal", "lead", "director", "architect", "senior"]):
                    # Wait, is this a honeypot? Yes! A Principal with 1 year of total experience is a honeypot.
                    rules_counts["progression_impossibility"] += 1
                    honeypots.add(cid)
                    break

print(f"Total honeypots found: {len(honeypots)}")
print(f"Counts by rule: {rules_counts}")
print(f"Sample honeypots: {list(honeypots)[:20]}")
