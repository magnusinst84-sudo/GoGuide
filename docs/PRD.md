# Product Requirements Document (PRD)

## 1. Product Overview
GoGuide is an AI-assisted career and education decision-support platform designed for students and families. It integrates student preferences, parent expectations, deterministic financial solvers, validated career data, and an LLM-powered conversational interface to guide critical life choices.

## 2. Problem
Students and parents must make career and education decisions across a complex landscape of variables:
- Student aptitude, interests, and preferences
- Education options and pathways
- Current and future skills
- Affordability and financial constraints
- Parent expectations
- Job-market uncertainty
- Future career changes

Currently, this process is fragmented, heavily biased, and often ignores the intersection of financial feasibility and student-parent alignment.

## 3. Product Goals
- Improve career decision quality through data-driven recommendations.
- Expose realistic, canonical education pathways.
- Account for financial constraints explicitly.
- Surface student-parent preference differences in a constructive manner.
- Identify current skills and tangible gaps relative to target careers.
- Provide alternative paths for resilience.
- Use current information (live web retrieval) where required.
- Provide actionable, sequential plans.

## 4. Non-goals
GoGuide is explicitly **not**:
- A guaranteed career predictor or crystal ball.
- An admissions authority or application portal.
- A financial institution or lender.
- A replacement for professional financial advice.
- A psychological diagnostic tool or clinical assessment.
- A job-placement guarantee.

## 5. Users
**Primary:**
- Students
- Parents/Guardians

**Secondary:**
- Counselors/Mentors

## 6. Core Features

### Student Assessment
Inputs should support:
- Interests and preferences
- Aptitude
- Personality-style dimensions (where available)
- Academic information
- Education preference
- Location preference
- Self-reported skills
- Financial constraints

### Parent Input
Capture:
- Preferred career directions
- Education preferences
- Affordability expectations
- Location preferences
- Concerns/priorities

### Recommendation Engine
- Use the validated Phase 7.2 engine (deterministic, evidence-gated, provenance-preserving).
- **Do not** rebuild this logic in the frontend. It operates strictly on the backend.

### Conflict Engine
- Represent student-parent preference alignment using vectors.
- Use "preference-alignment" language.
- **Do not** describe it as a psychological diagnosis.

### Financial Solver
Deterministic calculations supporting:
- Total cost
- Savings
- Annual family budget
- Scholarship
- Funding gap
- Loan requirement
- EMI
- Loan-cap feasibility
- EMI-to-entry-salary ratio

### Skill Engine
- Compare student/self-reported skills against canonical occupation-required skills.
- **Do not** claim missing skills are confirmed deficiencies when student evidence is simply unavailable.

### Live Information
- Retrieve current external information only when required (e.g., current fees, live job counts).

### What-If Simulator
Allow users to change variables and recalculate deterministic outputs dynamically:
- Budget, scholarship, loan assumptions
- Education option
- Career
- Location
- Preference weights

### Action Plan
Produce a grounded plan:
- Recommended direction
- Education path
- Skills to build
- Learning sequence
- Financial next steps
- Application/research tasks
- Alternative paths
- *LLM Note*: The LLM may generate wording, but all facts must originate from backend context.

## 7. MVP Priorities

**P0 (Core Journey):**
- Profile collection (Student/Parent)
- Recommendations (Phase 7.2 Engine)
- Financial solver
- Conflict analysis
- Career details
- Basic skill analysis

**P1 (Enhancement & Synthesis):**
- Live web retrieval
- What-if simulator
- Alternative pathways
- Action plan generation
- Conversational LLM assistant

**P2 (Future):**
- Advanced market intelligence
- Richer integrations (e.g., direct scholarship APIs)
- Counselor workflows and dashboards

## 8. Success Criteria
- **Completion Rate**: High percentage of users completing the core profile collection and reaching the recommendation view.
- **Alignment Resolution**: Users utilizing the What-If Simulator or Assistant to close the gap in the Conflict Engine metrics.
- **Actionability**: High percentage of users downloading or saving the Final Action Plan.
- **System Integrity**: Zero occurrences of LLM hallucination regarding financial calculations or recommendation scores (measured via backend logging and grounding audits).
