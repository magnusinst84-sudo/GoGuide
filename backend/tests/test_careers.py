import json
import os
from pathlib import Path
import pytest

from backend.app.data.loaders import (
    DuplicateIDError,
    MalformedJSONError,
    load_r2_data,
)
from backend.app.data.indexes import R2Indexes
from backend.app.data.repositories.career_repository import CareerRepository
from backend.app.data.repositories.education_repository import EducationRepository


def _write_json(path: Path, data: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _create_test_r2_directory(tmp_path: Path) -> Path:
    careers = [
        {
            "id": "btech-cse-govt",
            "name": "B.Tech Computer Science (government college)",
            "stream": "PCM",
            "education_level": "Undergraduate",
            "tuition_per_year": 50000,
            "salary": {"y1": 600000},
            "adjacent": ["polytechnic-diploma-engg"],
            "scholarship_ids": ["pm-csss"],
            "sources": {"_note": "Verified govt stats"},
            "estimated_fields": ["stub"],
        },
        {
            "id": "b-des-ux",
            "name": "B.Des / UX Design",
            "stream": "Design",
            "education_level": "Undergraduate",
            "tuition_per_year": 200000,
            "salary": {"y1": 400000},
            "adjacent": [],
            "scholarship_ids": [],
            "sources": {"_note": "Placeholder values; not sourced."},
            "estimated_fields": ["stub", "tuition_per_year"],
        },
        {
            "id": "polytechnic-diploma-engg",
            "name": "Diploma in Engineering (polytechnic)",
            "stream": "PCM",
            "education_level": "Diploma",
            "tuition_per_year": 15000,
            "salary": {"y1": 250000},
            "adjacent": ["btech-cse-govt"],
            "scholarship_ids": [],
            "sources": {"_note": "State diploma portal"},
            "estimated_fields": ["stub"],
        },
    ]
    scholarships = [{"id": "pm-csss", "name": "PM-CSSS", "education_level": "Undergraduate"}]
    local_opps = [{"id": "lo-01", "city": "Bengaluru"}]
    demand = {"status": "ok", "entries": {}}
    questions = [{"id": "q-01", "text": "Question 1"}]

    _write_json(tmp_path / "careers.json", careers)
    _write_json(tmp_path / "scholarships.json", scholarships)
    _write_json(tmp_path / "local_opportunities.json", local_opps)
    _write_json(tmp_path / "demand_snapshot.json", demand)
    _write_json(tmp_path / "questions.json", questions)
    return tmp_path


def test_get_career_known_id(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    repo = CareerRepository(indexes)

    res = repo.get_career("btech-cse-govt")
    assert res.found is True
    assert res.career is not None
    assert res.career.id == "btech-cse-govt"
    assert res.career.name == "B.Tech Computer Science (government college)"
    assert res.career.placeholder is False
    assert res.career.sources["_note"] == "Verified govt stats"
    assert res.career.estimated_fields == ["stub"]


def test_get_career_unknown_id(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    repo = CareerRepository(indexes)

    res = repo.get_career("non-existent-id")
    assert res.found is False
    assert res.career is None
    assert "not found" in res.message.lower()


def test_list_careers_empty_filter(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    repo = CareerRepository(indexes)

    careers = repo.list_careers({})
    ids = [c.id for c in careers]
    assert ids == ["btech-cse-govt", "polytechnic-diploma-engg"]
    assert "b-des-ux" not in ids


def test_duplicate_id_handling(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    careers = [
        {"id": "c-01", "name": "C1", "adjacent": [], "scholarship_ids": []},
        {"id": "c-01", "name": "C1 Duplicate", "adjacent": [], "scholarship_ids": []},
    ]
    _write_json(d / "careers.json", careers)
    with pytest.raises(DuplicateIDError):
        load_r2_data(d)


def test_malformed_record_handling(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    careers = [{"id": "c-malformed", "adjacent": [], "scholarship_ids": []}]
    _write_json(d / "careers.json", careers)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    with pytest.raises(MalformedJSONError) as exc_info:
        CareerRepository(indexes)
    assert "missing required 'name' field" in str(exc_info.value)


def test_placeholder_exclusion_and_inclusion(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    repo = CareerRepository(indexes)

    res = repo.get_career("b-des-ux")
    assert res.found is True
    assert res.career.placeholder is True

    default_list = repo.list_careers()
    assert "b-des-ux" not in [c.id for c in default_list]

    with_ph = repo.list_careers(include_placeholder=True)
    assert "b-des-ux" in [c.id for c in with_ph]


def test_get_adjacent(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    repo = CareerRepository(indexes)

    adj = repo.get_adjacent("btech-cse-govt")
    assert len(adj) == 1
    assert adj[0].id == "polytechnic-diploma-engg"


def test_education_repository_equivalents(tmp_path: Path):
    d = _create_test_r2_directory(tmp_path)
    bundle = load_r2_data(d)
    indexes = R2Indexes(bundle)
    career_repo = CareerRepository(indexes)
    edu_repo = EducationRepository(career_repo)

    res = edu_repo.get_education("btech-cse-govt")
    assert res.found is True
    assert res.program is not None
    assert res.program.id == "btech-cse-govt"

    list_edu = edu_repo.list_education()
    assert len(list_edu) == 2

    adj_edu = edu_repo.get_adjacent("btech-cse-govt")
    assert len(adj_edu) == 1
    assert adj_edu[0].id == "polytechnic-diploma-engg"
