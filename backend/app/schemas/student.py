from pydantic import BaseModel, Field
from typing import Dict, Optional, Union

class StudentSkills(BaseModel):
    mathematics: float = 0.0
    statistics: float = 0.0
    programming: float = 0.0
    logic: float = 0.0
    communication: float = 0.0
    design: float = 0.0
    biology: float = 0.0
    electronics: float = 0.0

class StudentProfile(BaseModel):
    academic_stream: Optional[str] = None
    marks_percentage: Optional[float] = None
    current_city: Optional[str] = None
    interests: Dict[str, Optional[Union[int, float]]] = Field(default_factory=dict)
    skills: StudentSkills = Field(default_factory=StudentSkills)
    risk_tolerance: Optional[Union[int, float]] = None
    target_career: Optional[str] = None

    # Allows additional arbitrary kwargs like tuition_per_year for financial_solver compatibility
    model_config = {"extra": "allow"}