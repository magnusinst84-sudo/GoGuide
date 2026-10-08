from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_recommendations_endpoint():
    payload = {
        "academic_stream": "Science",
        "target_career": "Software Developer",
        "interests": {},
        "skills": {}
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("AVAILABLE", "UNAVAILABLE")
