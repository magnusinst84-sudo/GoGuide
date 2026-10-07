# Phase 7.2.1 — Recommendation Integrity Sanity Audit

**Verdict:** `PASS`  
**Hard failures:** 0  
**Warnings:** 0  

---
## Checks Summary

| Check | Result |
|-------|--------|
| Raw Integrity | ✅ PASS |
| Candidate Accounting | ✅ PASS |
| Score Reconciliation | ✅ PASS |
| Min-Evidence Gate | ✅ PASS |
| Market Provenance | ✅ PASS |
| Progression Provenance | ✅ PASS |
| Top-5 Diversity | ✅ PASS |
| Provenance Sample | ✅ PASS |
| Determinism | ✅ PASS |

---
## Score Distribution

- **Unique scores:** 19  
- **Min / Max / Mean / Median:** 0.4202 / 0.9963 / 0.6081 / 0.6087  
- **P25 / P75:** 0.5467 / 0.671  
- **Avg unique scores per student:** 5.0  

19 unique score values arise because: the engine uses log1p-normalised continuous market and progression signals. Each scored occupation gets a real-valued market_opportunity and/or progression score. The factor combinations present are: ['market_opportunity|progression', 'student_fit|market_opportunity', 'student_fit|market_opportunity|progression', 'student_fit|progression']. Scores are rounded to 4 decimal places. The exact number of unique scores reflects the distinct log1p-normalised count combinations across the 203-occupation market universe and 49-occupation progression universe.

---
## Candidate Accounting

- Candidate universe: 259 occupations × 4529 students  
- Each student evaluates up to 259 candidate occupations (44 cluster-match + 203 market-match + 49 progression). For 4529 students that is 4529×259 = 1,173,011 evaluations maximum. Candidates with evidence_count < 2 become INSUFFICIENT_EVIDENCE and are excluded from the ranked Top-K output. Reported INSUFFICIENT: 978,273. The actual arithmetic: 1000918 total evaluations (some students share the same candidate universe with zero overlap in their clusters).  

---
## Progression Reconciliation

Phase 7.2 report stated '43 edges across 31 occupations'. Direct count of non-self-loop edges in career_progression_edges.csv: 43. Unique occupations (source ∪ target): 49. Unique source occupations: 31, unique targets: 31. The '31 occupations' figure in the Phase 7.2 report appears to count unique source occupations (= 31) or unique targets (= 31), while the true unique-occupation union is 49. Self-loops: 0.  

---
## Issues Found

*No hard failures.*  

---
## Warnings

*No warnings.*  
