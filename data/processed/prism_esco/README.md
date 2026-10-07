# prism_esco

## Purpose
Official European Skills, Competences, Qualifications and Occupations (ESCO) taxonomy dataset (v1.2). Provides the authoritative international classification bridge for occupations, skill concepts, ISCO-08 groups, digital competences, green skills, and transversal skills within the PRISM Engine.

## Quick Summary

| File Name | Format | Rows | Columns | Primary Key / Identifier | Key Fields |
|---|---|---|---|---|---|
| `ISCOGroups_en.csv` | CSV | 619 | 8 | `conceptUri` | `code`, `preferredLabel`, `conceptType` |
| `broaderRelationsOccPillar_en.csv` | CSV | 3,648 | 6 | `(conceptUri, broaderUri)` | `conceptType`, `conceptUri`, `broaderType`, `broaderUri` |
| `broaderRelationsSkillPillar_en.csv` | CSV | 20,819 | 6 | `(conceptUri, broaderUri)` | `conceptType`, `conceptUri`, `broaderType`, `broaderUri` |
| `conceptSchemes_en.csv` | CSV | 20 | 7 | `conceptSchemeUri` | `conceptSchemeUri`, `title`, `description` |
| `dictionary_en.csv` | CSV | 160 | 4 | `(filename, data header)` | `filename`, `data header`, `property`, `description` |
| `digCompSkillsCollection_en.csv` | CSV | 25 | 10 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel` |
| `digitalSkillsCollection_en.csv` | CSV | 1,284 | 10 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel` |
| `greenShareOcc_en.csv` | CSV | 3,590 | 5 | `conceptUri` | `conceptUri`, `preferredLabel`, `greenShare` |
| `greenSkillsCollection_en.csv` | CSV | 629 | 10 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel` |
| `languageSkillsCollection_en.csv` | CSV | 359 | 10 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel` |
| `occupationSkillRelations_en.csv` | CSV | 126,051 | 6 | `(occupationUri, skillUri)` | `occupationUri`, `relationType`, `skillUri`, `skillType` |
| `occupations_en.csv` | CSV | 3,043 | 15 | `conceptUri` | `conceptUri`, `preferredLabel`, `iscoGroup`, `code`, `description` |
| `researchOccupationsCollection_en.csv` | CSV | 122 | 8 | `conceptUri` | `conceptUri`, `preferredLabel`, `description` |
| `researchSkillsCollection_en.csv` | CSV | 40 | 10 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel` |
| `skillGroups_en.csv` | CSV | 640 | 11 | `conceptUri` | `conceptUri`, `preferredLabel`, `code`, `description` |
| `skillSkillRelations_en.csv` | CSV | 5,818 | 5 | `(originalSkillUri, relatedSkillUri)` | `originalSkillUri`, `relationType`, `relatedSkillUri` |
| `skillsHierarchy_en.csv` | CSV | 640 | 14 | `Level 0 URI` | `Level 0 preferred term`, `Level 1 preferred term`, `Level 0 code` |
| `skills_en.csv` | CSV | 13,960 | 13 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel`, `description` |
| `transversalSkillsCollection_en.csv` | CSV | 95 | 10 | `conceptUri` | `conceptUri`, `preferredLabel`, `skillType`, `reuseLevel` |

---

## Detailed File Inventory

### Main Entity Tables

#### 1. `occupations_en.csv`
- **Rows:** 3,043 | **Columns:** 15 | **Primary Key:** `conceptUri`
- **Description:** Core ESCO occupation concepts with ISCO-08 group mapping and descriptions.
- **Key Columns:** `conceptUri` (URI), `iscoGroup` (URI), `preferredLabel` (Text), `altLabels` (Text), `description` (Text), `code` (ISCO-08 code).
- **Null Stats:** `hiddenLabels` (99.74% null), `scopeNote` (89.81% null), `definition` (99.74% null).

#### 2. `skills_en.csv`
- **Rows:** 13,960 | **Columns:** 13 | **Primary Key:** `conceptUri`
- **Description:** Complete dictionary of 13,960 ESCO skills and knowledge concepts.
- **Key Columns:** `conceptUri` (URI), `skillType` (knowledge vs skill/competence), `reuseLevel` (sector-specific, transversal, occupation-specific), `preferredLabel`, `description`.
- **Null Stats:** `definition` (99.99% null), `scopeNote` (98.31% null), `hiddenLabels` (98.9% null).

#### 3. `occupationSkillRelations_en.csv`
- **Rows:** 126,051 | **Columns:** 6 | **Primary Key:** Composite `(occupationUri, skillUri)`
- **Description:** Essential and optional skill requirements mapping occupations to skills.
- **Key Columns:** `occupationUri` (FK → `occupations_en`), `relationType` (`essential` / `optional`), `skillUri` (FK → `skills_en`), `skillType`.

#### 4. `ISCOGroups_en.csv`
- **Rows:** 619 | **Columns:** 8 | **Primary Key:** `conceptUri`
- **Description:** Official ISCO-08 international standard classification of occupations hierarchy.
- **Key Columns:** `conceptUri`, `code` (e.g., `2512`), `preferredLabel`, `description`.

---

### Special Collections & Hierarchies

#### 5. `broaderRelationsOccPillar_en.csv`
- **Rows:** 3,648 | **Columns:** 6 | **PK:** `(conceptUri, broaderUri)`
- Hierarchical parent-child links between ESCO occupation concepts.

#### 6. `broaderRelationsSkillPillar_en.csv`
- **Rows:** 20,819 | **Columns:** 6 | **PK:** `(conceptUri, broaderUri)`
- Hierarchical parent-child relations between ESCO skills and skill groups.

#### 7. `skillGroups_en.csv` & `skillsHierarchy_en.csv`
- **`skillGroups_en.csv`:** 640 rows, 11 cols | **PK:** `conceptUri`. ESCO skill group categories.
- **`skillsHierarchy_en.csv`:** 640 rows, 14 cols. 4-level taxonomy tree (`Level 0` to `Level 3`).

#### 8. Special Skill Collections
- **`digCompSkillsCollection_en.csv`:** 25 digital competence framework skills.
- **`digitalSkillsCollection_en.csv`:** 1,284 specialized digital and ICT skills.
- **`greenSkillsCollection_en.csv`:** 629 green/environmental sustainability skills.
- **`greenShareOcc_en.csv`:** 3,590 occupations with green transition score (`greenShare`).
- **`languageSkillsCollection_en.csv`:** 359 language proficiency skills.
- **`transversalSkillsCollection_en.csv`:** 95 cross-cutting soft/transversal skills.
- **`researchSkillsCollection_en.csv`:** 40 academic and research skills.
- **`researchOccupationsCollection_en.csv`:** 122 academic/research occupation concepts.

#### 9. Auxiliary Files
- **`conceptSchemes_en.csv`:** 20 rows. Taxonomy scheme metadata.
- **`dictionary_en.csv`:** 160 rows. Column header definition lookup dictionary.
- **`skillSkillRelations_en.csv`:** 5,818 rows. Direct inter-skill relationships.

---

## PRISM Integration / Usage

The ESCO dataset serves as PRISM's primary **Standardization & Normalization Bridge**:

1. **Synthetic Data Enrichment:** `prism_education_career/occupations.csv.esco_occupation_uri` links directly to `occupations_en.csv.conceptUri`.
2. **Skill Normalization:** Raw skill titles extracted from job descriptions or resumes are mapped to `skills_en.csv.preferredLabel` and `conceptUri`.
3. **Green & Digital Skill Indexing:** Enables PRISM to calculate "Green Transition Scores" and "Digital Maturity Scores" for student pathways using `greenShareOcc_en.csv` and `digitalSkillsCollection_en.csv`.

---

## Data Quality & Caveats

1. **Completeness:** 100% valid CSV headers and UTF-8 encoding.
2. **European Context:** Derived from EU ESCO classification. Terminology may use European spellings and concepts that require localization for the Indian job market.
3. **Null Values:** Fields such as `definition`, `scopeNote`, and `hiddenLabels` have >90% null counts across major tables as per standard ESCO exports.

---

## Notes (preserved)

> **Preserved Notes & Licensing:**
> - ESCO dataset © European Union, 2024. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0).
> - **Filename Note:** Previous human notes referred to simplified filenames (`occupations.csv`, `skills.csv`, `occupation_skill_relations.csv`). The actual canonical files on disk are `occupations_en.csv`, `skills_en.csv`, `occupationSkillRelations_en.csv`, etc.
