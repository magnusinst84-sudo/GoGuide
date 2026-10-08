"""
Education program repository layer operating on R2 loaders and indexes.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.app.data.repositories.career_repository import Career, CareerRepository


@dataclass
class EducationProgram:
    id: str
    name: str
    tuition_per_year: int = 0
    living_per_year: int = 0
    years: float = 0.0
    entrance_required: bool = False
    exams: List[str] = field(default_factory=list)
    adjacent: List[str] = field(default_factory=list)
    scholarship_ids: List[str] = field(default_factory=list)
    sources: Dict[str, Any] = field(default_factory=dict)
    estimated_fields: List[str] = field(default_factory=list)
    placeholder: bool = False
    stream: Optional[str] = None
    education_level: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_career(cls, career: Career) -> "EducationProgram":
        return cls(
            id=career.id,
            name=career.name,
            tuition_per_year=career.tuition_per_year,
            living_per_year=career.living_per_year,
            years=career.years,
            entrance_required=career.entrance_required,
            exams=career.exams,
            adjacent=career.adjacent,
            scholarship_ids=career.scholarship_ids,
            sources=career.sources,
            estimated_fields=career.estimated_fields,
            placeholder=career.placeholder,
            stream=career.stream,
            education_level=career.education_level,
            raw_data=career.raw_data,
        )


@dataclass
class EducationResult:
    found: bool
    program: Optional[EducationProgram] = None
    message: Optional[str] = None


class EducationRepository:
    def __init__(self, career_repo: CareerRepository):
        self._career_repo = career_repo

    def get_education(self, education_id: str) -> EducationResult:
        res = self._career_repo.get_career(education_id)
        if not res.found or not res.career:
            return EducationResult(
                found=False,
                program=None,
                message=f"Education program with ID '{education_id}' not found.",
            )
        return EducationResult(
            found=True, program=EducationProgram.from_career(res.career)
        )

    def list_education(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_placeholder: bool = False,
    ) -> List[EducationProgram]:
        careers = self._career_repo.list_careers(
            filters=filters, include_placeholder=include_placeholder
        )
        return [EducationProgram.from_career(c) for c in careers]

    def get_adjacent(
        self, education_id: str, include_placeholder: bool = False
    ) -> List[EducationProgram]:
        adj_careers = self._career_repo.get_adjacent(
            education_id, include_placeholder=include_placeholder
        )
        return [EducationProgram.from_career(c) for c in adj_careers]