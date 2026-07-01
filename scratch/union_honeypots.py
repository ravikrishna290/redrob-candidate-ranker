import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

startup_founding_years = {
    "Sarvam AI": 2023,
    "Krutrim": 2023,
    "Rephrase.ai": 2019,
    "Glance": 2019,
    "Aganitha": 2017,
    "Niramai": 2016,
    "Saarthi.ai": 2017,
    "Mad Street Den": 2013,
    "Observe.AI": 2017,
    "Wysa": 2015,
    "Haptik": 2012,
    "Verloop.io": 2015,
    "Yellow.ai": 2016,
    "Locobuzz": 2015,
    "Genpact AI": 2022
}

honeypots = {}

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        reasons = []
        
        # 1. Job Duration vs Date Range Mismatch
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
                    if duration_months > actual_months + 6 and duration_months > actual_months * 1.5:
                        reasons.append(f"job_duration_mismatch ({job['company']}: claimed {duration_months} mos, actual max {actual_months})")
                except:
                    pass
                    
        # 2. Skills Inflation (Expert skills with 0 duration)
        expert_zero = [s['name'] for s in c.get("skills", []) if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
        if len(expert_zero) >= 3:
            reasons.append(f"skills_inflation ({len(expert_zero)} expert skills with 0 duration)")
            
        # 3. Startup Founding Year Anomaly
        for job in c.get("career_history", []):
            company = job.get("company")
            start = job.get("start_date")
            if company in startup_founding_years and start:
                try:
                    start_yr = int(start.split("-")[0])
                    founding_yr = startup_founding_years[company]
                    if start_yr < founding_yr:
                        reasons.append(f"startup_founding_year_anomaly ({company} started in {start_yr}, founded in {founding_yr})")
                except:
                    pass
                    
        if reasons:
            honeypots[cid] = reasons

print(f"Total unique honeypot candidates found: {len(honeypots)}")
# Print some stats
reason_counts = {}
for cid, r_list in honeypots.items():
    for r in r_list:
        name = r.split("(")[0].strip()
        reason_counts[name] = reason_counts.get(name, 0) + 1
        
print("Honeypot count by reason class:")
for k, v in reason_counts.items():
    print(f"  {k}: {v}")

# Save all honeypot candidate IDs to a file for our ranking pipeline to reference or penalize
import pickle
out_path = r"C:\Users\USER\.gemini\antigravity\brain\f6d152af-6f94-40e4-be41-05c6c66e22cb\scratch\honeypots.json"
with open(out_path, "w", encoding="utf-8") as out:
    json.dump(list(honeypots.keys()), out)
print(f"Saved {len(honeypots)} honeypot candidate IDs to {out_path}")
