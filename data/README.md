# PRISM Engine Data Intelligence Layer (DataQuest 3.0)

Welcome to the data intelligence repository for **PRISM** (DataQuest 3.0, DQNM), an AI-powered education-to-career pathway guidance and recommendation engine for students.

This repository houses clean, machine-readable datasets spanning synthetic pathway graphs, international occupation taxonomies (ESCO, O*NET SOC), Indian job market hiring benchmarks, global job posting corpora, anonymized resume transition histories, and student psychometric/academic performance profiles.

---

## Data Domain Index

| Domain Directory | Purpose in PRISM Engine | File Count | Total Rows | Disk Size | Primary Standards & Data Source |
|---|---|---|---|---|---|
| [`prism_education_career/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_education_career/README.md) | Core synthetic pathway graph (Degree → Occupation → Skill → Industry → Progression) | 8 | 9,521 | 2.32 MB | PRISM Validated Synthetic Graph |
| [`prism_esco/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_esco/README.md) | Official European ESCO v1.2 taxonomy (occupations, skills, digital/green collections) | 19 | 181,562 | 49.39 MB | European Commission ESCO v1.2 (CC BY 4.0) |
| [`prism_india_jobs/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_india_jobs/README.md) | Indian labor-market hiring benchmarks (salaries in INR LPA, skills, city tiers) | 1 | 5,000 | 0.89 MB | Indian Hiring Benchmark Model (2024–2026) |
| [`prism_job_descriptions/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_job_descriptions/README.md) | Unstructured/structured job vacancy listings & role descriptions for NLP extraction | 3 | 19,486 | 18.09 MB | Adzuna Global Feed + Role Corpus (2025) |
| [`prism_occupation_intelligence/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_occupation_intelligence/README.md) | O*NET SOC task structures + USPTO patent classification demand indices | 8 | 3,033,707 | 71.74 MB | O*NET 28.0 + USPTO Patent Database (2010–2023) |
| [`prism_resume_intelligence/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_resume_intelligence/README.md) | Anonymized real-world resume experience, education, and skill co-occurrence histories | 6 | 4,325,945 | 129.68 MB | Kaggle 54K Resume Dataset (Anonymized) |
| [`prism_student_profile/`](file:///c:/Users/TANMAY/Desktop/PROJECT/DataQuest/data/prism_student_profile/README.md) | Student psychometric profiles (OCEAN + 5 aptitudes) & academic performance records | 2 | 4,529 | 0.52 MB | Psychometric ML Corpus + PIP Academic Dataset |
| **TOTAL** | **Complete PRISM Data Intelligence Layer** | **47** | **7,579,750** | **272.63 MB** | **Multi-Source Unified Architecture** |

---

## PRISM Engine Architecture & Domain Interactions

```
                          ┌───────────────────────────────┐
                          │     prism_student_profile     │
                          │ (Psychometrics & Academic Rec)│
                          └───────────────┬───────────────┘
                                          │ Profile Matching
                                          ▼
┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│     prism_india_jobs      │──>│  prism_education_career   │<──│     prism_esco            │
│ (Salary LPA, City Hubs)   │   │ (Pathways, Degree->Career)│   │ (ESCO URIs, Green/Digital)│
└───────────────────────────┘   └─────────────┬─────────────┘   └───────────────────────────┘
                                              │ Graph Querying
                                              ▼
┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
│ prism_resume_intelligence │──>│  PRISM Guidance & Roadmap │<──│prism_occupation_intel.    │
│ (Real Transition Validation)│  │   Recommendation Engine   │   │ (USPTO Patent Task Trends)│
└───────────────────────────┘   └───────────────────────────┘   └───────────────────────────┘
```

### Domain Interconnections & Join Keys
1. **Degree → Career Pathway Querying:** `prism_student_profile` feeds user academic background into `prism_education_career/education_pathways.csv` via `degree_level` and `field_of_study`.
2. **Occupational Standard Bridges:** `prism_education_career/occupations.csv` joins:
   - `onet_soc_code` → `prism_occupation_intelligence/USPTO–ONET/onet_occupations.csv.soc_code`
   - `esco_occupation_uri` → `prism_esco/occupations_en.csv.conceptUri`
3. **Skill Normalization & Gap Analysis:** `prism_education_career/skills.csv` joins:
   - `esco_skill_uri` → `prism_esco/skills_en.csv.conceptUri`
   - `skill_name` → `prism_india_jobs/india_job_market_2024_2026.csv.Skills_Required`
   - `skill_name` → `prism_resume_intelligence/05_person_skills.csv.skill`
4. **Future-Proofing & Trend Signals:** `prism_occupation_intelligence/USPTO–ONET/aggregated_task_demand.csv` calculates patent demand velocity to enrich `automation_risk_score` and `future_demand_score` in `occupations.csv`.

---

## Repository Governance & Guidelines

1. **Read-Only Data Integrity:** Data files inside `data/` must remain immutable during runtime execution. Any preprocessing or embedding vectors should be cached in secondary operational stores.
2. **Privacy & PII Protection:** `prism_resume_intelligence/01_people.csv` contains residual contact information (`name`, `email`, `phone`, `linkedin`). These fields must **never** be exposed in end-user application views or APIs and are restricted to anonymized backend pattern mining.
3. **Synthetic vs. Real Data Distinction:**
   - **Synthetic/Simulated:** `prism_education_career/`, `prism_india_jobs/`, `Career Prediction Dataset.csv`
   - **Real/Anonymized/Official:** `prism_esco/`, `prism_job_descriptions/`, `prism_occupation_intelligence/`, `prism_resume_intelligence/`, `Student performance (Polytechnic Institute of Portalegre).csv`
