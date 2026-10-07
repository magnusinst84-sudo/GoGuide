"""
Indexes for R2 dataset entity lookups.
"""
from typing import Any, Dict, List
from backend.app.data.loaders import R2DataBundle


class R2Indexes:
    """In-memory indexes for careers and scholarships with deterministic ordering."""

    def __init__(self, bundle: R2DataBundle):
        self._careers_by_id: Dict[str, Dict[str, Any]] = {}
        self._careers_by_canonical_id: Dict[str, List[Dict[str, Any]]] = {}
        self._careers_by_stream: Dict[str, List[Dict[str, Any]]] = {}
        self._careers_by_education_level: Dict[str, List[Dict[str, Any]]] = {}

        self._scholarships_by_id: Dict[str, Dict[str, Any]] = {}
        self._scholarships_by_education_level: Dict[str, List[Dict[str, Any]]] = {}

        self._build_indexes(bundle)

    def _extract_values(self, item: Dict[str, Any], keys: List[str]) -> List[str]:
        values: List[str] = []
        for k in keys:
            val = item.get(k)
            if val is None:
                continue
            if isinstance(val, list):
                for v in val:
                    if isinstance(v, str) and v.strip() and v.strip() not in values:
                        values.append(v.strip())
            elif isinstance(val, str) and val.strip():
                if val.strip() not in values:
                    values.append(val.strip())
        return values

    def _build_indexes(self, bundle: R2DataBundle) -> None:
        sorted_careers = sorted(bundle.careers, key=lambda c: c["id"])

        # 1. Careers by R2 ID
        for c in sorted_careers:
            self._careers_by_id[c["id"]] = c

        # 2. Careers by Canonical ID
        for r2_id, canonical_id in bundle.id_map.items():
            if canonical_id and r2_id in self._careers_by_id:
                career = self._careers_by_id[r2_id]
                self._careers_by_canonical_id.setdefault(canonical_id, []).append(career)

        for can_id in self._careers_by_canonical_id:
            self._careers_by_canonical_id[can_id].sort(key=lambda c: c["id"])

        # 3. Careers by Stream & 4. Careers by Education Level
        stream_keys = ["stream", "streams", "stream_tags", "cluster"]
        edu_keys = ["education_level", "min_education_level", "eligible_education_levels", "level"]

        for c in sorted_careers:
            streams = self._extract_values(c, stream_keys) or ["unspecified"]
            for st in streams:
                self._careers_by_stream.setdefault(st, []).append(c)

            edu_levels = self._extract_values(c, edu_keys) or ["unspecified"]
            for el in edu_levels:
                self._careers_by_education_level.setdefault(el, []).append(c)

        for st in self._careers_by_stream:
            self._careers_by_stream[st].sort(key=lambda c: c["id"])
        for el in self._careers_by_education_level:
            self._careers_by_education_level[el].sort(key=lambda c: c["id"])

        # 5. Scholarships by ID & 6. Scholarships by Education Level
        sorted_scholarships = sorted(bundle.scholarships, key=lambda s: s["id"])

        for s in sorted_scholarships:
            self._scholarships_by_id[s["id"]] = s
            edu_levels = self._extract_values(s, edu_keys) or ["unspecified"]
            for el in edu_levels:
                self._scholarships_by_education_level.setdefault(el, []).append(s)

        for el in self._scholarships_by_education_level:
            self._scholarships_by_education_level[el].sort(key=lambda s: s["id"])

    @property
    def careers_by_id(self) -> Dict[str, Dict[str, Any]]:
        return self._careers_by_id

    @property
    def careers_by_canonical_id(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._careers_by_canonical_id

    @property
    def careers_by_stream(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._careers_by_stream

    @property
    def careers_by_education_level(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._careers_by_education_level

    @property
    def scholarships_by_id(self) -> Dict[str, Dict[str, Any]]:
        return self._scholarships_by_id

    @property
    def scholarships_by_education_level(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._scholarships_by_education_level

