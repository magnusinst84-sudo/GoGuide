# prism_india_jobs

## Purpose
Indian labor-market intelligence layer for PRISM Engine (DataQuest 3.0). Provides salary benchmarks, skill demand, company types, city distributions (Tier 1/2/3), work modes, and hiring applicant signals modeled specifically for the Indian job market (2024–2026).

## Quick Summary

| File Name | Format | Rows | Columns | Primary Key / Identifier | Key Fields |
|---|---|---|---|---|---|
| `india_job_market_2024_2026.csv` | CSV | 5,000 | 17 | `Job_ID` | `Job_Title`, `Company`, `Industry`, `City`, `Salary_LPA`, `Skills_Required`, `Experience_Level` |

---

## Detailed File Inventory

### `india_job_market_2024_2026.csv`
- **Rows:** 5,000
- **Columns:** 17
- **Primary Key:** `Job_ID` (100% unique string IDs from `JOB_00001` to `JOB_05000`)
- **Data Status:** Structured synthetic benchmark dataset representing Indian job market dynamics. Zero null values across all 5,000 rows.

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `Job_ID` | String | 0 | 0.0% | `JOB_00001`, `JOB_05000` | Primary key identifier |
| `Job_Title` | String | 0 | 0.0% | `Software Engineer`, `Data Scientist` | Target job title |
| `Company` | String | 0 | 0.0% | `Infosys`, `TCS`, `Flipkart`, `Amazon` | Hiring organization name |
| `Company_Type` | String | 0 | 0.0% | `MNC`, `Startup`, `Unicorn` | Organization classification |
| `Industry` | String | 0 | 0.0% | `Information Technology`, `Fintech` | Industry sector |
| `City` | String | 0 | 0.0% | `Bengaluru`, `Mumbai`, `Hyderabad`, `Pune` | Indian hiring hub location |
| `Location_Tier` | String | 0 | 0.0% | `Tier 1`, `Tier 2`, `Tier 3` | City tier classification |
| `Experience_Level` | String | 0 | 0.0% | `Entry Level (0-2 yrs)`, `Mid Level` | Required experience level |
| `Job_Type` | String | 0 | 0.0% | `Full-time`, `Contract`, `Internship` | Employment type |
| `Work_Mode` | String | 0 | 0.0% | `In-office`, `Hybrid`, `Remote` | Workplace arrangements |
| `Salary_LPA` | Float | 0 | 0.0% | `6.5`, `14.2`, `28.0` | Annual compensation in INR Lakhs Per Annum |
| `Skills_Required` | String | 0 | 0.0% | `Python, SQL, AWS, Docker` | Comma-separated list of required skills |
| `Education_Required` | String | 0 | 0.0% | `B.Tech/B.E.`, `B.Sc/BCA`, `MBA` | Educational eligibility requirement |
| `Openings` | Integer | 0 | 0.0% | `5`, `12`, `50` | Number of open headcount positions |
| `Applicants` | Integer | 0 | 0.0% | `120`, `450`, `1200` | Total applicant count (competition metric) |
| `Company_Rating` | Float | 0 | 0.0% | `4.2`, `3.8`, `4.5` | Employer rating (1.0 - 5.0 scale) |
| `Date_Posted` | String (Date) | 0 | 0.0% | `2024-03-15`, `2025-01-10` | Posting date (ISO YYYY-MM-DD format) |

---

## PRISM Integration / Usage

1. **India Market Compensation Benchmarks:** Provides localized salary figures in INR LPA to override general global/US compensation baselines in `prism_education_career/occupations.csv`.
2. **Opportunity Heatmap:** Powers regional hiring city analytics (Bengaluru vs Hyderabad vs Tier-2 hubs) for student career placement planning.
3. **Skill Demand Weighting:** Skills listed in `Skills_Required` cross-reference `prism_education_career/skills.csv.skill_name` to calculate real-world skill demand frequencies in India.
4. **Competition Metric:** `Applicants` / `Openings` ratio provides a competition index for target roles.

---

## Data Quality & Caveats

1. **Synthetic Nature:** Curated synthetic model dataset representing Indian hiring trends. Must be presented as market modeling intelligence rather than live API job board feeds.
2. **Coverage:** Balanced across Tech (IT, Software, Analytics) and Non-Tech roles, with heavy representation of Indian tech hubs (Bengaluru, NCR, Hyderabad, Pune, Mumbai, Chennai).

---

## Notes (preserved)

> **Preserved Notes & Contradiction Flag:**
> - Previous human documentation referenced a dataset named `india_tech_jobs.csv`.
> - **CONTRADICTION FLAG:** The actual file present on disk is **`india_job_market_2024_2026.csv`** containing 5,000 structured rows.
