from backend.app.data.loaders import load_r2_data
from backend.app.data.indexes import R2Indexes
from backend.app.data.repositories.scholarship_repository import ScholarshipRepository


def test_scholarship_repository_known_id():
    bundle = load_r2_data("data/r2")
    indexes = R2Indexes(bundle)
    repo = ScholarshipRepository(indexes)

    res = repo.get_scholarship("pm-csss")
    assert res.found is True
    assert res.scholarship is not None
    assert res.scholarship.id == "pm-csss"
    assert res.scholarship.income_cap_annual == 450000


def test_scholarship_repository_unknown_id():
    bundle = load_r2_data("data/r2")
    indexes = R2Indexes(bundle)
    repo = ScholarshipRepository(indexes)

    res = repo.get_scholarship("unknown-scholarship-id")
    assert res.found is False
    assert res.scholarship is None


def test_scholarship_repository_list():
    bundle = load_r2_data("data/r2")
    indexes = R2Indexes(bundle)
    repo = ScholarshipRepository(indexes)

    scholarships = repo.list_scholarships()
    assert len(scholarships) == 5
    ids = [s.id for s in scholarships]
    assert "aicte-pragati" in ids
    assert "aicte-saksham" in ids
