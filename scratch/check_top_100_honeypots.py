import json
import pandas as pd

# Load honeypots list
honeypots_path = r"d:\Redrob AI hackathon\redrob-ai\scratch\honeypots.json"
with open(honeypots_path, "r", encoding="utf-8") as f:
    honeypots = set(json.load(f))

# Load our top 100 ranking
ranking_path = r"d:\Redrob AI hackathon\redrob-ai\scratch\redrob_ranking_output.csv"
df = pd.read_csv(ranking_path)

top_100_ids = df["candidate_id"].tolist()

matched_honeypots = [cid for cid in top_100_ids if cid in honeypots]

print(f"Top 100 Candidates checked: {len(top_100_ids)}")
print(f"Number of honeypots in top 100: {len(matched_honeypots)}")
if matched_honeypots:
    print(f"Honeypots found: {matched_honeypots}")
else:
    print("Zero honeypots found in the top 100! Excellent.")
