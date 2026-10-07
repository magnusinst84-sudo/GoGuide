# Backend Schema & API Contracts

This document defines the implementation contract for the GoGuide backend. It details JSON schemas for 22 core entities, API endpoints (planned vs. implemented), mathematical models for engines, and rules for recommendations and LLM training.

---

## 1. Core Schemas

Every schema distinguishes between user input, calculated fields, externally retrieved fields, and LLM-generated fields. Use explicit status values like `AVAILABLE`, `NOT_AVAILABLE`, `SYNTHETIC_PROTOTYPE`, `LIVE_SOURCE`, or `CALCULATED`. Do not invent fake values merely to satisfy schemas.

### 1. StudentProfile
```json
{
  "student_id": "uuid",
  "interests": ["coding", "design"],
  "aptitude_score": 85.5,
  "education_preference": "B.Tech",
  "location_preference": "AVAILABLE",
  "skills_self_reported": ["Python", "Figma"]
}
```

### 2. ParentProfile
```json
{
  "parent_id": "uuid",
  "student_id": "uuid",
  "preferred_career_directions": ["Engineering", "Medicine"],
  "affordability_expectation_max": 2000000,
  "location_preference": "NOT_AVAILABLE",
  "priorities": ["job security", "ROI"]
}
```

### 3. FinancialProfile
```json
{
  "profile_id": "uuid",
  "annual_family_budget": 500000,
  "total_savings": 1000000,
  "loan_willingness": true,
  "scholarship_awareness": "AVAILABLE"
}
```

### 4. PreferenceProfile
```json
{
  "profile_id": "uuid",
  "career_cluster_weights": {"Tech": 0.8, "Healthcare": 0.2},
  "risk_tolerance": 0.5
}
```

### 5. StudentAssessment
```json
{
  "assessment_id": "uuid",
  "student_id": "uuid",
  "personality_dimensions": {"openness": 0.7},
  "academic_history": {"12th_percentage": 92.0}
}
```

### 6. Recommendation
```json
{
  "recommendation_id": "uuid",
  "student_id": "uuid",
  "occupation_id": "O-1234",
  "final_score": 0.89,
  "rank": 1,
  "status": "RANKABLE",
  "evidence": {} 
}
```

### 7. RecommendationEvidence
```json
{
  "evidence_count": 3,
  "market_opportunity_available": "AVAILABLE",
  "progression_available": "NOT_AVAILABLE"
}
```

### 8. Career
```json
{
  "occupation_id": "O-1234",
  "title": "Software Developer",
  "description": "Develops applications...",
  "cluster": "Information Technology"
}
```

### 9. CareerSkill
```json
{
  "occupation_id": "O-1234",
  "skill_name": "Python",
  "importance": 0.9,
  "type": "hard_skill"
}
```

### 10. SkillGap
```json
{
  "student_id": "uuid",
  "occupation_id": "O-1234",
  "missing_skills": ["Java", "System Design"],
  "status": "CALCULATED"
}
```

### 11. EducationPathway
```json
{
  "pathway_id": "P-1",
  "occupation_id": "O-1234",
  "degrees_required": ["B.Tech", "B.Sc CS"],
  "common_exams": ["JEE"]
}
```

### 12. FinancialCalculation
```json
{
  "student_id": "uuid",
  "total_cost": 1500000,
  "funding_need": 500000,
  "emi": 12000,
  "status": "CALCULATED"
}
```

### 13. FinancialFeasibility
```json
{
  "is_feasible": true,
  "loan_cap_exceeded": false,
  "emi_to_entry_salary_ratio": 0.15,
  "status": "CALCULATED"
}
```

### 14. ConflictAnalysis
```json
{
  "student_id": "uuid",
  "parent_id": "uuid",
  "alignment_score": 0.82,
  "conflict_areas": ["Location", "Affordability"],
  "status": "CALCULATED"
}
```

### 15. WhatIfScenario
```json
{
  "scenario_id": "uuid",
  "adjusted_budget": 600000,
  "adjusted_location": "Delhi",
  "resulting_recommendations": []
}
```

### 16. MarketEvidence
```json
{
  "occupation_id": "O-1234",
  "posting_count": 1500,
  "source_type": "REAL_JOB_FEED"
}
```

### 17. LiveWebSource
```json
{
  "source_url": "https://api.example.com/fees",
  "retrieved_at": "2026-10-07T12:00:00Z",
  "data_type": "college_fees",
  "status": "LIVE_SOURCE"
}
```

### 18. ActionPlan
```json
{
  "student_id": "uuid",
  "recommended_direction": "Software Engineering",
  "skills_to_build": ["Python", "Data Structures"],
  "financial_next_steps": ["Apply for XYZ Scholarship"],
  "llm_generated_summary": "Based on your strong aptitude in math..."
}
```

### 19. LLMContext
```json
{
  "student_profile": {},
  "financial_feasibility": {},
  "recommendations": [],
  "skill_gaps": []
}
```

### 20. LLMRequest
```json
{
  "prompt": "Explain why Software Engineering is a good fit.",
  "context": {}
}
```

### 21. LLMResponse
```json
{
  "response_text": "Software Engineering aligns with your high math aptitude...",
  "generated_at": "2026-10-07T12:05:00Z"
}
```

### 22. APIError
```json
{
  "error_code": "NOT_FOUND",
  "message": "Occupation O-9999 not found.",
  "details": {}
}
```

---

## 2. API Contracts

**IMPLEMENTED:**
- `GET /health`

**PLANNED:**
- `POST /api/students/profile`
- `POST /api/recommendations`
- `GET /api/recommendations/{student_id}`
- `GET /api/careers`
- `GET /api/careers/{occupation_id}`
- `POST /api/financial/solver`
- `POST /api/conflict`
- `POST /api/skills/analyze`
- `GET /api/pathways/{occupation_id}`
- `POST /api/what-if`
- `POST /api/action-plan`
- `POST /api/llm/chat`
- `POST /api/live-search`

---

## 3. Financial Model

Use deterministic calculations:

**Total Cost:**
`TC = (Tuition + Living Costs) × Years + Coaching/Other Costs`

**Funding Need:**
`Need = max(0, TC - Savings - Annual Budget × Years - Scholarship)`

**EMI:**
`EMI = P × r × (1+r)^n / ((1+r)^n - 1)`
*(P = loan principal, r = monthly interest rate, n = number of monthly payments)*

Feasibility must consider loan caps, EMI affordability, and entry salary when available. Do not invent missing values.

---

## 4. Conflict Model

Where comparable vectors exist, use preference-alignment modeling:

`Conflict(c) = min(1, |cos(student,c) - cos(parent,c)|)`

Overall preference alignment (CI):
`CI = 1 - cos(student,parent)`

**Important:** Clearly label this as a preference-alignment metric. Do not call it a psychological diagnosis.

---

## 5. Recommendation Rules

- Recommendations originate strictly from deterministic backend logic.
- Use validated Phase 7.2 data.
- Require sufficient evidence (MIN_FACTORS = 2).
- Preserve provenance.
- Distinguish real/live vs synthetic evidence explicitly.
- **Never fabricate missing factors.** The frontend renders results; the LLM explains them.

---

## 6. LLM Training Rules

- The model should **NOT** simply be trained on raw CSV files.
- The training corpus should eventually contain curated instruction/response examples across guidance, finances, skills, pathways, and action plans.
- **Raw PII must never enter the corpus.**
- Synthetic data must remain explicitly labelled.
- The LLM must learn to use supplied evidence context rather than memorize volatile facts.
