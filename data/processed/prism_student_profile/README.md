# prism_student_profile

## Purpose
Student aptitude, personality, and academic-performance intelligence layer for PRISM Engine (DataQuest 3.0). Used to model student psychometric profiles (Big Five personality traits + 5 aptitude dimensions) and higher-education academic performance/retention metrics for personalized career recommendation and risk assessment.

## Quick Summary

| File Name | Format | Rows | Columns | Primary Key / Identifier | Key Fields |
|---|---|---|---|---|---|
| `Career Prediction Dataset.csv` | CSV | 105 | 11 | N/A (Bag/ML Rows) | `O_score`, `C_score`, `E_score`, `A_score`, `N_score`, `Numerical Aptitude`, `Career` |
| `Student performance (Polytechnic Institute of Portalegre).csv` | CSV | 4,424 | 37 | N/A (Student Records) | `Course`, `Admission grade`, `Tuition fees up to date`, `Curricular units 1st sem (approved)`, `Target` |

---

## Detailed File Inventory

### 1. `Career Prediction Dataset.csv`
- **Rows:** 105
- **Columns:** 11
- **Primary Key:** None (Independent psychometric profile records)
- **Data Status:** Synthetic ML training dataset modeling OCEAN personality scores and aptitudes to target career cluster predictions. Zero nulls.

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `O_score` | Integer | 0 | 0.0% | `4`, `7`, `9` | Openness to Experience (1–10 scale) |
| `C_score` | Integer | 0 | 0.0% | `6`, `8` | Conscientiousness score |
| `E_score` | Integer | 0 | 0.0% | `3`, `5` | Extraversion score |
| `A_score` | Integer | 0 | 0.0% | `5`, `7` | Agreeableness score |
| `N_score` | Integer | 0 | 0.0% | `2`, `4` | Neuroticism score |
| `Numerical Aptitude` | Integer | 0 | 0.0% | `7`, `9` | Numerical reasoning score (1–10 scale) |
| `Spatial Aptitude` | Integer | 0 | 0.0% | `5`, `8` | Spatial reasoning score |
| `Perceptual Aptitude` | Integer | 0 | 0.0% | `6`, `8` | Perceptual speed/accuracy score |
| `Abstract Reasoning` | Integer | 0 | 0.0% | `8`, `9` | Abstract logical reasoning score |
| `Verbal Reasoning` | Integer | 0 | 0.0% | `6`, `7` | Verbal comprehension score |
| `Career` | String | 0 | 0.0% | `Software Engineer`, `Lawyer` | Target career prediction label |

### 2. `Student performance (Polytechnic Institute of Portalegre).csv`
- **Rows:** 4,424
- **Columns:** 37
- **Primary Key:** None (Anonymized student academic record rows)
- **Data Status:** Real anonymized academic performance dataset from the Polytechnic Institute of Portalegre. Zero nulls.

| Column | Data Type | Null Count | Null % | Sample Values | Description / Quality Notes |
|---|---|---|---|---|---|
| `Marital status` | Integer | 0 | 0.0% | `1`, `2` | Categorical code |
| `Application mode` | Integer | 0 | 0.0% | `1`, `17` | College application route code |
| `Course` | Integer | 0 | 0.0% | `33`, `171`, `9015` | Academic course/major code |
| `Daytime/evening attendance\t` | Integer | 0 | 0.0% | `1`, `0` | Attendance mode (**Note: Header includes trailing tab `\t`**) |
| `Previous qualification` | Integer | 0 | 0.0% | `1`, `3` | Prior education code |
| `Admission grade` | Float | 0 | 0.0% | `127.3`, `140.0` | Entry admission test score |
| `Gender` | Integer | 0 | 0.0% | `1`, `0` | Gender code (1=Male, 0=Female) |
| `Tuition fees up to date` | Integer | 0 | 0.0% | `1`, `0` | Financial compliance flag (1=Yes, 0=No) |
| `Curricular units 1st sem (approved)` | Integer | 0 | 0.0% | `5`, `6` | First-semester passed credits |
| `Curricular units 2nd sem (approved)` | Integer | 0 | 0.0% | `6`, `0` | Second-semester passed credits |
| `Target` | String | 0 | 0.0% | `Graduate`, `Dropout`, `Enrolled` | Academic outcome classification label |

---

## PRISM Integration / Usage

1. **Student Onboarding Profile Matching:** `Career Prediction Dataset.csv` trains PRISM's psychometric questionnaire module, mapping a student's self-assessed Big Five personality and aptitude scores to recommended career pathways in `prism_education_career/occupations.csv`.
2. **Academic Risk & Retention Modeling:** `Student performance (Polytechnic Institute of Portalegre).csv` enables PRISM to predict academic completion risks based on early semester performance metrics.

---

## Data Quality & Caveats

1. **Header Anomaly:** Column 5 in `Student performance (Polytechnic Institute of Portalegre).csv` contains a trailing tab character (`Daytime/evening attendance\t`). CSV parsers should strip whitespace/tabs from column names.
2. **Filenames:** Files retain original Kaggle source names (`Career Prediction Dataset.csv` and `Student performance (Polytechnic Institute of Portalegre).csv`).

---

## Notes (preserved)

> **Preserved Notes & Contradiction Flag:**
> - `career_prediction.csv` — **SYNTHETIC / SIMULATED** (psychometric ML training dataset)
> - `student_performance.csv` — **REAL (anonymized)** (Polytechnic Institute of Portalegre dataset)
> - **CONTRADICTION FLAG:** Previous documentation referenced simplified names (`career_prediction.csv` and `student_performance.csv`). The actual filenames on disk are **`Career Prediction Dataset.csv`** and **`Student performance (Polytechnic Institute of Portalegre).csv`**.
