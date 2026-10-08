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
from app.engines.recommendation_engine import get_recommendations
from app.engines.skill_gap_engine import analyze_skill_gap
from app.engines.pathway_engine import analyze_pathway

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

    # ── Recommendation engine ─────────────────────────────────────
    if "career_recommendation" in intents or request.student_profile.get("target_career"):
        recs = get_recommendations(request.student_profile)
        if recs:
            deterministic_results["recommendations"] = _authoritative(recs, "recommendation_engine")
            engines_used.append("recommendation_engine")
            provenance.append(Evidence(source="recommendation_engine", value="Top recommendations generated based on profile"))
            
            # Select the top recommendation or target career for further analysis
            primary_occ_id = recs[0]["occupation_id"]
            
            # ── Skill gap engine ──────────────────────────────────────────
            if "skill_gap" in intents or "career_recommendation" in intents:
                sg = analyze_skill_gap(request.student_profile, primary_occ_id)
                deterministic_results["skill_gap"] = _authoritative(sg, "skill_gap_engine")
                engines_used.append("skill_gap_engine")
                provenance.append(Evidence(source="skill_gap_engine", value="Skill gap analyzed against top recommendation"))
                
            # ── Pathway engine ────────────────────────────────────────────
            if "education_pathway" in intents or "career_recommendation" in intents:
                pw = analyze_pathway(primary_occ_id)
                if pw["status"] == "AVAILABLE":
                    deterministic_results["education_pathway"] = _authoritative(pw, "pathway_engine")
                    engines_used.append("pathway_engine")
                    provenance.append(Evidence(source="pathway_engine", value="Education pathways retrieved for top recommendation"))
                else:
                    deterministic_results["education_pathway"] = _unavailable("pathway_engine", pw["reason"])
        else:
            deterministic_results["recommendations"] = _unavailable("recommendation_engine", "Insufficient evidence to generate rankable recommendations.")
    else:
        # User didn't ask for a career and no target career provided
        if "skill_gap" in intents:
             deterministic_results["skill_gap"] = _unavailable("skill_gap_engine", "No target career specified for skill gap analysis.")
        if "education_pathway" in intents:
             deterministic_results["education_pathway"] = _unavailable("pathway_engine", "No target career specified for pathway analysis.")

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
        status="AVAILABLE",
        answer=llm_resp.response_text,
        intent=intents,
        recommendations=deterministic_results.get("recommendations", {}).get("value", []) if isinstance(deterministic_results.get("recommendations"), dict) else [],
        skill_gap=deterministic_results.get("skill_gap", {}).get("value") if isinstance(deterministic_results.get("skill_gap"), dict) else None,
        pathway=deterministic_results.get("education_pathway", {}).get("value") if isinstance(deterministic_results.get("education_pathway"), dict) else None,
        financial=deterministic_results.get("financial"),
        conflict=deterministic_results.get("conflict"),
        actions=[],
        sources=provenance,
        grounding=GroundingInfo(
            retrieved_documents=len(retrieved_docs),
            deterministic_engines_used=engines_used,
        ),
    )
