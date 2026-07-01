import json

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Finding candidates with many skills having 0 duration...")
counts = {}
with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c["candidate_id"]
        
        # count skills with 0 duration (any proficiency)
        zero_dur = [s['name'] for s in c.get("skills", []) if s.get("duration_months", 0) == 0]
        if len(zero_dur) > 0:
            n = len(zero_dur)
            counts[n] = counts.get(n, 0) + 1
            if n >= 8:
                print(f"Candidate: {cid} has {n} skills with 0 duration: {zero_dur[:8]}...")

print("Histogram of skills with 0 duration per candidate:")
for k, v in sorted(counts.items()):
    print(f"  {k} skills: {v} candidates")
