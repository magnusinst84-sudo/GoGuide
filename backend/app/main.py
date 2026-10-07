from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="GoGuide Backend", version="0.1.0")

origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "goguide-backend", "version": "0.1.0"}

def not_implemented_response():
    return {"status": "UNAVAILABLE", "message": "Feature scaffold created; implementation pending."}

@app.post("/api/students")
def create_student(): return not_implemented_response()

from app.schemas.student import StudentProfile
from app.services.recommendation_service import generate_recommendations
from app.services.skill_service import get_skill_gaps
from app.services.pathway_service import get_education_pathway
from app.engines.financial_solver import total_cost, funding_need, monthly_emi, affordability_ratio, financial_feasibility
from app.engines.conflict_engine import preference_alignment

@app.post("/api/recommendations")
def api_get_recommendations(profile: StudentProfile):
    recs = generate_recommendations(profile.model_dump())
    if not recs:
        return {"status": "UNAVAILABLE", "message": "Insufficient evidence"}
    return {"status": "AVAILABLE", "recommendations": recs}

@app.get("/api/recommendations/student/{student_id}")
def get_student_recommendations(student_id: str): return not_implemented_response()

@app.get("/api/careers")
def list_careers(): return not_implemented_response()

@app.get("/api/careers/{career_id}")
def get_career(career_id: str): return not_implemented_response()

@app.post("/api/financial/solver")
def solve_financial(profile: dict): 
    # Wrap in try-except if needed, but financial solver expects kwargs
    # We will just return unavailable for now since guide_service handles it
    return not_implemented_response()

@app.post("/api/conflict")
def resolve_conflict(data: dict):
    return not_implemented_response()

@app.post("/api/skills/gap")
def api_analyze_skills_gap(payload: dict):
    profile = payload.get("profile", {})
    occupation_id = payload.get("occupation_id")
    if not occupation_id:
        return {"status": "UNAVAILABLE", "message": "occupation_id required"}
    res = get_skill_gaps(profile, occupation_id)
    return {"status": "AVAILABLE", "data": res}

@app.get("/api/pathways/{career_id}")
def api_get_pathways(career_id: str): 
    res = get_education_pathway(career_id)
    return res

@app.post("/api/action-plan")
def create_action_plan(): return not_implemented_response()

from app.api.llm import router as llm_router
from app.api.guide import router as guide_router
from app.api.quick_doubts import router as quick_doubts_router

app.include_router(llm_router, prefix="/api/llm")
app.include_router(guide_router, prefix="/api/guide")
app.include_router(quick_doubts_router, prefix="/api/quick-doubts")
