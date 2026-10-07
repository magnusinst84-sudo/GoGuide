from app.engines.skill_gap_engine import analyze_skill_gap

def get_skill_gaps(profile: dict, occupation_id: str):
    return analyze_skill_gap(profile, occupation_id)