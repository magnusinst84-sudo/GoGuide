from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.llm import Evidence

class GuideRequest(BaseModel):
    message: str
    student_profile: Dict[str, Any] = Field(default_factory=dict)
    parent_profile: Optional[Dict[str, Any]] = None

class GroundingInfo(BaseModel):
    retrieved_documents: int
    deterministic_engines_used: List[str]

class GuideResponse(BaseModel):
    status: str = "AVAILABLE"
    answer: str
    intent: List[str]
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    skill_gap: Optional[Dict[str, Any]] = None
    pathway: Optional[Dict[str, Any]] = None
    financial: Optional[Dict[str, Any]] = None
    conflict: Optional[Dict[str, Any]] = None
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[Evidence] = Field(default_factory=list)
    grounding: GroundingInfo
