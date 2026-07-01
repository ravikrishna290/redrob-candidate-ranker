import json

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

print("Checking startup dates...")
anomalous_startups = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        for job in c.get("career_history", []):
            company = job.get("company")
            start = job.get("start_date")
            if company in startup_founding_years and start:
                try:
                    start_yr = int(start.split("-")[0])
                    founding_yr = startup_founding_years[company]
                    if start_yr < founding_yr:
                        anomalous_startups.append((cid, company, start_yr, founding_yr))
                except Exception as e:
                    pass

print(f"Total startup founding year anomalies: {len(anomalous_startups)}")
for item in anomalous_startups[:20]:
    print(item)
