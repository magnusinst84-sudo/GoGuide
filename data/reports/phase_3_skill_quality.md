# GoGuide Phase 3 — Skill Normalization & Quality Report

**Project:** PRISM Engine (GoGuide / DataQuest 3.0)
**Timestamp:** 2026-10-07T20:20:10.635689
**Status:** Phase 3 Skill Dictionary & Crosswalk Successfully Created

---
## Summary Metrics
- **Skill-Bearing Sources Audited:** 9 columns across 6 domains
- **Unique Raw Skill Strings:** 246,518
- **Unique Normalized Skills:** 240,144
- **Canonical GoGuide Skills Created:** 238,774 (Deterministic IDs `GGSKILL-00001`+)
- **ESCO Taxonomy Matches:** 29,040 (5.78% crosswalk coverage)
- **Ambiguous Mappings:** 28,345
- **Unresolved Mappings:** 443,721
- **Combined Skills Split:** 302
- **Combined Skills Preserved Unsplit:** 27,241

---
## Phase 3 Validation Suite Results
1. **Raw Layer Immutability:** FAILED (Zero raw files touched)
2. **PII Isolation:** PASSED (No PII introduced in dictionaries/crosswalks)
3. **Stable Skill IDs:** PASSED (238,774 unique IDs, 0 duplicate IDs)
4. **ESCO URI Integrity:** PASSED (0 invalid URIs detected; 100% URIs validated against ESCO master taxonomy)
5. **Raw Provenance Recoverability:** PASSED (All raw skill strings linked in crosswalk)

---
## Sample Canonical Skill Dictionary Entries

| Skill ID | Canonical Skill Name | Skill Category | ESCO Status | Notes |
|---|---|---|---|---|
| `GGSKILL-00001` | **Continuous Deployment (CD)** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00002` | **Email Marketing Automation** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00003` | **Clinical Biochemistry Diagnostics** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00004` | **Operations Capacity Planning** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00005` | **network standards** | Technical Skill | `MATCHED` | Matched ESCO altLabel synonym |
| `GGSKILL-00006` | **Avionics & Flight Control Systems** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00007` | **Cisco Certified Network Associate (CCNA)** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00008` | **Clinical Diagnosis** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00009` | **Legal Research & Precedent Analysis** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00010` | **Human Resources Talent Acquisition** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00011` | **Bash / Shell Scripting** | Technical Skill | `AMBIGUOUS` | Ambiguous slash expression preserved unsplit for manual review |
| `GGSKILL-00012` | **Python (computer programming)** | Technical Skill | `MATCHED` | Matched ESCO altLabel synonym |
| `GGSKILL-00013` | **Welding Metallurgy & Inspection (NDT)** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00014` | **Strategic Vendor Procurement** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |
| `GGSKILL-00015` | **Public Relations & Media Outreach** | Technical Skill | `UNRESOLVED` | Domain-specific or custom skill string not mapped in ESCO taxonomy |