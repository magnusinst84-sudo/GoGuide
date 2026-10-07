# Phase 7.1 — Recommendation Audit Report
**Diagnostic only. No Phase 6 or Phase 7 outputs were modified.**
**Total recommendations audited:** 22,645

---
## 1. Executive Summary
- **Production Ready:** False
- **Scoring Engine Status:** `CORRECT_BUT_EVIDENCE_STARVED`
- **Ranking Status:** `RANKING_COLLAPSE`
- **Root Cause:** Single-factor renormalization + binary factors both = 1.0 for all candidates
- **Data Integrity:** VALID — no fabricated IDs, no invalid references
- **skill_gap_analysis_status:** `NOT_AVAILABLE — correctly labeled`

> Phase 7 is NOT production-ready. The scoring engine is architecturally correct and deterministic, but available student evidence is too sparse to produce differentiated scores. 100% of students receive final_score=1.0 on all 5 recommendations, and Top-5 selection is entirely determined by occupation_id tie-breaking. The ranking is not meaningful.

---
## 2. Score-Collapse Diagnosis
- **Unique final_score values:** [1.0]
- **Min / Max / Mean:** 1.0 / 1.0 / 1.0
- **Students with all 5 tied at 1.0:** 4529 (100.0%)
- **Unique occupations in recommendations:** 5

**Scores by rank:**
| Rank | Mean Score |
|------|------------|
| 1 | 1.0 |
| 2 | 1.0 |
| 3 | 1.0 |
| 4 | 1.0 |
| 5 | 1.0 |

---
## 3. Factor Availability

### A. Student Fit
- Psychometric students: 105
- Unique career clusters: 104
- Clusters matched to an occupation (MATCHED): 44
- Clusters unmapped: 60
- **Students with usable student_fit: 44**
- Reason missing: Each psychometric student has exactly ONE career cluster label. The cluster is matched to AT MOST one canonical occupation. For any other candidate occupation in Top-K, student_fit is unavailable. Only 1 student out of 4529 had their matched occupation appear in Top-5.

### B. Education Fit
- student_features.csv fields: `A_score, Abstract Reasoning, Admission_Grade, C_score, Career, E_score, N_score, Numerical Aptitude, O_score, Perceptual Aptitude, Spatial Aptitude, Target, Tuition_Paid, Verbal Reasoning`
- Has education data: **False**
- Students with usable education evidence: **0**
- Reason: student_features.csv only contains Psychometric and Academic Performance groups. Neither group contains degree, field_of_study, or education_id. No student→education link exists in current Phase 6 output. education_fit is NOT_AVAILABLE for ALL 4529 students.

### C. Skill Fit
- skill_gap_analysis_status: `NOT_AVAILABLE`
- Occupation skill edges available: 708
- UI readiness: The system is architecturally ready to accept self-reported skills from the GoGuide UI. occupation_skill_edges.csv provides occupation skill requirements. Once a student submits skills via UI, overlap can be calculated.

### D. Market Opportunity
- Total market postings: 22,350
- MATCHED postings: 6,815
- REAL_JOB_FEED postings: 3,630
- SYNTHETIC_PROTOTYPE postings: 3,185
- Occupations with REAL feed: 198
- Unique market scores in recs: [1.0]
- **Is binary score:** True
> market_opportunity is scored as a binary: 1.0 if MATCHED evidence exists (REAL_JOB_FEED preferred), 0.5 if SYNTHETIC_PROTOTYPE only, else NOT_AVAILABLE. This is evidence PRESENCE, not evidence STRENGTH.

### E. Progression
- Total progression edges: 43
- Occupations as target (can transition INTO): 31
- Unique progression scores: ['1.0']
- **Effectively always 1.0:** True
> Progression is scored as binary: 1.0 if occupation_id is in the target set of career_progression_edges.csv (meaning the occupation can be transitioned INTO), 0.0 otherwise. Since candidate_occs = matched_occs | market_occ_ids | prog_targets, ALL occupations from prog_targets receive progression=1.0 by construction. This makes progression=1.0 for the ENTIRE candidate pool drawn from prog_targets.

---
## 4. Renormalization Analysis

**Case: `only_progression`**
- Available factors: `['progression']`
- Original weights: `{'progression': 0.1}`
- Renormalized weights: `{'progression': 1.0}`
- Factor values: `{'progression': 1.0}`
- **final_score: 1.0**
- Diagnosis: progression renormalizes from 0.10 → 1.00; score collapses to 1.0

**Case: `market_and_progression`**
- Available factors: `['market_opportunity', 'progression']`
- Original weights: `{'market_opportunity': 0.1, 'progression': 0.1}`
- Renormalized weights: `{'market_opportunity': 0.5, 'progression': 0.5}`
- Factor values: `{'market_opportunity': 1.0, 'progression': 1.0}`
- **final_score: 1.0**
- Diagnosis: both factors = 1.0, so renormalized score = 1.0 regardless of weights

**Case: `student_market_progression`**
- Available factors: `['student_fit', 'market_opportunity', 'progression']`
- Original weights: `{'student_fit': 0.35, 'market_opportunity': 0.1, 'progression': 0.1}`
- Renormalized weights: `{'student_fit': 0.6364, 'market_opportunity': 0.1818, 'progression': 0.1818}`
- Factor values: `{'student_fit': 1.0, 'market_opportunity': 1.0, 'progression': 1.0}`
- **final_score: 1.0**
- Diagnosis: all three factor values = 1.0, so final score = 1.0

```
ROOT CAUSE OF SCORE COLLAPSE:
1. candidate_occs is constructed as: matched_occs | market_occ_ids | prog_targets.
   This means ALL candidates come from the union of those sets.
2. For any candidate drawn from prog_targets: progression=1.0 (by construction).
3. For any candidate drawn from market_occ_ids: market_opportunity=1.0 (binary presence).
4. student_fit, education_fit, skill_fit are unavailable for 4528 of 4529 students.
5. When only progression is available, renormalization makes it 100% of the score.
   progression = 1.0  →  renormalized weight = 1.0  →  final_score = 1.0.
6. When both market + progression are available, both = 1.0 →  final_score = 1.0.
7. The Top-5 is therefore purely occupation_id alphabetic ordering (tie-breaker).
CONCLUSION: The scoring model is correct in principle, but the available evidence
does NOT provide score differentiation. The ranking is a RANKING_COLLAPSE.
```

---
## 5. Ranking Collapse
- **RANKING_COLLAPSE detected:** True
- Students with fully tied Top-5: 4529 (100.0%)
- Recommendations determined by occupation_id tie-break: 22,645 (100.0%)
> 100.0% of students have all 5 recommendations with final_score=1.0. Top-5 selection is determined solely by the occupation_id ascending tiebreaker, not by evidence quality. The ranking is not meaningful.

---
## 6. Data Join Analysis
- Student IDs in recs valid: **True** (0 invalid)
- Occupation IDs in recs valid: **True** (0 invalid)
- Market occ IDs missing from canonical: 0
- Progression occ IDs missing from canonical: 0
- Students missing education_id: **4529** (all)
- Students missing skill evidence: **4529** (all)
> All student_id and occupation_id references in recommendations are valid. The join gap is VERTICAL: student_features.csv lacks education_id, skill fields. These fields were never populated because the source datasets do not contain them.

---
## 7. Recommended Fixes
| Priority | Fix | Description |
|----------|-----|-------------|
| 1 | Minimum-evidence gate | Require at least 2 usable factors before generating a recommendation. Prevents single-factor renormalization from inflating scores to 1.0. |
| 2 | Market opportunity scoring: replace binary with strength metric | Score market opportunity as normalized posting count per occupation (log scale), not as binary 1.0/0.5. This differentiates occupations within the candidate pool. |
| 3 | Progression scoring: replace binary with path depth | Score progression as 0.5 if occupation is a source AND target, 1.0 if it is only a target (higher career goal), 0.25 if it is only a source (entry-only). This replaces the current binary that makes prog_targets always 1.0. |
| 4 | GoGuide UI: capture student education during onboarding | The Phase 6 education_occupation_edges.csv is ready. The UI must ask for degree and field_of_study so education_fit can be calculated. |
| 5 | GoGuide UI: capture self-reported skills during onboarding | occupation_skill_edges.csv already has requirements. The UI must let students self-report skills so skill_fit overlap can be calculated. |
| 6 | Expand cluster→occupation mapping | 104 career clusters exist. More can be explicitly matched to canonical occupations without fuzzy matching by reviewing the UNMAPPED clusters in career_cluster_occupation_edges.csv. |
