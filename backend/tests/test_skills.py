from backend.app.data.repositories.skill_repository import SkillRepository


def test_skill_repository_known_occupation():
    repo = SkillRepository()
    skills = repo.get_required_skills("GGOCC-00176")
    assert isinstance(skills, list)
    if skills:
        assert hasattr(skills[0], "skill_id")
        assert hasattr(skills[0], "skill_name")


def test_skill_repository_unknown_occupation():
    repo = SkillRepository()
    skills = repo.get_required_skills("UNKNOWN-OCCUPATION-999")
    assert skills == []


def test_skill_repository_normalize_skill():
    repo = SkillRepository()
    normalized = repo.normalize_skill("python")
    assert normalized is not None
