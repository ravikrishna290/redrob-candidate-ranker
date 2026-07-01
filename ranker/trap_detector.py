from datetime import datetime

STARTUP_FOUNDING_YEARS = {
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

CURRENT_DATE = datetime(2026, 7, 1)

def detect_traps(cand):
    """
    Checks the candidate for all known honeypot patterns.
    Returns:
        is_trap (bool): True if candidate is a confirmed honeypot/trap
        reasons (list): List of matched trap explanations
    """
    reasons = []
    
    # 1. Job Duration vs Date Range Mismatch
    for job in cand.get("career_history", []):
        start = job.get("start_date")
        end = job.get("end_date")
        duration_months = job.get("duration_months", 0)
        if start:
            try:
                s_dt = datetime.strptime(start, "%Y-%m-%d")
                if end:
                    e_dt = datetime.strptime(end, "%Y-%m-%d")
                else:
                    e_dt = CURRENT_DATE
                actual_months = (e_dt.year - s_dt.year) * 12 + (e_dt.month - s_dt.month)
                # If claimed duration exceeds actual date range by a large margin
                if duration_months > actual_months + 6 and duration_months > actual_months * 1.5:
                    reasons.append(f"Job duration mismatch at {job['company']}: claimed {duration_months} months, date range permits max {actual_months} months.")
            except:
                pass
                
    # 2. Skills Inflation (Expert skills with 0 duration)
    expert_zero = [s['name'] for s in cand.get("skills", []) if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0]
    if len(expert_zero) >= 3:
        reasons.append(f"Skill inflation: Claimed 'expert' proficiency in {len(expert_zero)} skills (including {', '.join(expert_zero[:3])}) but has 0 duration of usage.")
        
    # 3. Startup Founding Year Anomaly
    for job in cand.get("career_history", []):
        company = job.get("company")
        start = job.get("start_date")
        if company in STARTUP_FOUNDING_YEARS and start:
            try:
                start_yr = int(start.split("-")[0])
                founding_yr = STARTUP_FOUNDING_YEARS[company]
                if start_yr < founding_yr:
                    reasons.append(f"Timeline impossibility: Started working at {company} in {start_yr}, but the company was founded in {founding_yr}.")
            except:
                pass
                
    # 4. Unrealistic Title Progression / Role-Title Mismatch
    # E.g. Intern in 2024 to Principal in 2025 (less than 1.5 years)
    history = cand.get("career_history", [])
    if len(history) >= 2:
        intern_date = None
        principal_date = None
        for job in history:
            t = job.get("title", "").lower()
            sd = job.get("start_date")
            if sd:
                try:
                    dt = datetime.strptime(sd, "%Y-%m-%d")
                    if "intern" in t:
                        intern_date = dt
                    if "principal" in t or "staff" in t or "director" in t:
                        principal_date = dt
                except:
                    pass
        if intern_date and principal_date:
            diff_years = abs((principal_date - intern_date).days) / 365.25
            if diff_years < 1.5:
                reasons.append(f"Timeline impossibility: Promoted from Intern to Principal in just {diff_years:.1f} years.")

    is_trap = len(reasons) > 0
    return is_trap, reasons
