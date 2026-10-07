# prism_occupation_intelligence

## Purpose
Occupation and task intelligence layer for PRISM Engine (DataQuest 3.0), combining O*NET SOC occupation task structures with United States Patent and Trademark Office (USPTO) Cooperative Patent Classification (CPC) patent data (2010–2023). Used to compute task-level automation risk, technological demand evolution, and future-proofing scores for occupations.

## Location Note
All data files for this domain reside within the **`USPTO–ONET/`** subfolder (`data/prism_occupation_intelligence/USPTO–ONET/`).

## Quick Summary

| File Name | Format | Rows | Columns | Primary Key / Identifier | Key Fields |
|---|---|---|---|---|---|
| `USPTO–ONET/aggregated_task_demand.csv` | CSV | 1,600 | 4 | `task_id` | `task_id`, `demand_2010_2023`, `demand_2019_2023`, `task_description` |
| `USPTO–ONET/cpc_descriptions.csv` | CSV | 37 | 4 | `cpc_code` | `cpc_code`, `description`, `parent_code`, `full_description` |
| `USPTO–ONET/onet_jobs.csv` | CSV | 40 | 3 | `soc_code` | `soc_code`, `job_title`, `job_description` |
| `USPTO–ONET/onet_occupations.csv` | CSV | 40 | 4 | `soc_code` | `soc_code`, `job_title`, `job_description`, `domain` |
| `USPTO–ONET/onet_tasks.csv` | CSV | 1,600 | 5 | `task_id` | `soc_code`, `job_title`, `task_id`, `task_description`, `task_type` |
| `USPTO–ONET/task_cpc_similarity_topk.csv` | CSV | 8,000 | 3 | `(task_id, cpc_code)` | `task_id`, `cpc_code`, `cosine_similarity` |
| `USPTO–ONET/uspto_patents.csv` | CSV | 2,999,990 | 3 | `(patent_id, year)` | `patent_id`, `year`, `cpc_code` |
| `USPTO–ONET/yearly_task_demand.csv` | CSV | 22,400 | 4 | `(task_id, year)` | `task_id`, `job_title`, `year`, `demand` |

---

## Detailed File Inventory

### 1. `onet_occupations.csv` & `onet_jobs.csv`
- **Rows:** 40
- **Columns:** 4 (occupations) / 3 (jobs)
- **Primary Key:** `soc_code` (O*NET 8-digit SOC identifier, e.g., `15-1252.00`)
- **Data Status:** Clean reference dataset of core benchmark occupations across domain sectors.

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `soc_code` | String | 0 | 0.0% | `15-1252.00`, `15-2051.00` | Standard Occupational Classification code |
| `job_title` | String | 0 | 0.0% | `Software Developers`, `Data Scientists` | O*NET occupation title |
| `job_description` | String | 0 | 0.0% | `Develop, create, and modify computer...` | Standardized job definition text |
| `domain` | String | 0 | 0.0% | `Information Technology`, `Engineering` | High-level functional domain |

### 2. `onet_tasks.csv`
- **Rows:** 1,600
- **Columns:** 5
- **Primary Key:** `task_id` (Unique integer task identifier)
- **Description:** Granular workplace task statements mapped to O*NET occupations (40 tasks per occupation).

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `soc_code` | String | 0 | 0.0% | `15-1252.00` | Foreign key → `onet_occupations.soc_code` |
| `job_title` | String | 0 | 0.0% | `Software Developers` | Denormalized occupation title |
| `task_id` | Integer | 0 | 0.0% | `1001`, `2600` | Primary key task identifier |
| `task_description` | String | 0 | 0.0% | `Analyze user needs and software requirements...` | Granular work task description |
| `task_type` | String | 0 | 0.0% | `Core`, `Supplemental` | O*NET task importance classification |

### 3. `aggregated_task_demand.csv` & `yearly_task_demand.csv`
- **Rows:** 1,600 (aggregated) / 22,400 (yearly 2010–2023)
- **Columns:** 4
- **Primary Key:** `task_id` (aggregated) / Composite `(task_id, year)` (yearly)
- **Description:** Derived patent-similarity weighted demand indices reflecting patenting activity linked to work tasks over time.

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `task_id` | Integer | 0 | 0.0% | `1001`, `1600` | Foreign key → `onet_tasks.task_id` |
| `demand_2010_2023` | Float | 0 | 0.0% | `142.50`, `89.12` | Cumulative patent demand weight (2010–2023) |
| `demand_2019_2023` | Float | 0 | 0.0% | `58.20`, `31.45` | Recent 5-year patent demand weight (2019–2023) |
| `year` | Integer | 0 | 0.0% | `2010`, `2023` | Calendar year (in `yearly_task_demand.csv`) |
| `demand` | Float | 0 | 0.0% | `12.4`, `18.6` | Annual demand score |

### 4. `cpc_descriptions.csv`
- **Rows:** 37
- **Columns:** 4
- **Primary Key:** `cpc_code` (Patent Classification code, e.g., `G06F`)
- **Null Stats:** `parent_code` (13.51% null for root CPC categories).

### 5. `task_cpc_similarity_topk.csv`
- **Rows:** 8,000
- **Columns:** 3
- **Primary Key:** Composite `(task_id, cpc_code)`
- **Description:** Semantic vector cosine similarity scores between O*NET tasks and USPTO patent classes (top-k matches per task).

### 6. `uspto_patents.csv`
- **Rows:** 2,999,990
- **Columns:** 3
- **Primary Key:** Composite `(patent_id, year)`
- **Description:** Bulk patent classification records linking 3M USPTO patent filings to CPC technology codes across years.

---

## PRISM Integration / Usage

1. **Future-Proofing Index:** `aggregated_task_demand.csv` feeds PRISM's `future_demand_score` in `prism_education_career/occupations.csv`.
2. **SOC Taxonomy Link:** `soc_code` in `onet_occupations.csv` connects directly to `onet_soc_code` in `prism_education_career/occupations.csv`.
3. **Task Automation Risk:** Semantic similarity weights in `task_cpc_similarity_topk.csv` allow PRISM to model which specific job duties are seeing high patenting/automation activity.

---

## Data Quality & Caveats

1. **Subdirectory Structure:** Data files are stored inside `USPTO–ONET/`.
2. **US Market Origin:** O*NET reflects US labor structure; compensation or demand weights should be interpreted in conjunction with `prism_india_jobs/` for Indian context.
3. **Patent Bias:** Patent-derived demand heavily highlights hardware, software, and R&D-intensive sectors relative to service or manual labor roles.

---

## Notes (preserved)

> **Preserved Notes:**
> - `onet_soc_code` in `prism_education_career/occupations.csv` links to `onet_occupations.csv`.
> - Task demand feeds the "future-proofing" signals in PRISM's Career Roadmap module.
> - Cross-referenced with `prism_esco/` via occupation URI ↔ SOC code mappings.
> - Salary/demand from `prism_india_jobs/` overrides O*NET salary when India context is needed.
