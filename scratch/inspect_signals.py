import json
from datetime import datetime

candidates_path = r"d:\Redrob AI hackathon\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Checking behavioral signals...")
inactive_count = 0
low_response_count = 0
both_count = 0
total = 0

current_date = datetime(2026, 7, 1)

with open(candidates_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        total += 1
        
        signals = c.get("redrob_signals", {})
        last_active = signals.get("last_active_date")
        response_rate = signals.get("recruiter_response_rate", 1.0)
        
        is_inactive = False
        if last_active:
            try:
                la_dt = datetime.strptime(last_active, "%Y-%m-%d")
                days_inactive = (current_date - la_dt).days
                if days_inactive > 180: # 6 months
                    is_inactive = True
            except:
                pass
                
        is_low_response = response_rate <= 0.10
        
        if is_inactive:
            inactive_count += 1
        if is_low_response:
            low_response_count += 1
        if is_inactive and is_low_response:
            both_count += 1

print(f"Total: {total}")
print(f"Inactive > 6 months: {inactive_count} ({inactive_count/total*100:.1f}%)")
print(f"Low response rate <= 10%: {low_response_count} ({low_response_count/total*100:.1f}%)")
print(f"Both inactive and low response: {both_count} ({both_count/total*100:.1f}%)")
