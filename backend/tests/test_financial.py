from app.engines.financial_solver import total_cost, funding_need, monthly_emi, affordability_ratio, financial_feasibility

def test_total_cost():
    assert total_cost(100, 50, 4, 20) == 620

def test_funding_need():
    assert funding_need(1000, 200, 100, 4, 100) == 300
    assert funding_need(500, 600, 100, 4, 100) == 0

def test_monthly_emi():
    assert abs(monthly_emi(100000, 0.01, 12) - 8884.8788) < 0.1

def test_affordability_ratio():
    assert affordability_ratio(1000, 10000) == 0.1
    assert affordability_ratio(1000, 0) == float('inf')

def test_financial_feasibility():
    res = financial_feasibility(50000, 100000, 0.2, 0.3)
    assert res['is_feasible'] == True
    
    res = financial_feasibility(150000, 100000, 0.2, 0.3)
    assert res['is_feasible'] == False
    assert res['loan_cap_exceeded'] == True
