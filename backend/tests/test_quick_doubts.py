import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@patch("app.services.quick_doubts_service.os.getenv")
@patch("app.services.quick_doubts_service.httpx.AsyncClient.post")
def test_valid_request(mock_post, mock_getenv):
    mock_getenv.side_effect = lambda k, d=None: "fake_key" if k == "GEMINI_API_KEY" else ("gemini-3.5-flash-lite" if k == "GEMINI_MODEL" else d)
    
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "AI is artificial intelligence."}]}}]
    }
    mock_post.return_value = mock_response

    response = client.post("/api/quick-doubts", json={"message": "What is AI?"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "AVAILABLE"
    assert data["answer"] == "AI is artificial intelligence."
    assert "message" not in data or data["message"] is None

def test_empty_message_rejected():
    response = client.post("/api/quick-doubts", json={"message": ""})
    assert response.status_code == 422
    
    response2 = client.post("/api/quick-doubts", json={"message": "   "})
    assert response2.status_code == 422

def test_overly_long_message_rejected():
    response = client.post("/api/quick-doubts", json={"message": "a" * 2001})
    assert response.status_code == 422

@patch("app.services.quick_doubts_service.os.getenv")
def test_missing_api_key(mock_getenv):
    mock_getenv.return_value = None
    response = client.post("/api/quick-doubts", json={"message": "What is AI?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ERROR"
    assert "temporarily unavailable" in data["message"]

@patch("app.services.quick_doubts_service.os.getenv")
@patch("app.services.quick_doubts_service.httpx.AsyncClient.post")
def test_gemini_failure(mock_post, mock_getenv):
    mock_getenv.side_effect = lambda k, d=None: "fake_key" if k == "GEMINI_API_KEY" else ("gemini-3.5-flash-lite" if k == "GEMINI_MODEL" else d)
    
    import httpx
    mock_post.side_effect = httpx.TimeoutException("Timeout")

    response = client.post("/api/quick-doubts", json={"message": "What is AI?"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ERROR"
    assert "temporarily unavailable" in data["message"]
