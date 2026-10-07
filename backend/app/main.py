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
    return {"status": "not_implemented", "message": "Feature scaffold created; implementation pending."}

@app.post("/api/students")
def create_student(): return not_implemented_response()

@app.post("/api/recommendations")
def get_recommendations(): return not_implemented_response()

@app.get("/api/recommendations/student/{student_id}")
def get_student_recommendations(student_id: str): return not_implemented_response()

@app.get("/api/careers")
def list_careers(): return not_implemented_response()

@app.get("/api/careers/{career_id}")
def get_career(career_id: str): return not_implemented_response()

@app.post("/api/financial/solver")
def solve_financial(): return not_implemented_response()

@app.post("/api/conflict")
def resolve_conflict(): return not_implemented_response()

@app.post("/api/skills/gap")
def analyze_skills_gap(): return not_implemented_response()

@app.get("/api/pathways/{career_id}")
def get_pathways(career_id: str): return not_implemented_response()

@app.post("/api/action-plan")
def create_action_plan(): return not_implemented_response()

@app.post("/api/llm/chat")
def chat_with_llm(): return not_implemented_response()
