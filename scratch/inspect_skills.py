import json

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Finding expert skills with 0 duration...")
counts = {}
with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        # count expert skills with 0 duration
        zero_dur_expert = [s['name'] for s in c.get("skills", []) if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
        if len(zero_dur_expert) > 0:
            n = len(zero_dur_expert)
            counts[n] = counts.get(n, 0) + 1
            if n >= 5:
                print(f"Honeypot Candidate: {cid} has {n} expert skills with 0 duration: {zero_dur_expert[:5]}...")

print("Histogram of expert skills with 0 duration per candidate:")
for k, v in sorted(counts.items()):
    print(f"  {k} skills: {v} candidates")
