"""
GoGuide PRISM Engine - Phase 8 Product Integration Blueprint Generator
"""

import os
import json
from datetime import datetime

ROOT_DIR = r'C:\Users\TANMAY\Desktop\PROJECT\DataQuest'
REPORTS_DIR = os.path.join(ROOT_DIR, 'data', 'reports')

BLUEPRINT_MD = os.path.join(REPORTS_DIR, 'phase_8_product_blueprint.md')
BLUEPRINT_JSON = os.path.join(REPORTS_DIR, 'phase_8_product_blueprint.json')

def build_phase8_blueprint():
    timestamp = datetime.now().isoformat()
    
    # JSON Data Structure
    blueprint_json = {
        "blueprint_metadata": {
            "title": "GoGuide PRISM Engine - Phase 8 Product Integration Blueprint",
            "project": "DataQuest 3.0 (Problem Statement: DQNM)",
            "timestamp": timestamp,
            "status": "APPROVED_SPECIFICATION",
            "phase": "Phase 8 — Product Integration Blueprint"
        },
        "executive_summary": {
            "vision": "A multi-stakeholder, transparent, rule-based career guidance web application enabling students and parents to evaluate STEAM career paths together with financial feasibility gates, explicit conflict measurement, and deterministic score explainability.",
            "core_principles": [
                "Zero data fabrication or black-box ML scoring.",
                "100% auditable scores backed by explicit CSV crosswalks and graph edges.",
                "Hard financial feasibility gate (Pass/Fail) based on rupee cost, loan EMI, and entry salary.",
                "Explicit parent-student conflict calculation without speculative psychological claims.",
                "Strict evidence labeling (SYNTHETIC_PROTOTYPE vs REAL_JOB_FEED)."
            ]
        },
        "product_architecture": {
            "frontend_stack": "Next.js 14+ (App Router), TypeScript, Tailwind CSS, SVG visualization charts.",
            "backend_stack": "FastAPI (Python 3.11+), Pydantic v2 data models, NumPy for vector math.",
            "storage_strategy": "Zero database required for hackathon MVP. In-memory pandas/CSV dataset indexing directly from data/processed/ and data/crosswalks/.",
            "auth_strategy": "Firebase Auth (Google Sign-In) + Lightweight local demo profile runner."
        },
        "user_journey_screens": [
            {
                "step": 1,
                "screen_name": "Landing & Mode Selection",
                "purpose": "Introduce GoGuide PRISM Engine and allow quick demo profile selection or direct student/parent evaluation start.",
                "key_components": ["Hero header", "Interactive demo profile launcher ('Load Demo Pair')", "Role entry buttons (Student / Parent)"]
            },
            {
                "step": 2,
                "screen_name": "Student Assessment Form",
                "purpose": "Capture student academic stream, RIASEC interest profile (24 Likert items), self-reported skill ratings, and target career preference.",
                "key_components": ["Academic Stream selector", "24-item RIASEC Likert questionnaire (1-5)", "8 core skill self-ratings", "Target career cluster picker"]
            },
            {
                "step": 3,
                "screen_name": "Parent Input Form",
                "purpose": "Capture parent target career expectations, risk tolerance, early employment necessity, and explicit consent.",
                "key_components": ["Top 3-5 expected career choices", "Risk tolerance slider (1-5)", "Need for early employment slider (1-5)", "Parental consent checkbox"]
            },
            {
                "step": 4,
                "screen_name": "Financial Profile & Constraints",
                "purpose": "Capture household financial parameters to enforce the hard affordability feasibility gate.",
                "key_components": ["Annual education budget (₹)", "Available liquid savings (₹)", "Maximum loan cap tolerance (₹)", "Target location/city"]
            },
            {
                "step": 5,
                "screen_name": "Parent-Student Conflict Analysis",
                "purpose": "Display transparent vector distance, per-career alignment gap, risk disagreement, and surface compromise paths.",
                "key_components": ["Overall Conflict Index gauge", "Student vs Parent Interest Vector radar/bar chart", "Risk disparity indicator", "Surfaced compromise career card"]
            },
            {
                "step": 6,
                "screen_name": "Career Recommendations Dashboard",
                "purpose": "Present ranked feasible careers with composite match scores, component score breakdowns, and blocked careers.",
                "key_components": ["Ranked Career Cards", "Component Score Breakdown (Fit, Market, Financial, Risk)", "Feasibility status badge (FEASIBLE / BLOCKED)", "Interactive Weight Sliders"]
            },
            {
                "step": 7,
                "screen_name": "Career Detail & Pathway View",
                "purpose": "Deep dive into selected career requirements, education pathways, skill expectations, and market signals.",
                "key_components": ["Education path badge (DIRECT_PATH / RELATED_PATH)", "Target occupation required skills", "Market demand tag (SYNTHETIC_PROTOTYPE)", "Career progression trajectory tree"]
            },
            {
                "step": 8,
                "screen_name": "Financial Feasibility & Solver",
                "purpose": "Detailed financial breakdown including tuition/living cost, estimated loan EMI, shortfall ₹, and alternative low-cost pathways.",
                "key_components": ["5-Year Total Cost of Education (TC)", "Estimated Loan Amount & Monthly EMI", "EMI-to-Entry-Salary Ratio (%)", "Alternative Path Cost comparison table"]
            },
            {
                "step": 9,
                "screen_name": "What-If Simulator",
                "purpose": "Interactive sandbox allowing real-time parameter tweaking and immediate visual feedback on ranking and feasibility.",
                "key_components": ["Budget & Loan Sliders", "Salary Expectation adjustment", "Location picker", "Factor Weight Sliders", "Real-time re-ranked list"]
            },
            {
                "step": 10,
                "screen_name": "Final Action Plan & Roadmap",
                "purpose": "Consolidated actionable roadmap for the chosen career path including milestone targets, exams, and local innovation ideas.",
                "key_components": ["Phased timeline (0-3m, 3-6m, 6-12m)", "Relevant entrance exams & scholarships", "Hyper-local STEAM project card", "Downloadable Action Plan PDF/Summary"]
            }
        ],
        "core_formulas_and_inputs": {
            "feasibility_gate": {
                "formula": "G(c) = 1 if (Need <= Loan_Cap AND EMI / Entry_Salary <= 0.40) else 0",
                "inputs": ["Tuition Cost", "Living Cost", "Liquid Savings", "Annual Budget", "Loan Cap", "Entry Salary"],
                "policy": "Hard pass/fail gate. Blocked careers are removed from main ranking and shown in Blocked List with exact ₹ shortfall."
            },
            "parent_student_conflict": {
                "formula": "Conflict(c) = min(1, |cos(s, c) - cos(p, c)|); Overall CI = 1 - cos(s, p)",
                "inputs": ["Student RIASEC Vector (s)", "Parent Expected Vector (p)", "Career Vector (c)"],
                "policy": "Derived purely from explicit preference vector distance. Zero psychological or speculative claims."
            },
            "composite_score": {
                "formula": "Score(c) = G(c) * (w_fit * Fit + w_market * Market + w_fin * Financial + w_risk * RiskCompat) - 0.20 * Conflict(c)",
                "inputs": ["Fit score", "Market score", "Financial score", "RiskCompat score", "Conflict score", "Weights"],
                "renormalization": "Missing factors (e.g. unobserved skill fit) are excluded and remaining factor weights sum to 1.0."
            },
            "skill_gap_policy": {
                "rule": "Distinguish Known Student Skills, Unobserved Student Evidence (NOT_AVAILABLE), and Occupation Required Skills.",
                "policy": "Never label occupation-required skills as student skill gaps when student skill evidence is missing."
            },
            "market_evidence_policy": {
                "rule": "Strictly label SYNTHETIC_PROTOTYPE vs REAL_JOB_FEED.",
                "policy": "Never call job posting counts 'hiring velocity'. Never claim future-proofing without explicit automation risk & growth index source data."
            }
        },
        "api_requirements": [
            {"endpoint": "GET /api/health", "method": "GET", "purpose": "Backend status and dataset registry health check."},
            {"endpoint": "POST /api/score", "method": "POST", "purpose": "Calculates real-time feasibility gate, vector scores, conflict index, and returns ranked careers with component breakdown."},
            {"endpoint": "GET /api/careers", "method": "GET", "purpose": "Retrieves career dictionary list for expected-careers picker."},
            {"endpoint": "GET /api/careers/{occupation_id}", "method": "GET", "purpose": "Retrieves detailed occupation metadata, required skills, education pathways, and market edges."},
            {"endpoint": "POST /api/financial/solver", "method": "POST", "purpose": "Evaluates financial shortfall, loan EMI, EMI-to-salary ratio, and compares alternative cost paths."},
            {"endpoint": "POST /api/conflict", "method": "POST", "purpose": "Computes student-parent vector distance, conflict index, and searches for optimal compromise paths."},
            {"endpoint": "GET /api/recommendations/student/{student_id}", "method": "GET", "purpose": "Queries pre-computed Phase 7 recommendation records from career_recommendations.csv."}
        ],
        "dataset_dependencies": {
            "student_features": "data/processed/student_intelligence/student_features.csv",
            "occupation_dictionary": "data/dictionaries/occupation_dictionary.csv",
            "education_dictionary": "data/dictionaries/education_dictionary.csv",
            "skill_dictionary": "data/dictionaries/skill_dictionary.csv",
            "education_occupation_edges": "data/crosswalks/education_occupation_edges.csv",
            "occupation_skill_edges": "data/crosswalks/occupation_skill_edges.csv",
            "occupation_market_edges": "data/crosswalks/occupation_market_edges.csv",
            "career_progression_edges": "data/crosswalks/career_progression_edges.csv",
            "career_recommendations": "data/processed/recommendations/career_recommendations.csv"
        },
        "external_data_requirements": [
            "Real-time college tuition fee updates & seat matrix (marked REQUIRES_EXTERNAL_LIVE_DATA)",
            "Live scholarship application deadlines (marked REQUIRES_EXTERNAL_LIVE_DATA)",
            "Bank education loan interest rate feeds (marked REQUIRES_EXTERNAL_LIVE_DATA)",
            "Live Adzuna job posting feeds for real-time city demand (marked REAL_JOB_FEED with SYNTHETIC_PROTOTYPE fallback)"
        ],
        "implementation_roadmap": {
            "p0_core_mvp": [
                "FastAPI scoring & financial solver endpoints",
                "Student Assessment & Parent Input Forms",
                "Financial Feasibility Gate execution",
                "Ranked Results Dashboard with score breakdowns & weight sliders",
                "Parent-Student Conflict Index display and compromise card"
            ],
            "p1_enhanced_features": [
                "Financial Feasibility Solver & alternative pathway comparison",
                "Interactive What-If Simulator",
                "Skill Requirements vs Student Self-Reported Skills breakdown",
                "Action Plan & Roadmap summary view"
            ],
            "p2_optional_features": [
                "Live Adzuna API proxy integration",
                "Leaflet interactive demand map",
                "LLM plain-language explanation wrapper with template fallback"
            ]
        }
    }

    with open(BLUEPRINT_JSON, 'w', encoding='utf-8') as jf:
        json.dump(blueprint_json, jf, indent=2)

    # Markdown Report Construction
    md_content = """# GoGuide PRISM Engine — Phase 8 Product Integration Blueprint

**Project:** PRISM Engine (GoGuide / DataQuest 3.0)  
**Problem Statement:** DQNM (Multi-Dimensional STEAM Career Guidance and Hyper-Local Innovation Platform)  
**Document Status:** `APPROVED PRODUCT SPECIFICATION`  
**Timestamp:** TIMESTAMP_PLACEHOLDER  

---

## Executive Summary

The **GoGuide PRISM Engine** product architecture translates the validated Phase 1–7 graph and transparent recommendation engine into a multi-stakeholder, interactive web application. Designed for students (ages 16–21) and parents/guardians, the application addresses the **DQNM problem statement** by combining student psychometric fit, hard parental financial feasibility gates, explicit conflict measurement, and local market intelligence into a single, fully auditable platform.

### Core Guiding Principles
1. **Zero Data Fabrication / ML Black-Box:** Recommendations and numbers on screen are 100% computed from deterministic rules, cited data files, and explicit crosswalks.
2. **Hard Feasibility Gate:** A career failing household financial limits (cost, loan cap, EMI ratio) is marked `BLOCKED` with exact ₹ shortfall details rather than being disguised under a lower score.
3. **Explicit Stakeholder Conflict:** Parent-student disagreement is measured transparently using centered vector distance—never speculative psychological claims.
4. **Honest Data Provenance:** All market signals are strictly labeled `SYNTHETIC_PROTOTYPE` or `REAL_JOB_FEED`. Job posting counts are never described as "hiring velocity".

---

## Product Architecture & Stack

```
                     +---------------------------------------+
                     | Next.js App Router (TypeScript, SVG) |
                     +-------------------+-------------------+
                                         |
                                  JSON / REST API
                                         v
                     +---------------------------------------+
                     |    FastAPI Backend (Python 3.11+)     |
                     | - /api/score    - /api/conflict       |
                     | - /api/careers  - /api/financial      |
                     +-------------------+-------------------+
                                         |
                       Direct In-Memory Pandas/CSV Lookup
                                         v
+-----------------------------------------------------------------------------------+
|                            GoGuide Cleaned Data Layer                             |
|  - student_features.csv            - occupation_dictionary.csv                   |
|  - education_occupation_edges.csv  - occupation_skill_edges.csv                    |
|  - occupation_market_edges.csv     - career_recommendations.csv                    |
+-----------------------------------------------------------------------------------+
```

- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, SVG progress/radar charts.
- **Backend:** Python FastAPI, Pydantic v2 schemas, NumPy for vector math.
- **Data Indexing:** Zero external database server required for hackathon MVP. In-memory indexing of CSV datasets from `data/processed/` and `data/crosswalks/`.

---

## User Journey & 10-Screen UI Flow

| Step | Screen | User Intent & Functional Requirements | Key UI Components |
|---|---|---|---|
| 1 | **Landing & Mode Selection** | Overview of GoGuide PRISM Engine; quick demo profile loading or direct entry start. | Hero section, "Load Demo Profile" button, Role entry triggers. |
| 2 | **Student Assessment Form** | Capture academic stream, 24 Likert RIASEC items, 8 skill self-ratings, and target career preference. | Stream picker, 24-item Likert slider, 8-skill self-ratings, Target cluster input. |
| 3 | **Parent Input Form** | Capture parent's expected career choices (3–5), risk appetite (1–5), early employment need, and consent. | Expected career picker, Risk slider, Early employment slider, Mandatory consent checkbox. |
| 4 | **Financial Profile & Constraints** | Capture annual education budget, liquid savings, loan cap, and target location. | Household budget inputs (₹), Savings input (₹), Loan cap slider (₹), City selector. |
| 5 | **Parent-Student Conflict Analysis** | Transparently present overall conflict index, vector alignment, risk disparity, and compromise path. | Conflict Index gauge (0–100), Vector overlay radar chart, Surfaced Compromise Career card. |
| 6 | **Career Recommendations** | Display ranked feasible careers, score breakdowns, blocked careers list, and live weight sliders. | Ranked Career Cards, Component score bars (Fit, Market, Financial, Risk), Blocked List, Weight Sliders. |
| 7 | **Career Detail & Pathway** | Inspect required education path (`DIRECT_PATH`), target skills, market status, and progression tree. | Education path badge, Target occupation skills, Market tag (`SYNTHETIC_PROTOTYPE`), Progression tree. |
| 8 | **Financial Feasibility & Solver** | Analyze 5-year total cost, loan requirement, monthly EMI, and lower-cost alternative education pathways. | 5-Year Cost Breakdown, Estimated EMI & EMI/Salary ratio, Alternative Path cost comparison table. |
| 9 | **What-If Simulator** | Interactive sandbox to test scenario variations (budget, loan, salary, weights) with instant re-ranking. | Budget & Loan Sliders, Salary adjustment, Weight Sliders, Real-time re-ranked candidate list. |
| 10 | **Final Action Plan & Roadmap** | Actionable execution roadmap including timeline milestones, exams, scholarships, and local project card. | Phased timeline (0–3m, 3–6m, 6–12m), Exam/Scholarship schedule, Local STEAM project card, Export PDF button. |

---

## Mandatory Product Formulas & Rules

### 1. Financial Feasibility Gate (Pass/Fail)
TC = (Tuition + Living) * Years + Coaching
Funding Need = max(0, TC - Savings - Annual_Budget * Years - Scholarship)
EMI = (Need * r * (1+r)^n) / ((1+r)^n - 1)   where r = rate/12, n = tenure_years * 12
Gate G(c) = 1 if (Need <= Loan_Cap AND EMI / Entry_Salary <= 0.40) else 0 (BLOCKED)

### 2. Parent-Student Conflict Index
Conflict(c) = min(1, |cos(s, c) - cos(p, c)|)
Overall Conflict Index (CI) = 1 - cos(s, p)
Compromise Career = argmax over Feasible of min(cos(s, c), cos(p, c))  (floor 0.40)
Note: Measured purely via centered vector cosine distance. No speculative psychological claims.

### 3. Skill Gap & Learning Path Policy
- **Known Student Skills:** Self-reported by student in assessment form.
- **Unobserved Student Skills:** Labeled explicitly as `NOT_AVAILABLE`.
- **Occupation Required Skills:** Mapped directly from ESCO/O*NET crosswalks (`occupation_skill_edges.csv`).
- *Policy:* Occupation required skills are **never** described as student skill gaps when student evidence is unobserved.

### 4. Financial Constraint Solver
- Solves: Total 5-Year Cost, Funding Shortfall, Estimated Monthly EMI, EMI-to-Salary Ratio.
- Compares: High-cost private options vs. lower-cost state/central university pathways.
- Missing live values (exact college fees, live bank loan rates) are explicitly tagged `REQUIRES_EXTERNAL_LIVE_DATA`.

---

## Backend REST API Requirements

| Endpoint | Method | Input Parameters | Return Output & Purpose |
|---|---|---|---|
| `/api/health` | `GET` | None | Engine status, dictionary registry item counts. |
| `/api/score` | `POST` | Student answers, Parent answers, Financial limits, Weights | Feasibility gate status, composite match scores, component breakdown, blocked list. |
| `/api/careers` | `GET` | Search query, stream filter | List of canonical careers from `occupation_dictionary.csv`. |
| `/api/careers/{id}` | `GET` | `occupation_id` | Full occupation metadata, required skills, education pathways, market edges. |
| `/api/financial/solver` | `POST` | Career ID, Tuition, Living, Savings, Budget, Loan Cap | Financial shortfall, EMI, EMI/Salary ratio, alternative low-cost education paths. |
| `/api/conflict` | `POST` | Student RIASEC vector, Parent expected careers | Conflict Index, radar vector alignment, compromise career recommendation. |
| `/api/recommendations/student/{id}` | `GET` | `student_id` | Pre-computed Phase 7 career recommendations from `career_recommendations.csv`. |

---

## Dataset Artifact Dependencies

1. **Student Intelligence:** `data/processed/student_intelligence/student_features.csv`
2. **Canonical Dictionaries:**
   - `data/dictionaries/occupation_dictionary.csv`
   - `data/dictionaries/education_dictionary.csv`
   - `data/dictionaries/skill_dictionary.csv`
3. **Graph Edges & Crosswalks:**
   - `data/crosswalks/education_occupation_edges.csv`
   - `data/crosswalks/occupation_skill_edges.csv`
   - `data/crosswalks/occupation_market_edges.csv`
   - `data/crosswalks/career_progression_edges.csv`
4. **Pre-computed Recommendations:** `data/processed/recommendations/career_recommendations.csv`

---

## Implementation Roadmap for Hackathon Build

### P0 — Core Minimum Viable Product (Must-Have)
- FastAPI scoring service & financial feasibility gate.
- Student Assessment & Parent Input Forms with parental consent.
- Ranked Recommendations Dashboard with component score bars and real-time weight sliders.
- Parent-Student Conflict Index display and compromise card.

### P1 — Enhanced Product Features (High Priority)
- Financial Constraint Solver & alternative low-cost education pathway comparison.
- Interactive What-If Simulator sandbox.
- Skill Requirements vs Student Self-Reported Skills breakdown.
- Action Plan & Roadmap summary view.

### P2 — Optional / Polish Features (If Time Permits)
- Live Adzuna API proxy for real-time job counts.
- Interactive Leaflet demand map by city.
- LLM plain-language explanation wrapper with template fallback.
""".replace("TIMESTAMP_PLACEHOLDER", timestamp)

    with open(BLUEPRINT_MD, 'w', encoding='utf-8') as mf:
        mf.write(md_content)

    print(f"Blueprint generated successfully:\n- {BLUEPRINT_MD}\n- {BLUEPRINT_JSON}")

if __name__ == '__main__':
    build_phase8_blueprint()
