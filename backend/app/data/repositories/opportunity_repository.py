"""
Local opportunity repository operating on R2 DataBundle.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.app.data.loaders import R2DataBundle


@dataclass
class LocalOpportunity:
    id: str
    city: str
    problem: str
    domain_tags: List[str] = field(default_factory=list)
    skill_tags: List[str] = field(default_factory=list)
    project_idea: str = ""
    source: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocalOpportunity":
        return cls(
            id=str(data.get("id", "")),
            city=str(data.get("city", "")),
            problem=str(data.get("problem", "")),
            domain_tags=data.get("domain_tags", []),
            skill_tags=data.get("skill_tags", []),
            project_idea=str(data.get("project_idea", "")),
            source=str(data.get("source", "")),
            raw_data=data,
        )


@dataclass
class LocalOpportunityResult:
    found: bool
    opportunity: Optional[LocalOpportunity] = None
    message: Optional[str] = None


class LocalOpportunityRepository:
    def __init__(self, bundle: R2DataBundle):
        self._cache: Dict[str, LocalOpportunity] = {}
        for item in sorted(bundle.local_opportunities, key=lambda x: x.get("id", "")):
            opp = LocalOpportunity.from_dict(item)
            self._cache[opp.id] = opp

    def get_opportunity(self, opportunity_id: str) -> LocalOpportunityResult:
        opp = self._cache.get(opportunity_id)
        if not opp:
            return LocalOpportunityResult(
                found=False,
                opportunity=None,
                message=f"Local opportunity '{opportunity_id}' not found.",
            )
        return LocalOpportunityResult(found=True, opportunity=opp)

    def list_opportunities(self, city: Optional[str] = None) -> List[LocalOpportunity]:
        opps = list(self._cache.values())
        if city:
            c_clean = city.strip().lower()
            opps = [o for o in opps if o.city.lower() == c_clean]
        opps.sort(key=lambda o: o.id)
        return opps
