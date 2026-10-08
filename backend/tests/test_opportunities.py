from backend.app.data.loaders import load_r2_data
from backend.app.data.repositories.opportunity_repository import LocalOpportunityRepository


def test_opportunity_repository_list():
    bundle = load_r2_data("data/r2")
    repo = LocalOpportunityRepository(bundle)

    opps = repo.list_opportunities()
    assert len(opps) == 6

    bengaluru_opps = repo.list_opportunities(city="Bengaluru")
    assert len(bengaluru_opps) > 0
    assert all(o.city.lower() == "bengaluru" for o in bengaluru_opps)


def test_opportunity_repository_get_by_id():
    bundle = load_r2_data("data/r2")
    repo = LocalOpportunityRepository(bundle)

    res = repo.get_opportunity("blr-water-tanker")
    assert res.found is True
    assert res.opportunity is not None
    assert res.opportunity.city == "Bengaluru"

    res_unknown = repo.get_opportunity("unknown-opp-id")
    assert res_unknown.found is False
