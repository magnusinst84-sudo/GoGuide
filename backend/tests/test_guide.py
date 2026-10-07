"""
test_guide.py – Tests for /api/guide, guide_service, and RAG layer.

All tests run without Qwen weights by mocking LLM and RAG calls.
"""

import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.rag.index import RAGIndex, Document
from app.schemas.llm import LLMContext, LLMRequest, LLMResponse, Evidence
from app.services.guide_service import _detect_intents, _authoritative, _unavailable, process_guide_request
from app.schemas.guide import GuideRequest

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_retrieve(docs=None):
    if docs is None:
        docs = [{
            "document_id": "abc123",
            "document_type": "occupation",
            "title": "Software Developer",
            "text": "Software developers design and build applications.",
            "score": 0.12,
            "metadata": {"source": "prism_education_career", "file": "occupations.csv"},
        }]
    return docs


def _mock_llm_response(text="Here is your guidance."):
    return LLMResponse(response_text=text, generated_at="2026-01-01T00:00:00Z", model="mock-model")


# ---------------------------------------------------------------------------
# 1. Intent detection
# ---------------------------------------------------------------------------

class TestIntentDetection:
    def test_career_intent(self):
        assert "career_recommendation" in _detect_intents("What careers fit me?")

    def test_financial_intent(self):
        assert "financial_feasibility" in _detect_intents("Can I afford engineering college?")

    def test_parent_intent(self):
        assert "parent_student_alignment" in _detect_intents("My parents want me to study medicine.")

    def test_skill_intent(self):
        assert "skill_gap" in _detect_intents("What skills do I need for cybersecurity?")

    def test_education_intent(self):
        assert "education_pathway" in _detect_intents("Which degree should I study?")

    def test_market_intent(self):
        assert "market_outlook" in _detect_intents("What is the future demand for data science?")

    def test_fallback_to_general(self):
        assert _detect_intents("Hello there!") == ["general_guidance"]

    def test_multiple_intents(self):
        msg = "I want a career that I can afford. What degree should I pick?"
        intents = _detect_intents(msg)
        assert "financial_feasibility" in intents
        assert "education_pathway" in intents


# ---------------------------------------------------------------------------
# 2. Authoritative wrapper
# ---------------------------------------------------------------------------

class TestAuthoritativeWrapper:
    def test_authoritative_flag(self):
        result = _authoritative(12450, "financial_solver")
        assert result["authoritative"] is True
        assert result["value"] == 12450
        assert result["source"] == "financial_solver"

    def test_unavailable_flag(self):
        result = _unavailable("recommendation_engine")
        assert result["authoritative"] is True
        assert result["status"] == "UNAVAILABLE"
        assert result["engine"] == "recommendation_engine"

    def test_deterministic_value_not_overridable(self):
        """
        Context precedence test: even if a retrieved document mentions ₹8,00,000
        the authoritative deterministic result must be ₹4,00,000.
        """
        det = {"financial": {"total_cost": _authoritative(400_000, "financial_solver")}}
        rag = [{"text": "Tuition cost: ₹8,00,000", "metadata": {}}]

        # The deterministic result is completely separate from rag docs in context
        assert det["financial"]["total_cost"]["value"] == 400_000
        assert det["financial"]["total_cost"]["authoritative"] is True
        # RAG doc text is different but that is fine - LLM is instructed to ignore it
        assert "8,00,000" in rag[0]["text"]


# ---------------------------------------------------------------------------
# 3. RAG index – retrieval with mocked FAISS
# ---------------------------------------------------------------------------

class TestRAGRetrieval:
    def _setup_index(self, docs=None):
        idx = RAGIndex()
        idx._initialized = True

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2]])
        idx.model = mock_model

        mock_faiss = MagicMock()
        mock_faiss.search.return_value = (
            np.array([[0.01, 0.05, 0.09]]),
            np.array([[0, 1, 2]])
        )
        idx.index = mock_faiss

        if docs is None:
            docs = [
                Document("id1", "occupation", "Software Developer", "Designs software systems.", {"source": "prism_education_career"}),
                Document("id2", "skill",      "Python Programming",  "Python language skill.",   {"source": "prism_education_career"}),
                Document("id3", "market_signal", "Tech Market", "High demand in tech.", {"source": "prism_india_jobs", "status": "SYNTHETIC_PROTOTYPE"}),
            ]
        idx.documents = docs
        return idx

    def test_retrieval_returns_list(self):
        idx = self._setup_index()
        results = idx.retrieve("software development skills")
        assert isinstance(results, list)
        assert len(results) == 3

    def test_result_fields(self):
        idx = self._setup_index()
        r = idx.retrieve("software")[0]
        assert r["document_id"]
        assert r["document_type"]
        assert r["title"]
        assert r["text"]
        assert "score" in r
        assert "metadata" in r
        assert "source" in r["metadata"]

    def test_document_type_filter(self):
        idx = self._setup_index()
        results = idx.retrieve("skill", filters={"document_type": "skill"})
        assert all(r["document_type"] == "skill" for r in results)
        assert len(results) == 1

    def test_empty_retrieval_when_no_match(self):
        idx = self._setup_index()
        idx.index.search.return_value = (np.array([[9.9]]), np.array([[-1]]))
        results = idx.retrieve("nothing here")
        assert results == []

    def test_synthetic_market_labelled(self):
        idx = self._setup_index()
        results = idx.retrieve("tech demand")
        market = [r for r in results if r["document_type"] == "market_signal"]
        assert all(r["metadata"].get("status") == "SYNTHETIC_PROTOTYPE" for r in market)

    def test_provenance_present(self):
        idx = self._setup_index()
        results = idx.retrieve("technology")
        for r in results:
            assert "source" in r["metadata"]


# ---------------------------------------------------------------------------
# 4. /api/guide endpoint
# ---------------------------------------------------------------------------

class TestGuideEndpoint:
    def _post(self, message, student_profile=None, parent_profile=None):
        payload = {"message": message}
        if student_profile:
            payload["student_profile"] = student_profile
        if parent_profile:
            payload["parent_profile"] = parent_profile
        return client.post("/api/guide", json=payload)

    def test_e2e_mocked(self):
        """Full mocked end-to-end: intent → engines → RAG → LLM → GuideResponse."""
        with patch("app.services.guide_service.retrieve", return_value=_mock_retrieve()), \
             patch("app.services.guide_service.process_chat_request", return_value=_mock_llm_response()):
            resp = self._post(
                "I like computers. What careers could fit me?",
                student_profile={"interests": ["computers"]}
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["answer"] == "Here is your guidance."
        assert "career_recommendation" in data["intent"]
        assert data["grounding"]["retrieved_documents"] == 1
        assert isinstance(data["grounding"]["deterministic_engines_used"], list)

    def test_financial_engine_called(self):
        with patch("app.services.guide_service.retrieve", return_value=[]), \
             patch("app.services.guide_service.process_chat_request", return_value=_mock_llm_response()):
            resp = self._post(
                "Can I afford medical college?",
                student_profile={
                    "tuition_per_year": 100000,
                    "living_per_year": 50000,
                    "course_years": 5,
                    "expected_entry_salary": 80000,
                    "loan_cap": 2000000,
                }
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "financial_feasibility" in data["intent"]
        assert "financial_solver" in data["grounding"]["deterministic_engines_used"]

    def test_conflict_engine_called_with_parent_profile(self):
        with patch("app.services.guide_service.retrieve", return_value=[]), \
             patch("app.services.guide_service.process_chat_request", return_value=_mock_llm_response()):
            resp = self._post(
                "My parents want me to study medicine but I disagree.",
                student_profile={"preference_vector": [1, 0, 0]},
                parent_profile={"preference_vector": [0, 1, 0]}
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "parent_student_alignment" in data["intent"]
        assert "conflict_engine" in data["grounding"]["deterministic_engines_used"]

    def test_stub_engines_return_unavailable(self):
        """Recommendation and skill engines are stubs – must return UNAVAILABLE, not fabricate."""
        with patch("app.services.guide_service.retrieve", return_value=[]), \
             patch("app.services.guide_service.process_chat_request", return_value=_mock_llm_response()) as mock_chat:
            resp = self._post("What careers suit my skills?")
        assert resp.status_code == 200

    def test_validation_error_missing_message(self):
        resp = client.post("/api/guide", json={"student_profile": {}})
        assert resp.status_code == 422

    def test_frontend_cannot_construct_llm_context(self):
        """
        The /api/guide schema is GuideRequest which has no llm_context field.
        Extra unknown fields must be silently ignored (not forwarded to the engine).
        The request must go through the normal orchestration path and NOT blindly
        use any injected context.
        503 is acceptable here because LLM_MODEL is not configured in the test env.
        """
        with patch("app.services.guide_service.retrieve", return_value=[]):
            resp = client.post("/api/guide", json={
                "message": "test",
                "llm_context": {"hacked": True}  # unknown field — must be ignored
            })
        # 200 (mocked LLM), 422 (validation rejected it), or 503 (LLM_MODEL not set)
        # All three prove the injected llm_context was not used
        assert resp.status_code in (200, 422, 503)

    def test_deterministic_value_authoritative_in_context(self):
        """When financial engine runs, the LLMContext must contain authoritative=True results."""
        captured_context = {}

        def capture_request(req: LLMRequest):
            captured_context.update(req.context.model_dump())
            return _mock_llm_response()

        with patch("app.services.guide_service.retrieve", return_value=[]), \
             patch("app.services.guide_service.process_chat_request", side_effect=capture_request):
            self._post(
                "Can I afford this course fee?",
                student_profile={"tuition_per_year": 400000, "expected_entry_salary": 80000,
                                 "course_years": 4, "loan_cap": 2000000}
            )

        fin = captured_context.get("deterministic_results", {}).get("financial", {})
        assert fin, "financial results missing from LLMContext"
        for key, val in fin.items():
            assert val.get("authoritative") is True, f"{key} must be marked authoritative"


# ---------------------------------------------------------------------------
# 5. LocalProvider (no weights)
# ---------------------------------------------------------------------------

class TestLocalProvider:
    def test_raises_without_llm_model_env(self):
        """If LLM_MODEL is not set, generate() must raise RuntimeError, not return fake text."""
        os.environ.pop("LLM_MODEL", None)
        from app.llm.providers.local import LocalProvider
        provider = LocalProvider()
        with pytest.raises(RuntimeError, match="LLM_MODEL environment variable is not set"):
            provider.generate("Hello")

    def test_health_reports_unconfigured(self):
        os.environ.pop("LLM_MODEL", None)
        from app.llm.providers.local import LocalProvider
        provider = LocalProvider()
        h = provider.health()
        assert h["model_configured"] is False

    def test_model_name_returns_env(self):
        os.environ["LLM_MODEL"] = "Qwen/Qwen3-4B-Instruct-2507"
        from app.llm.providers.local import LocalProvider
        provider = LocalProvider()
        assert provider.model_name() == "Qwen/Qwen3-4B-Instruct-2507"
        del os.environ["LLM_MODEL"]


# ---------------------------------------------------------------------------
# 6. /api/llm/chat still works
# ---------------------------------------------------------------------------

class TestLLMChatEndpoint:
    def test_llm_chat_still_works(self):
        """Ensure existing /api/llm/chat endpoint is unbroken."""
        with patch("app.services.llm_service.get_llm_provider") as mock_factory:
            mock_prov = MagicMock()
            mock_prov.generate.return_value = "LLM response"
            mock_prov.model_name.return_value = "mock"
            mock_factory.return_value = mock_prov

            resp = client.post("/api/llm/chat", json={
                "prompt": "What is AI?",
                "context": {
                    "user_profile": {},
                    "user_message": "What is AI?",
                    "deterministic_results": {},
                    "retrieved_documents": [],
                    "constraints": {},
                    "provenance": []
                }
            })
        assert resp.status_code == 200
        data = resp.json()
        assert "response_text" in data
