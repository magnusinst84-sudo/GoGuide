"""
Skill repository layer operating lazily over CSV crosswalks and dictionaries.
"""
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RequiredSkill:
    skill_id: str
    skill_name: str
    category: str = "General"
    relationship_type: str = "ESSENTIAL"
    confidence: float = 1.0


class SkillRepository:
    """Lazy-loading read-only repository over skill crosswalks and dictionaries."""

    def __init__(
        self,
        edges_path: Path | str = "data/crosswalks/occupation_skill_edges.csv",
        dict_path: Path | str = "data/dictionaries/skill_dictionary.csv",
    ):
        self._edges_path = Path(edges_path)
        self._dict_path = Path(dict_path)

        self._occupation_skills_map: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._skill_dict: Optional[Dict[str, Dict[str, Any]]] = None
        self._normalized_name_map: Optional[Dict[str, str]] = None

    def _ensure_loaded(self) -> None:
        if self._skill_dict is not None:
            return

        # Load skill dictionary
        self._skill_dict = {}
        self._normalized_name_map = {}
        if self._dict_path.exists():
            with open(self._dict_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sid = row.get("skill_id", "").strip()
                    sname = row.get("canonical_skill_name", "").strip()
                    if sid:
                        self._skill_dict[sid] = row
                    if sname:
                        self._normalized_name_map[sname.lower()] = sname

        # Load occupation-skill edges
        self._occupation_skills_map = {}
        if self._edges_path.exists():
            with open(self._edges_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row.get("occupation_id", "").strip()
                    if oid:
                        self._occupation_skills_map.setdefault(oid, []).append(row)

    def get_required_skills(self, canonical_occupation_id: str) -> List[RequiredSkill]:
        self._ensure_loaded()
        edges = self._occupation_skills_map.get(canonical_occupation_id, [])
        skills: List[RequiredSkill] = []

        for edge in edges:
            sid = edge.get("skill_id", "").strip()
            dict_entry = self._skill_dict.get(sid, {})
            sname = dict_entry.get("canonical_skill_name") or sid
            scat = dict_entry.get("skill_category") or "General"
            rel = edge.get("relationship_type") or "ESSENTIAL"
            try:
                conf = float(edge.get("confidence", 1.0))
            except (ValueError, TypeError):
                conf = 1.0

            skills.append(
                RequiredSkill(
                    skill_id=sid,
                    skill_name=sname,
                    category=scat,
                    relationship_type=rel,
                    confidence=conf,
                )
            )

        # Sort deterministically by skill_id
        skills.sort(key=lambda s: s.skill_id)
        return skills

    def normalize_skill(self, name: str) -> Optional[str]:
        self._ensure_loaded()
        if not name:
            return None
        clean_name = name.strip()
        # Direct lookup or lowercase normalized lookup
        if clean_name.lower() in self._normalized_name_map:
            return self._normalized_name_map[clean_name.lower()]
        return clean_name