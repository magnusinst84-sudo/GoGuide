"""
Demand snapshot repository operating on R2 DataBundle.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from backend.app.data.loaders import R2DataBundle


@dataclass
class DemandSnapshot:
    fetched_at: Optional[str] = None
    source: Optional[str] = None
    status: str = "placeholder"
    entries: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DemandSnapshot":
        return cls(
            fetched_at=data.get("fetched_at"),
            source=data.get("source"),
            status=str(data.get("status", "placeholder")),
            entries=data.get("entries", {}),
            raw_data=data,
        )


class DemandRepository:
    def __init__(self, bundle: R2DataBundle):
        self._snapshot = DemandSnapshot.from_dict(bundle.demand_snapshot)

    def get_demand_snapshot(self) -> DemandSnapshot:
        return self._snapshot
