"""
Data loaders for R2 dataset files under data/r2/.
"""
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union


class DataLoaderError(Exception):
    """Base exception for all R2 data loader and validation errors."""
    pass


class MissingFileError(DataLoaderError):
    """Raised when a required R2 data file is missing."""
    pass


class MalformedJSONError(DataLoaderError):
    """Raised when an R2 data file contains invalid JSON syntax."""
    pass


class DuplicateIDError(DataLoaderError):
    """Raised when duplicate IDs are detected within an R2 dataset."""
    pass


class DanglingReferenceError(DataLoaderError):
    """Raised when an entity references a non-existent ID."""
    pass


@dataclass(frozen=True)
class R2DataBundle:
    careers: List[Dict[str, Any]]
    scholarships: List[Dict[str, Any]]
    local_opportunities: List[Dict[str, Any]]
    demand_snapshot: Dict[str, Any]
    questions: List[Dict[str, Any]]
    id_map: Dict[str, str] = field(default_factory=dict)
    raw_id_map: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None


def _load_json_file(file_path: Path, required: bool = True) -> Optional[Any]:
    if not file_path.exists():
        if required:
            raise MissingFileError(f"Required R2 file missing: '{file_path.name}' at path '{file_path}'")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise MalformedJSONError(f"Malformed JSON in file '{file_path.name}': {e}") from e


def _check_duplicate_ids(items: List[Dict[str, Any]], entity_name: str) -> Set[str]:
    seen_ids: Set[str] = set()
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise MalformedJSONError(f"Expected dict item at index {idx} in {entity_name}, got {type(item).__name__}")
        item_id = item.get("id")
        if not item_id:
            raise MalformedJSONError(f"Missing 'id' field in {entity_name} record at index {idx}")
        if item_id in seen_ids:
            raise DuplicateIDError(f"Duplicate ID '{item_id}' found in dataset '{entity_name}'")
        seen_ids.add(item_id)
    return seen_ids


def _parse_and_validate_id_map(
    id_map_raw: Any, career_ids: Set[str], file_name: str = "id_map.json"
) -> Dict[str, str]:
    if id_map_raw is None:
        return {}

    id_map_dict: Dict[str, str] = {}
    seen_r2_ids: Set[str] = set()

    if isinstance(id_map_raw, dict):
        for r2_id, value in id_map_raw.items():
            if r2_id in seen_r2_ids:
                raise DuplicateIDError(f"Duplicate r2_id '{r2_id}' found in '{file_name}'")
            seen_r2_ids.add(r2_id)

            if isinstance(value, dict):
                canonical_id = str(value.get("canonical_id", ""))
            else:
                canonical_id = str(value)

            id_map_dict[r2_id] = canonical_id

    elif isinstance(id_map_raw, list):
        for idx, entry in enumerate(id_map_raw):
            if not isinstance(entry, dict):
                raise MalformedJSONError(f"Expected dict entry in '{file_name}' at index {idx}")
            r2_id = entry.get("r2_id")
            if not r2_id:
                raise MalformedJSONError(f"Missing 'r2_id' field in '{file_name}' entry at index {idx}")
            if r2_id in seen_r2_ids:
                raise DuplicateIDError(f"Duplicate r2_id '{r2_id}' found in '{file_name}'")
            seen_r2_ids.add(r2_id)
            id_map_dict[r2_id] = str(entry.get("canonical_id", ""))
    else:
        raise MalformedJSONError(f"Unsupported root JSON structure in '{file_name}': expected list or dict")

    for r2_id in id_map_dict:
        if r2_id not in career_ids:
            raise DanglingReferenceError(
                f"id_map entry references dangling r2_id '{r2_id}' not found in careers dataset"
            )

    return id_map_dict


def load_r2_data(data_dir: Union[str, Path] = "data/r2") -> R2DataBundle:
    """Eagerly loads and validates small R2 data files under data/r2/."""
    base_dir = Path(data_dir)

    careers_raw = _load_json_file(base_dir / "careers.json", required=True)
    scholarships_raw = _load_json_file(base_dir / "scholarships.json", required=True)
    local_opps_raw = _load_json_file(base_dir / "local_opportunities.json", required=True)
    demand_snapshot_raw = _load_json_file(base_dir / "demand_snapshot.json", required=True)
    questions_raw = _load_json_file(base_dir / "questions.json", required=True)
    id_map_raw = _load_json_file(base_dir / "id_map.json", required=False)

    if not isinstance(careers_raw, list):
        raise MalformedJSONError("careers.json root structure must be a list")
    if not isinstance(scholarships_raw, list):
        raise MalformedJSONError("scholarships.json root structure must be a list")
    if not isinstance(local_opps_raw, list):
        raise MalformedJSONError("local_opportunities.json root structure must be a list")
    if not isinstance(demand_snapshot_raw, dict):
        raise MalformedJSONError("demand_snapshot.json root structure must be a dict")
    if not isinstance(questions_raw, list):
        raise MalformedJSONError("questions.json root structure must be a list")

    career_ids = _check_duplicate_ids(careers_raw, "careers.json")
    scholarship_ids = _check_duplicate_ids(scholarships_raw, "scholarships.json")
    _check_duplicate_ids(local_opps_raw, "local_opportunities.json")
    _check_duplicate_ids(questions_raw, "questions.json")

    for career in careers_raw:
        cid = career["id"]
        for adj_id in career.get("adjacent", []):
            if adj_id not in career_ids:
                raise DanglingReferenceError(
                    f"Career '{cid}' references dangling adjacent career ID '{adj_id}'"
                )

        for sch_id in career.get("scholarship_ids", []):
            if sch_id not in scholarship_ids:
                raise DanglingReferenceError(
                    f"Career '{cid}' references dangling scholarship ID '{sch_id}'"
                )

    parsed_id_map = _parse_and_validate_id_map(id_map_raw, career_ids)

    return R2DataBundle(
        careers=careers_raw,
        scholarships=scholarships_raw,
        local_opportunities=local_opps_raw,
        demand_snapshot=demand_snapshot_raw,
        questions=questions_raw,
        id_map=parsed_id_map,
        raw_id_map=id_map_raw,
    )