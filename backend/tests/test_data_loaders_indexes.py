import json
import os
from pathlib import Path
import pytest

from backend.app.data.loaders import (
    DanglingReferenceError,
    DuplicateIDError,
    MalformedJSONError,
    MissingFileError,
    R2DataBundle,
    load_r2_data,
)
from backend.app.data.indexes import R2Indexes


def _write_json(path: Path, data: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _create_minimal_r2_directory(tmp_path: Path) -> Path:
    careers = [
        {
            "id": "c-02",
            "name": "Career Two",
            "stream": "PCM",
            "education_level": "Undergraduate",
            "adjacent": ["c-01"],
            "scholarship_ids": ["s-01"],
        },
        {
            "id": "c-01",
            "name": "Career One",
            "stream": "PCM",
            "education_level": "Undergraduate",
            "adjacent": [],
            "scholarship_ids": [],
        },
    ]
    scholarships = [
        {"id": "s-01", "name": "Scholarship One", "education_level": "Undergraduate"}
    ]
    local_opps = [{"id": "lo-01", "city": "Bengaluru"}]
    demand = {"status": "ok", "entries": {}}
    questions = [{"id": "q-01", "text": "Question 1"}]

    _write_json(tmp_path / "careers.json", careers)
    _write_json(tmp_path / "scholarships.json", scholarships)
    _write_json(tmp_path / "local_opportunities.json", local_opps)
    _write_json(tmp_path / "demand_snapshot.json", demand)
    _write_json(tmp_path / "questions.json", questions)
    return tmp_path


def test_load_r2_data_success_and_indexes(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    _write_json(d / "id_map.json", {"c-01": "GGOCC-00001", "c-02": "GGOCC-00001"})

    bundle = load_r2_data(d)
    assert len(bundle.careers) == 2
    assert bundle.id_map["c-01"] == "GGOCC-00001"

    idx = R2Indexes(bundle)

    # Careers by ID
    assert list(idx.careers_by_id.keys()) == ["c-01", "c-02"]

    # Careers by Canonical ID
    assert "GGOCC-00001" in idx.careers_by_canonical_id
    assert [c["id"] for c in idx.careers_by_canonical_id["GGOCC-00001"]] == ["c-01", "c-02"]

    # Careers by Stream
    assert "PCM" in idx.careers_by_stream
    assert [c["id"] for c in idx.careers_by_stream["PCM"]] == ["c-01", "c-02"]

    # Careers by Education Level
    assert "Undergraduate" in idx.careers_by_education_level
    assert [c["id"] for c in idx.careers_by_education_level["Undergraduate"]] == ["c-01", "c-02"]

    # Scholarships by ID
    assert list(idx.scholarships_by_id.keys()) == ["s-01"]
    assert "Undergraduate" in idx.scholarships_by_education_level


def test_missing_required_file(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    os.remove(d / "careers.json")
    with pytest.raises(MissingFileError) as exc_info:
        load_r2_data(d)
    assert "careers.json" in str(exc_info.value)


def test_malformed_json(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    with open(d / "careers.json", "w", encoding="utf-8") as f:
        f.write("{invalid json")
    with pytest.raises(MalformedJSONError) as exc_info:
        load_r2_data(d)
    assert "careers.json" in str(exc_info.value)


def test_duplicate_career_ids(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    careers = [
        {"id": "c-01", "adjacent": [], "scholarship_ids": []},
        {"id": "c-01", "adjacent": [], "scholarship_ids": []},
    ]
    _write_json(d / "careers.json", careers)
    with pytest.raises(DuplicateIDError) as exc_info:
        load_r2_data(d)
    assert "c-01" in str(exc_info.value)


def test_dangling_adjacent_reference(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    careers = [
        {"id": "c-01", "adjacent": ["non-existent-career"], "scholarship_ids": []}
    ]
    _write_json(d / "careers.json", careers)
    with pytest.raises(DanglingReferenceError) as exc_info:
        load_r2_data(d)
    assert "non-existent-career" in str(exc_info.value)


def test_dangling_scholarship_reference(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    careers = [
        {"id": "c-01", "adjacent": [], "scholarship_ids": ["non-existent-scholarship"]}
    ]
    _write_json(d / "careers.json", careers)
    with pytest.raises(DanglingReferenceError) as exc_info:
        load_r2_data(d)
    assert "non-existent-scholarship" in str(exc_info.value)


def test_dangling_id_map_reference(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    _write_json(d / "id_map.json", {"unknown-r2-id": "GGOCC-99999"})
    with pytest.raises(DanglingReferenceError) as exc_info:
        load_r2_data(d)
    assert "unknown-r2-id" in str(exc_info.value)


def test_optional_id_map(tmp_path: Path):
    d = _create_minimal_r2_directory(tmp_path)
    if (d / "id_map.json").exists():
        os.remove(d / "id_map.json")
    bundle = load_r2_data(d)
    assert bundle.id_map == {}
