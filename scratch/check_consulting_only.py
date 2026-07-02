import json
import pandas as pd

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
ranking_path = r"d:\Redrob AI hackathon\redrob-ai\scratch\redrob_ranking_output.csv"

DISALLOWED = {
    "tcs", "tata consultancy services", "infosys", "wipro", "cognizant",
    "capgemini", "accenture", "hcl", "tech mahindra", "genpact", "mphasis"
}

def is_consulting_only(cand):
    history = cand.get("career_history", [])
    if not history:
        return False # No history at all is not consulting-only
    
    for job in history:
        company = job.get("company", "").lower()
        # Check if the company name contains any of the disallowed keywords
        if not any(dis in company for dis in DISALLOWED):
            return False # Found at least one non-consulting company
            
    return True

# Check all candidates in dataset
consulting_only_ids = set()
with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        if is_consulting_only(c):
            consulting_only_ids.add(c["candidate_id"])

print(f"Total candidates in dataset who only worked at consulting firms: {len(consulting_only_ids)}")

# Cross-reference with our top 100
df = pd.read_csv(ranking_path)
top_100_ids = df["candidate_id"].tolist()
matched = [cid for cid in top_100_ids if cid in consulting_only_ids]

print(f"Number of consulting-only candidates in our top 100: {len(matched)}")
if matched:
    print(f"Consulting-only candidates in top 100: {matched}")
