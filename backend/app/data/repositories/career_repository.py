"""
Career repository layer operating on R2 loaders and indexes.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.app.data.loaders import MalformedJSONError
from backend.app.data.indexes import R2Indexes


@dataclass
class Career:
    id: str
    name: str
    riasec: List[float] = field(default_factory=list)
    tuition_per_year: int = 0
    living_per_year: int = 0
    years: float = 0.0
    coaching: int = 0
    salary: Dict[str, int] = field(default_factory=dict)
    years_to_first_income: float = 0.0
    static_national: float = 0.0
    city_demand: Dict[str, float] = field(default_factory=dict)
    growth_index: float = 0.0
    automation_risk: float = 0.0
    career_risk: float = 0.0
    entrance_required: bool = False
    expected_scholarship: int = 0
    skills: List[Dict[str, Any]] = field(default_factory=list)
    roadmap: List[Dict[str, Any]] = field(default_factory=list)
    exams: List[str] = field(default_factory=list)
    scholarship_ids: List[str] = field(default_factory=list)
    adjacent: List[str] = field(default_factory=list)
    sources: Dict[str, Any] = field(default_factory=dict)
    estimated_fields: List[str] = field(default_factory=list)
    placeholder: bool = False
    stream: Optional[str] = None
    education_level: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Career":
        if not isinstance(data, dict):
            raise MalformedJSONError(f"Career record must be a dict, got {type(data).__name__}")
        if "id" not in data or not data["id"]:
            raise MalformedJSONError("Career record missing required 'id' field")
        if "name" not in data or not data["name"]:
            raise MalformedJSONError("Career record missing required 'name' field")

        estimated = data.get("estimated_fields", [])
        has_stub = "stub" in estimated
        sources = data.get("sources", {})
        note = sources.get("_note", "") if isinstance(sources, dict) else ""
        is_placeholder = has_stub and ("placeholder" in str(note).lower())

        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            riasec=data.get("riasec", []),
            tuition_per_year=int(data.get("tuition_per_year", 0)),
            living_per_year=int(data.get("living_per_year", 0)),
            years=float(data.get("years", 0.0)),
            coaching=int(data.get("coaching", 0)),
            salary=data.get("salary", {}),
            years_to_first_income=float(data.get("years_to_first_income", 0.0)),
            static_national=float(data.get("static_national", 0.0)),
            city_demand=data.get("city_demand", {}),
            growth_index=float(data.get("growth_index", 0.0)),
            automation_risk=float(data.get("automation_risk", 0.0)),
            career_risk=float(data.get("career_risk", 0.0)),
            entrance_required=bool(data.get("entrance_required", False)),
            expected_scholarship=int(data.get("expected_scholarship", 0)),
            skills=data.get("skills", []),
            roadmap=data.get("roadmap", []),
            exams=data.get("exams", []),
            scholarship_ids=data.get("scholarship_ids", []),
            adjacent=data.get("adjacent", []),
            sources=sources,
            estimated_fields=estimated,
            placeholder=is_placeholder,
            stream=data.get("stream") or data.get("cluster"),
            education_level=data.get("education_level"),
            raw_data=data,
        )


@dataclass
class CareerResult:
    found: bool
    career: Optional[Career] = None
    message: Optional[str] = None


class CareerRepository:
    def __init__(self, indexes: R2Indexes):
        self._indexes = indexes
        self._careers_cache: Dict[str, Career] = {}
        self._init_cache()

    def _init_cache(self) -> None:
        for cid, raw_career in self._indexes.careers_by_id.items():
            self._careers_cache[cid] = Career.from_dict(raw_career)

    def get_career(self, career_id: str) -> CareerResult:
        career = self._careers_cache.get(career_id)
        if not career:
            return CareerResult(
                found=False,
                career=None,
                message=f"Career with ID '{career_id}' not found.",
            )
        return CareerResult(found=True, career=career)

    def list_careers(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_placeholder: bool = False,
    ) -> List[Career]:
        filters = filters or {}
        results: List[Career] = []

        candidate_ids = list(self._indexes.careers_by_id.keys())

        if "canonical_id" in filters and filters["canonical_id"]:
            can_id = filters["canonical_id"]
            if can_id in self._indexes.careers_by_canonical_id:
                candidate_ids = [
                    c["id"] for c in self._indexes.careers_by_canonical_id[can_id]
                ]
            else:
                candidate_ids = []

        for cid in candidate_ids:
            career = self._careers_cache[cid]

            # Rule: exclude placeholder unless include_placeholder=True
            if career.placeholder and not include_placeholder:
                continue

            if "stream" in filters and filters["stream"]:
                st_filter = str(filters["stream"]).lower()
                c_stream = (career.stream or "").lower()
                if st_filter not in c_stream:
                    continue

            if "education_level" in filters and filters["education_level"]:
                el_filter = str(filters["education_level"]).lower()
                c_el = (career.education_level or "").lower()
                if el_filter not in c_el:
                    continue

            if "max_tuition" in filters and filters["max_tuition"] is not None:
                if career.tuition_per_year > int(filters["max_tuition"]):
                    continue

            if "min_salary" in filters and filters["min_salary"] is not None:
                min_sal = int(filters["min_salary"])
                y1_sal = career.salary.get("y1", 0)
                if y1_sal < min_sal:
                    continue

            results.append(career)

        return results

    def get_adjacent(
        self, career_id: str, include_placeholder: bool = False
    ) -> List[Career]:
        res = self.get_career(career_id)
        if not res.found or not res.career:
            return []

        adj_careers: List[Career] = []
        for adj_id in res.career.adjacent:
            adj_res = self.get_career(adj_id)
            if adj_res.found and adj_res.career:
                if adj_res.career.placeholder and not include_placeholder:
                    continue
                adj_careers.append(adj_res.career)

        adj_careers.sort(key=lambda c: c.id)
        return adj_careers