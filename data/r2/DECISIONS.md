# R2 Closed Decisions

Rules agreed in session (2026-10-07). Apply these consistently to every career, every wave.
Reference this file before filling any of the fields below.

---

## 1. `entrance_required`

**Rule:** `true` when admission requires a score in a recognised entrance exam **and** seats are allocated by rank.

| Exam | entrance_required |
|---|---|
| JEE Main (NITs/GFTIs via JoSAA) | `true` |
| SRMJEEE, VITEEE | `true` |
| NEET (MBBS/BDS) | `true` |
| NATA (B.Arch) | `true` |
| Direct admission by board marks | `false` |
| Management quota / donation seat (no rank) | `false` |

---

## 2. `coaching` (pre-admission coaching cost, one-time INR)

**Rule:**

| Exam type | coaching value |
|---|---|
| JEE Main or JEE Advanced | `200000` |
| NEET (MBBS/BDS) | `200000` |
| Own-university entrance (SRMJEEE, VITEEE, NATA, etc.) | `50000` |
| No entrance / direct | `0` |

Rationale: JEE/NEET require 1-2 years of classroom coaching; institutional exams are coachable from free resources or short courses. Always label `coaching` as ESTIMATE and note this rule in `sources`.

---

## 3. `salary` growth assumption (y3 and y5 from y1)

**Rule:** ASSUMPTION — not sourced from any dataset. Always label y3 and y5 as ESTIMATE and write the formula in `sources`.

- `salary.y3 = round(salary.y1 * 1.30)` — uniform +30% over 2 years
- `salary.y5 = round(salary.y3 * 1.30)` — uniform +30% by year 5
- **Uniform multiplier; understates careers with steep late growth (e.g. MBBS after PG).**

Exception: for medicine/clinical careers use a flatter curve (internship/PG years mean low income at y3). Document the exception.

---

## 4. `automation_risk` differentiation

**These are RELATIVE JUDGMENT scores, not sourced values.** They are estimates based on the nature of the work in each cluster. Do not cite a URL for `automation_risk` unless you have opened a specific page and can quote an exact sentence that supports the number.

Different careers must have **different** values. Use these as starting anchors:

| Career cluster | automation_risk range | Rationale (judgment) |
|---|---|---|
| Software dev / CSE | 0.25–0.35 | Augmented, not replaced in near term |
| AI / Data Science | 0.20–0.25 | Builds automation tools; lower displacement risk |
| Biomedical Eng | 0.20–0.30 | Hardware/clinical component; hard to automate fully |
| Design (UX/B.Des) | 0.40–0.55 | Generative AI competes; human judgment still needed |
| MBBS / clinical | 0.10–0.20 | Regulatory and physical barriers; very low |
| Diploma / trades | 0.30–0.50 | Varies by branch |
| Nursing | 0.15–0.25 | Physical care; very low |
| Pharmacy | 0.35–0.50 | Dispensing automatable; clinical less so |

Always add to `estimated_fields`. In `sources`, write: "Relative judgment score per DECISIONS.md §4. Not sourced from a published index."

---

## 5. Representative institution type (private)

**Rule:** SRM Institute of Science and Technology (Kattankulathur campus) is the sole reference institution for all private engineering and technology careers.

- Fee basis: SRM Category 1 fee as published on the official fee page.
- Salary basis: NIRF 2024 median for SRM (IR-E-U-0473), all-branch UG 4-year.
- Note in `sources._note`: "Representative institution type: SRM Institute of Science and Technology, Category 1 fee."
- **VIT's NIRF 2024 median (₹9L UG, IR-E-U-0490) may be noted as an upper-bound sanity check only. It is never averaged into any field.**
- Do not use a "lower of two fees" rule. Do not average SRM and VIT.

For medicine (MBBS private): use a named private medical college (TBD when researching that career).

---

## 6. `salary.y1` basis (all careers)

**Rule:** `salary.y1 = median_fixed_CTC_INR / 12`, rounded to nearest integer.

- Prefer branch-specific placement report if the college publishes one.
- Fallback: NIRF median (all-branch), state the year and batch in `sources`.
- Do **not** use average or highest CTC; these are biased upwards by outliers.
- Government colleges: median of Trichy, Surathkal, Rourkela NIRF 2024 UG, 2022-23 batch.
- Private (engineering): SRM NIRF 2024 UG, 2022-23 batch.

---

## 7. `years` vs `years_to_first_income`

| Career | years | years_to_first_income | Note |
|---|---|---|---|
| B.Tech / B.Des / B.Arch | 4 | 4 | Placed at graduation |
| MBBS govt | 5.5 | 8+ | Internship (1 yr) + PG prep before independent practice |
| MBBS private | 5.5 | 6.5 | Same internship; private practice possible sooner |
| Diploma (polytechnic) | 3 | 3 | |
| B.Sc | 3 | 3 | |
| BCA | 3 | 3 | |
| B.Pharm | 4 | 4 | |
| BDS | 5 | 6 | Internship 1 yr |

---

*This file is owned by R2. Any change must be announced to R1, R3, R4 before it is committed.*
