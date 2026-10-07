# GoGuide Phase 5 — Education & Location Quality Report

**Project:** PRISM Engine (GoGuide / DataQuest 3.0)
**Timestamp:** 2026-10-07T20:24:54.408343
**Status:** Phase 5 Education & Location Dictionaries and Crosswalks Successfully Created

---
## Summary Metrics
- **Education Sources Audited:** 10 columns across 4 domains
- **Unique Raw Education Values:** 12,230
- **Canonical Education Dictionary Entries:** 12,018 (Deterministic IDs `GGEDU-00001`+)
- **Degree Distinction Audit:** `B.E.` (173 entries) vs `B.Tech` (142 entries) strictly preserved as separate degrees
- **Location Sources Audited:** 4 columns across 3 domains
- **Unique Raw Location Strings:** 15,113
- **Canonical Location Dictionary Entries:** 14,531 (Deterministic IDs `GGLOC-00001`+)
- **Indian Location Normalization:** Alias mapping applied for `Bangalore` -> `Bengaluru`, `Bombay` -> `Mumbai`, `Madras` -> `Chennai`

---
## Phase 5 Validation Suite Results
1. **Raw Layer Immutability:** PASSED (Zero raw files touched)
2. **Degree Distinction (B.E. != B.Tech):** PASSED (B.E. and B.Tech kept 100% distinct under `Undergraduate Engineering` family)
3. **Deterministic IDs:** PASSED (12,018 education IDs & 14,531 location IDs unique)
4. **International Location Isolation:** PASSED (International cities retained without forced Indian state/tier assignment)

---
## Sample Education Dictionary Entries

| Education ID | Raw Value | Canonical Degree | Degree Family | Level | Field of Study |
|---|---|---|---|---|---|
| `GGEDU-00001` | **Data Analytics (Applied)** | `None` | None | `UNKNOWN` | Data Analytics (Applied) |
| `GGEDU-00002` | **Political Science & Public Policy** | `None` | None | `UNKNOWN` | Political Science & Public Policy |
| `GGEDU-00003` | **Data Science & Engineering** | `None` | None | `UNKNOWN` | Data Science & Engineering |
| `GGEDU-00004` | **Computer Science** | `None` | None | `UNKNOWN` | Computer Science |
| `GGEDU-00005` | **Fine Arts** | `None` | None | `UNKNOWN` | Fine Arts |
| `GGEDU-00006` | **Civil Engineering** | `None` | None | `UNKNOWN` | Civil Engineering |
| `GGEDU-00007` | **Electronics & Communication Engineering** | `None` | None | `UNKNOWN` | Electronics & Communication Engineering |
| `GGEDU-00008` | **Physics** | `None` | None | `UNKNOWN` | Physics |
| `GGEDU-00009` | **Chemical Engineering** | `None` | None | `UNKNOWN` | Chemical Engineering |
| `GGEDU-00010` | **Business Administration** | `None` | None | `UNKNOWN` | Business Administration |