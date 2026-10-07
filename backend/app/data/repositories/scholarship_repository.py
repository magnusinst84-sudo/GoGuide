"""
Scholarship repository layer operating on R2 loaders and indexes.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.app.data.indexes import R2Indexes


@dataclass
class Scholarship:
    id: str
    name: str
    provider: str
    amount: Optional[int] = None
    amount_note: Optional[str] = None
    income_cap_annual: Optional[int] = None
    stream_tags: List[str] = field(default_factory=list)
    min_marks_pct: Optional[float] = None
    eligibility_note: Optional[str] = None
    deadline: Optional[str] = None
    deadline_year_note: Optional[str] = None
    url: str = ""
    source_note: Optional[str] = None
    checked_on: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scholarship":
        amt = data.get("amount")
        amount_int = int(amt) if isinstance(amt, (int, float)) else None

        inc_cap = data.get("income_cap_annual")
        inc_cap_int = int(inc_cap) if isinstance(inc_cap, (int, float)) else None

        min_m = data.get("min_marks_pct")
        min_m_float = float(min_m) if isinstance(min_m, (int, float)) else None

        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            provider=str(data.get("provider", "")),
            amount=amount_int,
            amount_note=data.get("amount_note"),
            income_cap_annual=inc_cap_int,
            stream_tags=data.get("stream_tags", []),
            min_marks_pct=min_m_float,
            eligibility_note=data.get("_eligibility_note") or data.get("eligibility_note"),
            deadline=data.get("deadline"),
            deadline_year_note=data.get("deadline_year_note"),
            url=str(data.get("url", "")),
            source_note=data.get("source_note"),
            checked_on=data.get("checked_on"),
            raw_data=data,
        )


@dataclass
class ScholarshipResult:
    found: bool
    scholarship: Optional[Scholarship] = None
    message: Optional[str] = None


class ScholarshipRepository:
    def __init__(self, indexes: R2Indexes):
        self._indexes = indexes
        self._scholarship_cache: Dict[str, Scholarship] = {}
        self._init_cache()

    def _init_cache(self) -> None:
        for sid, raw_s in self._indexes.scholarships_by_id.items():
            self._scholarship_cache[sid] = Scholarship.from_dict(raw_s)

    def get_scholarship(self, scholarship_id: str) -> ScholarshipResult:
        s = self._scholarship_cache.get(scholarship_id)
        if not s:
            return ScholarshipResult(
                found=False,
                scholarship=None,
                message=f"Scholarship with ID '{scholarship_id}' not found.",
            )
        return ScholarshipResult(found=True, scholarship=s)

    def list_scholarships(self, filters: Optional[Dict[str, Any]] = None) -> List[Scholarship]:
        filters = filters or {}
        results: List[Scholarship] = []

        for sid in self._indexes.scholarships_by_id.keys():
            s = self._scholarship_cache[sid]

            if "max_income_cap" in filters and filters["max_income_cap"] is not None:
                # Rule: Null/pending means unknown, never no requirement
                if s.income_cap_annual is not None:
                    if s.income_cap_annual < int(filters["max_income_cap"]):
                        continue

            results.append(s)

        results.sort(key=lambda item: item.id)
        return results
