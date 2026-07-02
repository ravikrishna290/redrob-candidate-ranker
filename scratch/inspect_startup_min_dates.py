import json

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

startups = [
    "Genpact AI", "Glance", "Rephrase.ai", "Aganitha", "Niramai", 
    "Saarthi.ai", "Sarvam AI", "Mad Street Den", "Observe.AI", 
    "Krutrim", "Wysa", "Haptik", "Verloop.io", "Yellow.ai", "Locobuzz"
]

earliest_years = {s: 9999 for s in startups}

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        for job in c.get("career_history", []):
            company = job.get("company")
            if company in earliest_years:
                start = job.get("start_date")
                if start:
                    try:
                        yr = int(start.split("-")[0])
                        if yr < earliest_years[company]:
                            earliest_years[company] = yr
                    except:
                        pass

print("Earliest start year found for each startup in dataset:")
for s, yr in sorted(earliest_years.items()):
    print(f"  {s}: {yr}")
