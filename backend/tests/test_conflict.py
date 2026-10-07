from app.engines.conflict_engine import preference_alignment

def test_preference_alignment():
    # Identical vectors should have 0 conflict (cos_sim=1, 1-1=0)
    assert abs(preference_alignment([1, 0, 0], [1, 0, 0]) - 0.0) < 1e-6
    # Orthogonal vectors should have 1 conflict (cos_sim=0, 1-0=1)
    assert abs(preference_alignment([1, 0, 0], [0, 1, 0]) - 1.0) < 1e-6
