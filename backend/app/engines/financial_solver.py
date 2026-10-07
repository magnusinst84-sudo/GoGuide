def total_cost(tuition: float, living_costs: float, years: int, other_costs: float = 0.0) -> float:
    return (tuition + living_costs) * years + other_costs

def funding_need(total_cost: float, savings: float, annual_budget: float, years: int, scholarship: float) -> float:
    return max(0.0, total_cost - savings - (annual_budget * years) - scholarship)

def monthly_emi(principal: float, monthly_rate: float, months: int) -> float:
    if monthly_rate == 0:
        return principal / months if months > 0 else 0.0
    if months == 0:
        return 0.0
    return (principal * monthly_rate * ((1 + monthly_rate) ** months)) / (((1 + monthly_rate) ** months) - 1)

def affordability_ratio(emi: float, entry_salary: float) -> float:
    if entry_salary <= 0:
        return float('inf')
    return emi / entry_salary

def financial_feasibility(funding_need: float, loan_cap: float, affordability_ratio: float, max_ratio: float) -> dict:
    loan_exceeded = funding_need > loan_cap
    ratio_exceeded = affordability_ratio > max_ratio
    return {
        "is_feasible": not (loan_exceeded or ratio_exceeded),
        "loan_cap_exceeded": loan_exceeded,
        "emi_to_entry_salary_ratio": affordability_ratio,
        "status": "CALCULATED"
    }
