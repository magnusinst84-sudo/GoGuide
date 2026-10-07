# prism_job_descriptions

## Purpose
Rich text and unstructured/semi-structured job listing intelligence layer for PRISM Engine (DataQuest 3.0). Provides real and curated global job posting text, duties, qualifications, and raw skill descriptions used for NLP skill extraction, vacancy pattern mining, and job description generation.

## Quick Summary

| File Name | Format | Rows | Columns | Primary Key / Identifier | Key Fields |
|---|---|---|---|---|---|
| `adzuna_global_job_listings_2025.csv` | CSV | 17,350 | 18 | `job_id` | `title`, `company`, `description`, `category_label`, `salary_min`, `salary_max` |
| `job_dataset.csv` | CSV | 1,068 | 7 | `(JobID, Title)` | `JobID`, `Title`, `ExperienceLevel`, `Skills`, `Responsibilities`, `Keywords` |
| `job_dataset.json` | JSON | 1,068 | 7 | N/A (JSON Array) | `JobID`, `Title`, `ExperienceLevel`, `Skills`, `Responsibilities`, `Keywords` |

---

## Detailed File Inventory

### 1. `adzuna_global_job_listings_2025.csv`
- **Rows:** 17,350
- **Columns:** 18
- **Primary Key:** `job_id` (Unique job listing ID)
- **Data Status:** Sourced from Adzuna global job vacancy feed (2025).

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `job_id` | String / Integer | 0 | 0.0% | `451239812`, `451239813` | Primary key identifier |
| `title` | String | 0 | 0.0% | `Senior Java Developer`, `Nurse Practitioner` | Raw job title |
| `company` | String | 4 | 0.02% | `CyberCoders`, `NHS Trust` | Hiring company / recruiter |
| `location_display` | String | 0 | 0.0% | `London, UK`, `New York, US` | Human-readable location text |
| `location_area` | String | 0 | 0.0% | `['UK', 'London']` | Hierarchical location array representation |
| `description` | String | 0 | 0.0% | `We are seeking an experienced Java...` | Full un-truncated job posting text |
| `created` | String (Timestamp) | 0 | 0.0% | `2025-01-15T08:30:00Z` | Date posted ISO timestamp |
| `contract_time` | String | 11,702 | 67.45% | `full_time`, `part_time` | Contract duration classification |
| `contract_type` | String | 15,644 | 90.17% | `permanent`, `contract` | Employment tenure type |
| `salary_min` | Float | 2 | 0.01% | `45000.0`, `85000.0` | Minimum annual salary bound |
| `salary_max` | Float | 36 | 0.21% | `60000.0`, `110000.0` | Maximum annual salary bound |
| `salary_is_predicted` | String / Boolean | 0 | 0.0% | `0`, `1` | Indicates if salary was estimated by platform |
| `redirect_url` | String (URL) | 0 | 0.0% | `https://www.adzuna.co.uk/land/ad/...` | Direct application link |
| `category_label` | String | 0 | 0.0% | `IT Jobs`, `Healthcare & Nursing Jobs` | Adzuna top-level category label |
| `category_tag` | String | 0 | 0.0% | `it-jobs`, `healthcare-nursing-jobs` | Normalized category tag slug |
| `latitude` | Float | 1,780 | 10.26% | `51.5074`, `40.7128` | Geocoded latitude |
| `longitude` | Float | 1,780 | 10.26% | `-0.1278`, `-74.0060` | Geocoded longitude |
| `adref` | String | 0 | 0.0% | `gb_451239812` | External platform reference ID |

### 2. `job_dataset.csv` & `job_dataset.json`
- **Rows:** 1,068
- **Columns:** 7
- **Primary Key:** `(JobID, Title)` (Composite primary key in CSV; matching JSON array structure)
- **Data Status:** Clean, structured job requirement profiles covering Tech and Non-Tech roles.

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `JobID` | Integer / String | 0 | 0.0% | `1`, `1068` | Job profile ID |
| `Title` | String | 1 | 0.09% | `Machine Learning Engineer`, `Product Manager` | Standardized job role title (1 null row) |
| `ExperienceLevel` | String | 0 | 0.0% | `Entry Level`, `Mid Level`, `Senior Level` | Target seniority level |
| `YearsOfExperience` | String / Integer | 0 | 0.0% | `1-3 years`, `5+ years` | Experience requirement range |
| `Skills` | String | 0 | 0.0% | `Python, PyTorch, Scikit-learn, Git` | Extracted key skills list |
| `Responsibilities` | String | 0 | 0.0% | `Develop ML models; Optimize pipelines...` | Bulleted or free-text duties |
| `Keywords` | String | 0 | 0.0% | `AI, Deep Learning, MLOps` | Search indexing keywords |

---

## PRISM Integration / Usage

1. **Skill Keyword Extraction:** Text from `description` and `Responsibilities` is processed via NLP to identify emerging skills for mapping into `prism_esco/skills_en.csv` and `prism_education_career/skills.csv`.
2. **Job Description Generation:** `job_dataset.json` powers PRISM's occupation details page views by providing candidate duties, responsibilities, and key deliverables for students exploring careers.
3. **Global Market Benchmarking:** `adzuna_global_job_listings_2025.csv` provides cross-border role requirements for students interested in international career transitions.

---

## Data Quality & Caveats

1. **Adzuna Nulls:** `contract_time` (67.45% null) and `contract_type` (90.17% null) are sparse in `adzuna_global_job_listings_2025.csv`.
2. **Title Anomaly:** `job_dataset.csv` contains 1 record with a missing/null `Title`.
3. **Geographic Coverage:** `adzuna_global_job_listings_2025.csv` reflects UK/US/Global listings; use `prism_india_jobs/` for India-specific salary and market demand.

---

## Notes (preserved)

> **Preserved Notes & Contradiction Flag:**
> - Previous documentation mentioned a single file named `job_descriptions.csv`.
> - **CONTRADICTION FLAG:** The actual files in `prism_job_descriptions/` are **`adzuna_global_job_listings_2025.csv`** (17,350 global vacancy rows), **`job_dataset.csv`** (1,068 structured profiles), and **`job_dataset.json`** (1,068 JSON records).
