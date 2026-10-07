"""
test_llm.py – Tests for /api/llm/chat, factory, prompts, and LLM service.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.llm.factory import get_llm_provider
from app.llm.providers.local import LocalProvider
from app.llm.prompts import construct_prompt
from app.schemas.llm import LLMContext, Evidence

client = TestClient(app)


def test_llm_provider_factory_returns_local():
    os.environ["LLM_PROVIDER"] = "local"
    provider = get_llm_provider()
    assert isinstance(provider, LocalProvider)
    assert provider.health()["status"] == "ok"


def test_llm_provider_factory_raises_on_unknown():
    os.environ["LLM_PROVIDER"] = "nonexistent_provider"
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        get_llm_provider()
    os.environ["LLM_PROVIDER"] = "local"


def test_local_provider_model_name_reflects_env():
    os.environ["LLM_MODEL"] = "Qwen/Qwen3-4B-Instruct-2507"
    p = LocalProvider()
    assert p.model_name() == "Qwen/Qwen3-4B-Instruct-2507"
    del os.environ["LLM_MODEL"]


def test_local_provider_model_name_default_when_unset():
    os.environ.pop("LLM_MODEL", None)
    p = LocalProvider()
    # Returns a non-empty string even when unconfigured
    assert isinstance(p.model_name(), str)


def test_local_provider_generate_raises_without_model():
    os.environ.pop("LLM_MODEL", None)
    p = LocalProvider()
    with pytest.raises(RuntimeError, match="LLM_MODEL environment variable is not set"):
        p.generate("test prompt")


def test_prompt_contains_grounding():
    context = LLMContext(user_profile={"aptitude": 85.5})
    prompt = construct_prompt("Help me choose a career.", context)

    assert "CRITICAL RULES" in prompt
    assert "never invent scholarships, colleges, fees, salaries" in prompt.lower()
    assert "85.5" in prompt
    assert "Help me choose a career." in prompt


def test_llm_chat_endpoint_success():
    """Mocked /api/llm/chat – provider is patched so no weights needed."""
    with patch("app.services.llm_service.get_llm_provider") as mock_factory:
        mock_prov = MagicMock()
        mock_prov.generate.return_value = "Mock LLM response text"
        mock_prov.model_name.return_value = "mock-model"
        mock_factory.return_value = mock_prov

        payload = {
            "prompt": "What are my options?",
            "context": {
                "user_profile": {"interests": ["tech"]},
                "user_message": "What are my options?",
                "deterministic_results": {"is_feasible": True},
                "retrieved_documents": [],
                "constraints": {},
                "provenance": [{"source": "system", "value": "test"}],
            },
        }
        response = client.post("/api/llm/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response_text"] == "Mock LLM response text"
    assert data["model"] == "mock-model"
    assert "generated_at" in data


def test_llm_chat_endpoint_validation_error():
    # Missing 'prompt'
    payload = {"context": {"user_profile": {}}}
    response = client.post("/api/llm/chat", json=payload)
    assert response.status_code == 422
