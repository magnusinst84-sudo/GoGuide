# prism_education_career

## Purpose
Core synthetic relational dataset modeling the education-to-career pathway landscape for the PRISM Engine (DataQuest 3.0). Serves as the primary intelligence layer connecting academic degrees, fields of study, occupations, required skills, industry sectors, and long-term career progression paths.

## Quick Summary

| File Name | Format | Rows | Columns | Primary Key / Identifier | Key Fields |
|---|---|---|---|---|---|
| `career_progression.csv` | CSV | 731 | 10 | `progression_id` | `from_occupation_id`, `to_occupation_id`, `typical_years_experience`, `advancement_type`, `salary_growth_percent` |
| `education_pathways.csv` | CSV | 686 | 12 | `education_id` | `degree_level`, `field_of_study`, `sub_field`, `stem_flag`, `prerequisite_education` |
| `education_to_occupation.csv` | CSV | 2,670 | 18 | `mapping_id` | `education_id`, `occupation_id`, `transition_likelihood`, `typical_starting_salary_inr_lpa`, `career_fit_score` |
| `occupation_requirements.csv` | CSV | 341 | 9 | `requirement_id` / `occupation_id` | `occupation_id`, `minimum_degree_level`, `preferred_degree_level`, `mandatory_certifications`, `portfolio_required` |
| `occupation_to_industry.csv` | CSV | 1,023 | 7 | `mapping_id` | `occupation_id`, `industry_id`, `industry_name`, `sub_industry`, `employment_share_percent` |
| `occupation_to_skill.csv` | CSV | 3,309 | 7 | `mapping_id` | `occupation_id`, `skill_id`, `skill_importance`, `skill_level_required`, `is_core_skill` |
| `occupations.csv` | CSV | 341 | 16 | `occupation_id` | `occupation_name`, `onet_soc_code`, `esco_occupation_uri`, `average_salary_inr_lpa`, `automation_risk_score` |
| `skills.csv` | CSV | 420 | 5 | `skill_id` | `skill_name`, `skill_category`, `esco_skill_uri`, `skill_description` |

---

## Detailed File Inventory

### 1. `career_progression.csv`
- **Rows:** 731
- **Columns:** 10
- **Primary Key:** `progression_id` (Unique integer identifier)
- **Data Status:** Validated synthetic transitions; 0 career self-loops (`from_occupation_id != to_occupation_id`).

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `progression_id` | String / Integer | 0 | 0.0% | `PROG_0001`, `PROG_0002` | Unique career progression link ID |
| `from_occupation_id` | String | 0 | 0.0% | `OCC_0001`, `OCC_0045` | Foreign key → `occupations.occupation_id` |
| `to_occupation_id` | String | 0 | 0.0% | `OCC_0012`, `OCC_0088` | Foreign key → `occupations.occupation_id` |
| `typical_years_experience` | Integer / Float | 0 | 0.0% | `2`, `5`, `8` | Expected years in origin role before transition |
| `advancement_type` | String | 0 | 0.0% | `Promotion`, `Lateral Move`, `Specialization` | Type of progression movement |
| `key_transition_skills` | String | 0 | 0.0% | `Project Management, Leadership` | Critical skills needed to execute move |
| `bridge_learning_required` | String | 0 | 0.0% | `System Architecture Certification` | Recommended learning/up-skilling |
| `difficulty_rating` | String / Float | 0 | 0.0% | `Moderate`, `High`, `Low` | Perceived barrier to transition |
| `salary_growth_percent` | Float | 0 | 0.0% | `15.5`, `30.0` | Expected compensation increase (%) |
| `additional_education_required` | String | 48 | 6.57% | `MBA`, `Master of Science`, `None` | Degree required for transition if any |

### 2. `education_pathways.csv`
- **Rows:** 686
- **Columns:** 12
- **Primary Key:** `education_id` (Unique pathway ID)

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `education_id` | String | 0 | 0.0% | `EDU_0001`, `EDU_0686` | Primary key |
| `degree_level` | String | 0 | 0.0% | `Bachelor`, `Master`, `Doctorate`, `Diploma` | Academic degree qualification level |
| `field_of_study` | String | 0 | 0.0% | `Computer Science`, `Mechanical Engineering` | Broad academic field |
| `sub_field` | String | 0 | 0.0% | `Artificial Intelligence`, `Robotics` | Specialized sub-discipline |
| `stem_flag` | Boolean / String | 0 | 0.0% | `TRUE`, `FALSE` | Indicates STEM field classification |
| `typical_duration_years` | Integer | 0 | 0.0% | `3`, `4`, `2` | Normal program completion time |
| `degree_type` | String | 0 | 0.0% | `B.Tech`, `B.Sc`, `M.Tech`, `MBA` | Specific degree designation |
| `prerequisite_education` | String | 0 | 0.0% | `Higher Secondary (10+2)`, `Bachelor Degree` | Entry requirement |
| `is_professional_degree` | Boolean / String | 0 | 0.0% | `TRUE`, `FALSE` | Licensed/professional program flag |
| `mapped_occupations_count` | Integer | 0 | 0.0% | `4`, `6` | Count of target roles mapped |
| `demand_growth_rate` | Float | 0 | 0.0% | `8.5`, `12.0` | Projected pathway demand growth (%) |
| `mapped_skills_count` | Integer | 0 | 0.0% | `12`, `18` | Total skill count associated |

### 3. `education_to_occupation.csv`
- **Rows:** 2,670
- **Columns:** 18
- **Primary Key:** `mapping_id` (Unique mapping ID)

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `mapping_id` | String | 0 | 0.0% | `MAP_0001`, `MAP_2670` | Primary key |
| `education_id` | String | 0 | 0.0% | `EDU_0012`, `EDU_0450` | Foreign key → `education_pathways.education_id` |
| `degree_level` | String | 0 | 0.0% | `Bachelor`, `Master` | Denormalized degree level |
| `field_of_study` | String | 0 | 0.0% | `Data Science`, `Finance` | Denormalized field |
| `sub_field` | String | 0 | 0.0% | `Machine Learning`, `Corporate Finance` | Denormalized subfield |
| `occupation_id` | String | 0 | 0.0% | `OCC_0005`, `OCC_0120` | Foreign key → `occupations.occupation_id` |
| `occupation_name` | String | 0 | 0.0% | `Data Scientist`, `Financial Analyst` | Denormalized role title |
| `transition_likelihood` | Float | 0 | 0.0% | `0.85`, `0.60` | Probability score of transition (0-1) |
| `entry_barrier_level` | String | 0 | 0.0% | `Low`, `Medium`, `High` | Entry difficulty |
| `typical_starting_salary_inr_lpa` | Float | 0 | 0.0% | `6.5`, `12.0` | Starting salary benchmark in INR Lakhs/Annum |
| `top_required_skills` | String | 0 | 0.0% | `Python, SQL, Machine Learning` | Top skill list |
| `time_to_career_fit_months` | Integer | 0 | 0.0% | `6`, `12` | Ramp-up months to role competency |
| `career_fit_score` | Float | 0 | 0.0% | `88.5`, `92.0` | Calculated alignment score (0-100) |
| `pathway_type` | String | 0 | 0.0% | `Direct`, `Adjacent`, `Alternative` | Transition pathway classification |
| `recommended_certifications` | String | 0 | 0.0% | `AWS Certified Data Analytics`, `CFA Level 1` | Recommended credentials |
| `why_this_career` | String | 0 | 0.0% | `Strong alignment in analytical skills...` | Explanatory rationale text |
| `industry_sector` | String | 0 | 0.0% | `Technology`, `Financial Services` | Target industry sector |
| `growth_outlook` | String | 0 | 0.0% | `High Growth`, `Stable` | Market growth projection |

### 4. `occupation_requirements.csv`
- **Rows:** 341
- **Columns:** 9
- **Primary Key:** `requirement_id` (1:1 with `occupation_id`)

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `requirement_id` | String | 0 | 0.0% | `REQ_0001`, `REQ_0341` | Primary key |
| `occupation_id` | String | 0 | 0.0% | `OCC_0001`, `OCC_0341` | Foreign key → `occupations.occupation_id` (100% unique) |
| `occupation_name` | String | 0 | 0.0% | `Software Engineer` | Denormalized role title |
| `minimum_degree_level` | String | 0 | 0.0% | `Bachelor`, `Diploma` | Minimum educational requirement |
| `preferred_degree_level` | String | 0 | 0.0% | `Master`, `Bachelor` | Preferred educational level |
| `licensing_or_statutory_requirement` | String | 144 | 42.23% | `Bar Council License`, `Medical Council Reg` | Official license if mandatory |
| `mandatory_certifications` | String | 0 | 0.0% | `None`, `AWS Certified Solutions Architect` | Mandatory certifications |
| `portfolio_required` | Boolean / String | 0 | 0.0% | `TRUE`, `FALSE` | Portfolio requirement flag |
| `background_check_required` | Boolean / String | 0 | 0.0% | `TRUE`, `FALSE` | Background verification flag |

### 5. `occupation_to_industry.csv`
- **Rows:** 1,023
- **Columns:** 7
- **Primary Key:** `mapping_id`

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `mapping_id` | String | 0 | 0.0% | `IND_MAP_0001` | Primary key |
| `occupation_id` | String | 0 | 0.0% | `OCC_0001` | Foreign key → `occupations.occupation_id` |
| `industry_id` | String | 0 | 0.0% | `IND_001`, `IND_061` | Industry classification ID (61 unique industries) |
| `industry_name` | String | 0 | 0.0% | `Information Technology`, `Healthcare` | Broad industry name |
| `sub_industry` | String | 0 | 0.0% | `Software Products`, `Hospitals` | Sub-industry classification (66 unique sub-industries) |
| `relevance_score` | Float | 0 | 0.0% | `0.95`, `0.70` | Industry relevance weight |
| `employment_share_percent` | Float | 0 | 0.0% | `45.0`, `20.0` | Estimated workforce distribution share |

### 6. `occupation_to_skill.csv`
- **Rows:** 3,309
- **Columns:** 7
- **Primary Key:** `mapping_id` (Composite key: `(occupation_id, skill_id)`)

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `mapping_id` | String | 0 | 0.0% | `SKL_MAP_0001` | Primary key |
| `occupation_id` | String | 0 | 0.0% | `OCC_0001` | Foreign key → `occupations.occupation_id` |
| `skill_id` | String | 0 | 0.0% | `SKILL_0001` | Foreign key → `skills.skill_id` |
| `skill_name` | String | 0 | 0.0% | `Python`, `Data Analysis` | Denormalized skill name |
| `skill_importance` | Float | 0 | 0.0% | `4.8`, `3.5` | Importance weight (1.0 - 5.0 scale) |
| `skill_level_required` | String | 0 | 0.0% | `Advanced`, `Intermediate` | Competency level required |
| `is_core_skill` | Boolean / String | 0 | 0.0% | `TRUE`, `FALSE` | Indicates core vs secondary skill |

### 7. `occupations.csv`
- **Rows:** 341
- **Columns:** 16
- **Primary Key:** `occupation_id` (Unique occupation ID)

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `occupation_id` | String | 0 | 0.0% | `OCC_0001`, `OCC_0341` | Primary key |
| `occupation_name` | String | 0 | 0.0% | `Software Engineer`, `Data Analyst` | Canonical occupation title |
| `onet_soc_code` | String | 0 | 0.0% | `15-1252.00`, `15-2051.00` | O*NET SOC crosswalk code |
| `esco_occupation_uri` | String | 252 | 73.9% | `http://data.europa.eu/esco/occupation/...` | ESCO URI bridge (89 matched roles) |
| `industry_sector` | String | 0 | 0.0% | `Technology`, `Finance` | Primary industry sector |
| `sub_industry` | String | 0 | 0.0% | `Software Engineering`, `Banking` | Primary sub-industry |
| `seniority_level` | String | 0 | 0.0% | `Entry`, `Mid`, `Senior` | Role level |
| `average_salary_inr_lpa` | Float | 0 | 0.0% | `8.5`, `18.0` | Benchmark salary in INR LPA |
| `min_salary_inr_lpa` | Float | 0 | 0.0% | `4.5`, `10.0` | Minimum salary bound |
| `max_salary_inr_lpa` | Float | 0 | 0.0% | `15.0`, `30.0` | Maximum salary bound |
| `work_environment` | String | 0 | 0.0% | `Office`, `Hybrid`, `Field` | Primary work setting |
| `remote_work_eligibility` | String | 0 | 0.0% | `High`, `Medium`, `Low` | Remote work capability |
| `automation_risk_score` | Float | 0 | 0.0% | `0.15`, `0.65` | AI/automation vulnerability (0-1) |
| `future_demand_score` | Float | 0 | 0.0% | `85.0`, `92.0` | Projected 10-year demand index (0-100) |
| `job_description` | String | 0 | 0.0% | `Designs and develops software systems...` | Concise role overview |
| `career_family` | String | 0 | 0.0% | `Software & Engineering`, `Data & Analytics` | High-level career cluster |

### 8. `skills.csv`
- **Rows:** 420
- **Columns:** 5
- **Primary Key:** `skill_id` (Unique skill ID)

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `skill_id` | String | 0 | 0.0% | `SKILL_0001`, `SKILL_0420` | Primary key |
| `skill_name` | String | 0 | 0.0% | `Python`, `Project Management` | Canonical skill name |
| `skill_category` | String | 0 | 0.0% | `Technical`, `Soft Skill`, `Domain Knowledge` | Skill category classification |
| `esco_skill_uri` | String | 410 | 97.62% | `http://data.europa.eu/esco/skill/...` | ESCO skill URI bridge (10 matched skills) |
| `skill_description` | String | 0 | 0.0% | `Proficiency in Python programming...` | Skill description |

---

## PRISM Integration / Usage

The `prism_education_career` domain is the primary graph database schema backbone for PRISM Engine:

```
[education_pathways] ──(1:N)──> [education_to_occupation] <──(N:1)── [occupations]
                                                                        │  │  │
                ┌───────────────────────────────────────────────────────┘  │  └─────────────┐
                ▼                                                          ▼                ▼
    [career_progression]                                   [occupation_to_skill]   [occupation_to_industry]
    (from_occ -> to_occ)                                           │                        │
                                                                   ▼                        ▼
                                                               [skills]                (61 Industries)
```

1. **Degree-to-Career Recommendation Engine:** `education_to_occupation.csv` matches student degree backgrounds (`education_id`) to viable target occupations (`occupation_id`), weighted by `career_fit_score` and `transition_likelihood`.
2. **Skill Gap Analysis:** `occupation_to_skill.csv` joined with `skills.csv` provides required core and secondary competencies for target roles.
3. **Career Progression Roadmap:** `career_progression.csv` powers multi-stage progression trajectories from entry-level to leadership roles.
4. **Taxonomy & Standards Bridge:** `onet_soc_code` and `esco_occupation_uri` in `occupations.csv` link this synthetic dataset directly into international standards in `prism_esco/` and `prism_occupation_intelligence/`.

---

## Data Quality & Caveats

1. **Validation Status:** Fully validated with 0 duplicate rows, 100% primary key uniqueness across all tables, 0 foreign-key reference violations, and 0 career self-loops.
2. **Synthetic Nature:** Synthetic dataset generated for hackathon benchmarking; compensation and growth metrics reflect curated logical distributions rather than live survey data.
3. **ESCO Match Rate:** ESCO URIs are present on 26.1% of occupations (89/341) and 2.38% of skills (10/420). Missing URIs are represented as `NULL` / empty strings.
4. **Currency:** Benchmark salaries are expressed in Indian Rupees Lakhs Per Annum (INR LPA) for the Indian job market context.

---

## Notes (preserved)

> **Preserved Notes:**
> - `education_pathways.csv` — 686 rows
> - `occupations.csv` — 341 rows
> - `skills.csv` — 420 rows
> - `education_to_occupation.csv` — 2,670 rows
> - `occupation_to_skill.csv` — 3,309 rows
> - `occupation_to_industry.csv` — 1,023 rows
> - `occupation_requirements.csv` — 341 rows
> - `career_progression.csv` — 731 rows
> - Verified zero foreign-key violations, zero composite duplicate mappings, zero career self-loops across 61 industries and 66 sub-industries.
