from app.engines.pathway_engine import analyze_pathway

def get_education_pathway(career_id: str):
    return analyze_pathway(career_id)