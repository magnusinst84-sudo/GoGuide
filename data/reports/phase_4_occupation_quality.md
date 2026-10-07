# GoGuide Phase 4 — Occupation Normalization & Quality Report

**Project:** PRISM Engine (GoGuide / DataQuest 3.0)
**Timestamp:** 2026-10-07T20:23:48.726885
**Status:** Phase 4 Occupation Dictionary & Crosswalk Successfully Created

---
## Summary Metrics
- **Occupation Sources Audited:** 9 columns across 5 domains
- **Unique Raw Occupation Titles:** 43,469
- **Canonical GoGuide Occupations Created:** 39,068 (Deterministic IDs `GGOCC-00001`+)
- **ESCO Taxonomy Matches:** 2,191
- **O*NET SOC Matches:** 40
- **Both ESCO + O*NET Matched:** 0
- **Ambiguous Mappings:** 12,494
- **Unresolved Mappings:** 29,640

---
## Seniority Extraction Summary
- **Seniority Breakdown:** {
  "MANAGER": 5875,
  "MID": 29,
  "LEAD": 1654,
  "SENIOR": 4652,
  "PRINCIPAL": 355,
  "EXECUTIVE": 386,
  "ENTRY": 1198,
  "DIRECTOR": 838,
  "JUNIOR": 1312,
  "UNKNOWN": 28066
}
- **Technology Modifiers Extracted:** 3,014
- **Specializations Extracted:** 6,980

---
## Phase 4 Validation Suite Results
1. **Raw Layer Immutability:** PASSED (Zero raw files touched)
2. **ESCO URI Validation:** PASSED (0 invalid URIs detected)
3. **O*NET SOC Validation:** PASSED (0 invalid SOC codes detected)
4. **Deterministic Occupation IDs:** PASSED (39,068 unique IDs, 0 duplicate IDs)
5. **Raw Provenance Recoverability:** PASSED (All raw titles recoverable in crosswalk)

---
## Sample Canonical Occupation Dictionary Entries

| Occupation ID | Canonical Name | Family | Seniority | Tech Modifier | ESCO URI | O*NET SOC |
|---|---|---|---|---|---|---|
| `GGOCC-00001` | **Civil Site Engineer** | Software Development | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00002` | **Plant Tissue Culture Specialist** | UNKNOWN | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00003` | **Dermatologist** | UNKNOWN | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00004` | **Operations** | UNKNOWN | `MANAGER` | `None` | `None` | `None` |
| `GGOCC-00005` | **Radiologic And Ct/Mri Technologist** | UNKNOWN | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00006` | **Mlops Engineer** | Software Development | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00007` | **Business Intelligence Developer** | Software Development | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00008` | **Salesforce Developer** | Software Development | `UNKNOWN` | `Salesforce` | `None` | `None` |
| `GGOCC-00009` | **Urban And Regional Planner** | UNKNOWN | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00010` | **Plant Operations** | UNKNOWN | `MANAGER` | `None` | `None` | `None` |
| `GGOCC-00011` | **Game Programmer** | UNKNOWN | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00012` | **Loan Syndication Officer** | UNKNOWN | `UNKNOWN` | `None` | `None` | `None` |
| `GGOCC-00013` | **Wealth Management Advisor** | UNKNOWN | `UNKNOWN` | `None` | `http://data.europa.eu/esc...` | `None` |
| `GGOCC-00014` | **Logistics Operations** | UNKNOWN | `MANAGER` | `None` | `None` | `None` |
| `GGOCC-00015` | **Data Scientist** | Data & Analytics | `LEAD` | `None` | `http://data.europa.eu/esc...` | `None` |