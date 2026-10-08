from app.engines.recommendation_engine import get_recommendations

def generate_recommendations(profile: dict):
    return get_recommendations(profile)