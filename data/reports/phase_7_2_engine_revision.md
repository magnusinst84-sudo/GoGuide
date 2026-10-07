# Phase 7.2 — Recommendation Engine Revision Report

**Status:** `COMPLETE`  
**Ranking Collapse Resolved:** `True`  

---
## Validation Checks

| Check | Result |
|-------|--------|
| A_no_invalid_occ_ids | ✅ PASS |
| B_no_duplicate_stu_occ | ✅ PASS |
| C_no_fabricated_ids | ✅ PASS |
| D_no_fabricated_edu | ✅ PASS |
| E_no_fabricated_skills | ✅ PASS |
| F_no_fabricated_market | ✅ PASS |
| G_no_fabricated_progression | ✅ PASS |
| H_scores_in_01 | ✅ PASS |
| I_no_rankable_below_min_factors | ✅ PASS |
| J_no_single_factor_100pct | ✅ PASS |
| K_synth_labeled | ✅ PASS |
| L_explanations_100pct | ✅ PASS |
| N_ranking_collapse_resolved | ✅ PASS |

---
## Score Distribution

- **min:** 0.4202
- **max:** 0.9963
- **mean:** 0.6081
- **median:** 0.6087
- **p25:** 0.5467
- **p75:** 0.671
- **unique_score_count:** 19

---
## Factor Availability (Rankable Recs)

| Factor | Recommendations with evidence |
|--------|-------------------------------|
| student_fit_coverage | 19 |
| education_fit_coverage | 0 |
| skill_fit_coverage | 0 |
| market_opportunity_coverage | 22643 |
| progression_coverage | 22631 |

---
## Evidence Count Distribution (All Candidates)

| Evidence Count | Candidates |
|----------------|------------|
| 1 | 978273 |
| 2 | 81535 |
| 3 | 3 |

---
## Tie Diagnostics

- Students with ALL Top-5 tied: **0** (0.0%)
- Students with differentiated Top-5: **4529**
- Average unique scores per student: **5.0**

---
## Before / After Comparison

| Metric | Phase 7 | Phase 7.2 |
|--------|---------|----------|
| Total recommendations | 22645 | 22645 |
| Score min | 1.0 | 0.4202 |
| Score max | 1.0 | 0.9963 |
| Score mean | 1.0 | 0.6081 |
| Unique scores | 1 | 19 |
| % all-tied Top-5 | 100.0% | 0.0% |
| Ranking collapse | True | False |

---
## Remaining Limitations

- education_fit is NOT_AVAILABLE for all students in current dataset (no degree/field_of_study in student_features.csv); UI must collect this.
- skill_fit is NOT_AVAILABLE for all students in current dataset (no self-reported skills); UI must collect this.
- student_fit is available only for students whose cluster maps to a MATCHED occupation (44 of 104 clusters are MATCHED).
- Market scoring uses REAL_JOB_FEED where available (198 occupations) and SYNTHETIC_PROTOTYPE as fallback (18 additional); SYNTHETIC scores are clearly labeled.
- Progression graph has 43 edges across 31 occupations only; most occupations lack progression evidence. This limits progression_score coverage.
- The engine does NOT include financial feasibility (separate GoGuide layer).
- cluster_to_occ mappings are from crosswalk MATCHED status only; 60 clusters remain UNMAPPED.
