import pytest
from backend.app.engines.recommendation_engine import get_recommendations
from backend.app.engines.skill_gap_engine import analyze_skill_gap
from backend.app.engines.pathway_engine import analyze_pathway

def test_recommendation_engine_deterministic_output():
    profile = {
        "target_career": "Software Developer",
        "academic_stream": "Science",
        "skills": {
            "programming": 90,
            "logic": 85
        }
    }
    recs = get_recommendations(profile)
    assert isinstance(recs, list)
    if len(recs) > 0:
        assert 'occupation_id' in recs[0]
        assert 'final_score' in recs[0]
        assert recs[0]['status'] == 'RANKABLE'
        assert recs[0]['evidence_count'] >= 2

def test_skill_gap_engine():
    profile = {
        "skills": {
            "programming": 90,
            "mathematics": 45
        }
    }
    # OCC_0001 might be software developer in canonical data
    sg = analyze_skill_gap(profile, "OCC_0001")
    assert "strengths" in sg
    assert "gaps" in sg
    assert "unassessed_skills" in sg

def test_pathway_engine_unavailable_behavior():
    pw = analyze_pathway("UNKNOWN_OCCUPATION_ID")
    assert pw["status"] == "UNAVAILABLE"
