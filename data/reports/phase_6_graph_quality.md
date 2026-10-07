# GoGuide Phase 6 — Unified Intelligence Graph Report

**Project:** PRISM Engine (GoGuide / DataQuest 3.0)
**Timestamp:** 2026-10-07T21:03:44.477407
**Status:** SUCCESS — all validation checks passed

---
## Entity Counts
- **Education:** 12,018
- **Occupation:** 39,068 (ALL canonical)
- **Skill:** 238,774 (ALL canonical)
- **Location:** 14,531
- **Industry:** 61

---
## Edge Counts
- **Education→Occupation:** 870
- **Occupation→Skill:** 708
- **Occupation→Industry:** 240
- **Career Progression:** 43
- **Market Evidence (occupation_market_edges.csv):** 22,350 (5,000 SYNTHETIC_PROTOTYPE / 17,350 REAL_JOB_FEED)
- **Career Cluster (CAREER_CLUSTER_LABEL):** 104

---
## Market Mapping Metrics
| Metric | Value |
|--------|-------|
| Total postings | 22,350 |
| Mapped (MATCHED) | 6,815 (30.49%) |
| Ambiguous | 2,083 |
| Unmapped | 13,452 |
| Unique titles total | 6,436 |
| Unique titles MATCHED | 285 |
| Unique titles AMBIGUOUS | 868 |
| Unique titles UNMAPPED | 5,283 |

---
## Canonical Graph Export
- **Nodes:** 289,921
- **Structural Edges:** 1,861
- **Market edges in graph:** No — market evidence is a separate layer

---
## Validation Checks
| Check | Status |
|-------|--------|
| Raw Integrity Pre | PASSED |
| Raw Integrity Post | PASSED |
| Entity Primary Keys | PASSED |
| Education Occupation Foreign Keys | PASSED |
| Occupation Skill Foreign Keys | PASSED |
| Occupation Industry Foreign Keys | PASSED |
| Progression Foreign Keys | PASSED |
| Market Foreign Keys | PASSED |
| Duplicate Edges | PASSED |
| Progression Self Loops | PASSED |
| Fabricated Ids | PASSED |

---
## Integrity Summary
- Self-loops removed: 13
- Duplicate progression edges removed: 5
- Invalid EO edges: 0
- Invalid OS edges: 0
- Invalid OI edges: 0
- Invalid progression edges: 0
- Invalid market occupation IDs: 0
- Adzuna currency field: NOT_AVAILABLE (no currency column in source)