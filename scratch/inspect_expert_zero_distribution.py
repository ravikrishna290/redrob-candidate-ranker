import json
from collections import Counter

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

counts = []

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        expert_zero = [s for s in c.get("skills", []) if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
        counts.append(len(expert_zero))

dist = Counter(counts)
print("Distribution of expert skills with 0 duration:")
for count, freq in sorted(dist.items()):
    print(f"  {count} skills: {freq} candidates")
