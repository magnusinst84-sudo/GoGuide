"""
guide_service.py – Context Orchestrator

Flow:
  GuideRequest
      → intent detection (keyword/rule based)
      → deterministic engine calls (only for engines that exist)
      → RAG retrieval
      → LLMContext assembly (deterministic results marked authoritative)
      → LLMService (provider-independent)
      → GuideResponse

Rules:
  - Deterministic engine results are marked {"value": ..., "source": ..., "authoritative": true}
  - Engines that are stubs (TODO) return {"status": "UNAVAILABLE"}
  - RAG documents are supporting context only; they never override engine outputs
  - Synthetic market data is explicitly labelled SYNTHETIC_PROTOTYPE
"""

from typing import List, Dict, Any
import logging

from app.schemas.guide import GuideRequest, GuideResponse, GroundingInfo
from app.schemas.llm import LLMContext, LLMRequest, Evidence
from app.services.llm_service import process_chat_request
from app.rag.index import retrieve

# Real engines (implemented)
from app.engines.financial_solver import (
    total_cost, funding_need, monthly_emi, affordability_ratio, financial_feasibility
)
from app.engines.conflict_engine import preference_alignment

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Intent keywords
# ---------------------------------------------------------------------------

_INTENT_RULES = [
    ("career_recommendation",    ["career", "job", "consider", "fit me", "should i be", "occupation"]),
    ("financial_feasibility",    ["afford", "cost", "fee", "money", "emi", "loan", "tuition", "scholarship"]),
    ("parent_student_alignment", ["parent", "mother", "father", "family", "conflict", "disagree", "want me to"]),
    ("skill_gap",                ["skill", "learn", "missing", "need to know"]),
    ("education_pathway",        ["degree", "college", "university", "study", "course", "pathway", "admission", "exam"]),
    ("market_outlook",           ["demand", "market", "future", "growth", "trend", "opportunities"]),
    ("what_if",                  ["what if", "if i choose", "scenario"]),
    ("general_guidance",         []),          # fallback
]


def _detect_intents(message: str) -> List[str]:
    msg = message.lower()
    found = [intent for intent, keywords in _INTENT_RULES[:-1] if any(k in msg for k in keywords)]
    if not found:
        found = ["general_guidance"]
    return found


# ---------------------------------------------------------------------------
# Authoritative result wrapper
# ---------------------------------------------------------------------------

def _authoritative(value: Any, source: str) -> Dict[str, Any]:
    """Wrap a deterministic result so the LLM knows it must not recalculate it."""
    return {"value": value, "source": source, "authoritative": True}


def _unavailable(engine_name: str, reason: str = "Engine not yet implemented") -> Dict[str, Any]:
    return {"status": "UNAVAILABLE", "engine": engine_name, "reason": reason, "authoritative": True}


# ---------------------------------------------------------------------------
# Individual engine calls
# ---------------------------------------------------------------------------

def _run_financial_solver(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses real financial_solver functions.
    Pulls values from student profile where present; uses transparent defaults otherwise.
    """
    tuition   = float(profile.get("tuition_per_year", 0))
    living    = float(profile.get("living_per_year", 0))
    years     = int(profile.get("course_years", 4))
    savings   = float(profile.get("savings", 0))
    annual_bud= float(profile.get("annual_budget", 0))
    scholarship = float(profile.get("scholarship", 0))
    entry_sal = float(profile.get("expected_entry_salary", 0))
    monthly_rate = float(profile.get("loan_monthly_rate", 0.01))
    loan_months  = int(profile.get("loan_months", 60))
    loan_cap     = float(profile.get("loan_cap", 2_000_000))
    max_ratio    = float(profile.get("max_emi_ratio", 0.4))

    tc   = total_cost(tuition, living, years)
    fn   = funding_need(tc, savings, annual_bud, years, scholarship)
    emi  = monthly_emi(fn, monthly_rate, loan_months)
    ar   = affordability_ratio(emi, entry_sal) if entry_sal > 0 else float("inf")
    feas = financial_feasibility(fn, loan_cap, ar, max_ratio)

    return {
        "total_cost":           _authoritative(tc,   "financial_solver"),
        "funding_need":         _authoritative(fn,   "financial_solver"),
        "monthly_emi":          _authoritative(emi,  "financial_solver"),
        "affordability_ratio":  _authoritative(ar,   "financial_solver"),
        "is_feasible":          _authoritative(feas["is_feasible"],  "financial_solver"),
        "loan_cap_exceeded":    _authoritative(feas["loan_cap_exceeded"], "financial_solver"),
    }


def _run_conflict_engine(student_profile: Dict[str, Any], parent_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses real conflict_engine.preference_alignment.
    Expects 'preference_vector' keys; returns conflict index.
    """
    sv = student_profile.get("preference_vector", [])
    pv = parent_profile.get("preference_vector", [])
    if not sv or not pv or len(sv) != len(pv):
        return _unavailable("conflict_engine", "preference_vector missing or mismatched in profiles")

    conflict_idx = preference_alignment(sv, pv)
    return {"conflict_index": _authoritative(conflict_idx, "conflict_engine")}


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def process_guide_request(request: GuideRequest) -> GuideResponse:
    intents = _detect_intents(request.message)
    logger.info(f"Detected intents: {intents} for message: '{request.message[:60]}'")

    deterministic_results: Dict[str, Any] = {}
    engines_used: List[str] = []
    provenance: List[Evidence] = []

    # ── Financial solver ────────────────────────────────────────────────
    if "financial_feasibility" in intents:
        try:
            fin = _run_financial_solver(request.student_profile)
            deterministic_results["financial"] = fin
            engines_used.append("financial_solver")
            provenance.append(Evidence(source="financial_solver", value="EMI/feasibility computed from student profile"))
        except Exception as e:
            logger.warning(f"financial_solver failed: {e}")
            deterministic_results["financial"] = _unavailable("financial_solver", str(e))

    # ── Conflict engine ──────────────────────────────────────────────────
    if "parent_student_alignment" in intents and request.parent_profile:
        try:
            conflict = _run_conflict_engine(request.student_profile, request.parent_profile)
            deterministic_results["conflict"] = conflict
            engines_used.append("conflict_engine")
            provenance.append(Evidence(source="conflict_engine", value="Preference alignment computed"))
        except Exception as e:
            logger.warning(f"conflict_engine failed: {e}")
            deterministic_results["conflict"] = _unavailable("conflict_engine", str(e))

    # ── Recommendation engine (stub) ─────────────────────────────────────
    if "career_recommendation" in intents:
        deterministic_results["recommendations"] = _unavailable(
            "recommendation_engine",
            "Recommendation engine not yet wired to backend service layer. "
            "See data/processed/recommendations_v2/ for pre-computed outputs."
        )

    # ── Skill gap engine (stub) ──────────────────────────────────────────
    if "skill_gap" in intents:
        deterministic_results["skill_gap"] = _unavailable(
            "skill_gap_engine",
            "Skill gap engine not yet implemented in the service layer."
        )

    # ── Pathway engine (stub) ────────────────────────────────────────────
    if "education_pathway" in intents:
        deterministic_results["education_pathway"] = _unavailable(
            "pathway_engine",
            "Pathway engine not yet implemented in the service layer."
        )

    # ── RAG retrieval ────────────────────────────────────────────────────
    retrieved_docs = retrieve(request.message, top_k=5)
    provenance.extend([
        Evidence(source=doc.get("metadata", {}).get("source", "unknown"),
                 value=f"Retrieved doc: {doc.get('title', '')} [type={doc.get('document_type', '')}]",
                 confidence="RAG")
        for doc in retrieved_docs
    ])

    # ── Assemble LLMContext ───────────────────────────────────────────────
    context = LLMContext(
        user_profile=request.student_profile,
        user_message=request.message,
        deterministic_results=deterministic_results,
        retrieved_documents=retrieved_docs,
        constraints={},
        provenance=provenance,
    )

    # ── Call LLM ─────────────────────────────────────────────────────────
    llm_req = LLMRequest(prompt=request.message, context=context)
    llm_resp = process_chat_request(llm_req)

    return GuideResponse(
        answer=llm_resp.response_text,
        intent=intents,
        recommendations=[],
        actions=[],
        sources=provenance,
        grounding=GroundingInfo(
            retrieved_documents=len(retrieved_docs),
            deterministic_engines_used=engines_used,
        ),
    )
