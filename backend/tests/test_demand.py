from backend.app.data.loaders import load_r2_data
from backend.app.data.repositories.demand_repository import DemandRepository


def test_demand_repository_get_snapshot():
    bundle = load_r2_data("data/r2")
    repo = DemandRepository(bundle)

    snapshot = repo.get_demand_snapshot()
    assert snapshot is not None
    assert snapshot.status == "placeholder"
    assert snapshot.entries == {}
