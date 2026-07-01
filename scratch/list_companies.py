import json

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Listing companies...")
companies = {}
with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        for job in c.get("career_history", []):
            company = job.get("company")
            industry = job.get("industry")
            size = job.get("company_size")
            if company not in companies:
                companies[company] = {"count": 0, "sizes": set(), "industries": set()}
            companies[company]["count"] += 1
            if size:
                companies[company]["sizes"].add(size)
            if industry:
                companies[company]["industries"].add(industry)

print("Unique companies and their counts:")
for name, info in sorted(companies.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"  {name}: {info['count']} times | sizes: {list(info['sizes'])} | industries: {list(info['industries'])}")
