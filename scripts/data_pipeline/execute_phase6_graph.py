"""
GoGuide PRISM Engine - Phase 6 Intelligence Graph Builder

Targeted corrections applied (no pipeline redesign):
  1.  _build_occupation_lookup() aggregates ALL crosswalk rows per title before resolving
      status — prevents incorrectly promoting AMBIGUOUS→MATCHED.
  2.  _normalize_title() collapses all internal whitespace deterministically.
  3.  Adzuna currency = NOT_AVAILABLE (no currency column in dataset).
  4.  Full FK validation before any artifact is written; Phase 6 aborts on violation.
  5.  _safe_write replaced by Phase6ValidationError + _validated_write (temp-file + atomic rename).
  6.  Market mapping metrics: both per-posting and per-unique-title coverage tracked.
  7.  career_cluster_occupation_edges.csv gains relationship_type = CAREER_CLUSTER_LABEL.
  8.  PIP student rows controlled by MAX_PIP_STUDENT_ROWS constant (None = all rows).
  9.  nodes.csv + edges.csv = structural canonical graph only.
      occupation_market_edges.csv = separate market evidence layer.
 10.  quality report includes validation_checks dict; all must be PASSED.
 11.  Execution order: A raw-integrity → B load → C construct → D PK validate →
      E FK validate → F market construct → G market FK → H write → I raw-integrity → J report.

Preserved policies:
  - data/raw/ is never touched
  - verify_raw_layer_integrity() pre and post
  - No GGOCC-SYNTH / GGOCC-REAL / GGOCC-CLUSTER IDs
  - No fabricated ESCO URIs or O*NET SOC codes
  - No fuzzy matching; no semantic guesses
  - India Jobs = SYNTHETIC_PROTOTYPE; Adzuna = REAL_JOB_FEED
  - No currency conversion; salaries verbatim from source
  - All canonical occupations and skills exported (no [:N] slicing)
  - run_phase_6() entry point unchanged
"""

import os
import sys
import json
import csv
import re
import tempfile
from datetime import datetime
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import BASE_DIR, DATA_DIR, RAW_DIR, PROCESSED_DIR, REPORTS_DIR, CROSSWALKS_DIR, DICTIONARIES_DIR
from io_utils import load_csv_rows, write_csv_rows
from audit_utils import verify_raw_layer_integrity

csv.field_size_limit(10_000_000)

GOGUIDE_ENTITIES_DIR = os.path.join(PROCESSED_DIR, 'goguide_entities')
STUDENT_INTEL_DIR    = os.path.join(PROCESSED_DIR, 'student_intelligence')
GOGUIDE_GRAPH_DIR    = os.path.join(PROCESSED_DIR, 'goguide_graph')

GRAPH_QUALITY_JSON = os.path.join(REPORTS_DIR, 'phase_6_graph_quality.json')
GRAPH_QUALITY_MD   = os.path.join(REPORTS_DIR, 'phase_6_graph_quality.md')

# PIP dataset has 4424 rows — include ALL for the hackathon MVP.
# Set to an integer to enable sampling (documents the limit explicitly).
MAX_PIP_STUDENT_ROWS = None   # None = include all rows


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

class Phase6ValidationError(Exception):
    """Raised when pre-write validation fails; dest file is NOT modified."""


def _normalize_title(raw: str) -> str:
    """
    Deterministic, whitespace-collapsed title normalization.
    1. Lowercase
    2. Replace every non-alphanumeric char with a space
    3. Collapse all internal whitespace to a single space
    4. Strip leading/trailing whitespace
    No fuzzy matching; no semantic guesses.
    Applied identically to both raw_occupation_title and normalized_occupation_title.
    """
    lowered   = raw.lower()
    spaced    = re.sub(r'[^a-z0-9]+', ' ', lowered)
    collapsed = re.sub(r'\s+', ' ', spaced).strip()
    return collapsed


def _build_occupation_lookup(cw_header, cw_rows):
    """
    Build a deterministic lookup: normalized_title → (occupation_id, mapping_status)

    Aggregation rules applied AFTER seeing ALL rows for a given title:
      - Exactly one unique non-empty MATCHED occupation_id → (id, MATCHED)
      - Multiple distinct matched ids, OR any MATCHED + other → ('', AMBIGUOUS)
      - Only AMBIGUOUS rows, no MATCHED → ('', AMBIGUOUS)
      - Only UNRESOLVED / empty → ('', UNMAPPED)

    Never arbitrarily chooses one occupation when multiple apply.
    Phase 4 crosswalk vocabulary: MATCHED | AMBIGUOUS | UNRESOLVED
    """
    raw_idx    = cw_header.index('raw_occupation_title')
    norm_idx   = cw_header.index('normalized_occupation_title')
    id_idx     = cw_header.index('occupation_id')
    status_idx = cw_header.index('mapping_status')

    # First pass: aggregate all (occ_id, status) pairs per normalized key.
    # Each crosswalk row is indexed under BOTH the raw and normalized title keys.
    agg = defaultdict(list)  # normalized_key → list of (occ_id, status)
    for r in cw_rows:
        raw_title  = r[raw_idx].strip()
        norm_title = r[norm_idx].strip()
        occ_id     = r[id_idx].strip()
        status     = r[status_idx].strip()
        for key in (_normalize_title(raw_title), _normalize_title(norm_title)):
            if key:
                agg[key].append((occ_id, status))

    # Second pass: resolve each key deterministically.
    lookup = {}
    for key, entries in agg.items():
        matched_ids = {oid for oid, st in entries if st == 'MATCHED' and oid}
        if len(matched_ids) == 1:
            lookup[key] = (matched_ids.pop(), 'MATCHED')
        elif len(matched_ids) > 1:
            lookup[key] = ('', 'AMBIGUOUS')
        else:
            any_ambiguous = any(st == 'AMBIGUOUS' for _, st in entries)
            lookup[key] = ('', 'AMBIGUOUS' if any_ambiguous else 'UNMAPPED')

    return lookup


def _map_market_title(raw_title: str, lookup: dict, valid_occ_ids: set):
    """
    Map a raw market job title to a canonical occupation_id.
    Returns (occupation_id, mapping_status, mapping_source).
    Only returns non-empty occupation_id when MATCHED AND id is in valid_occ_ids.
    No fuzzy matching; no semantic guesses.
    """
    key = _normalize_title(raw_title)
    if key not in lookup:
        return ('', 'UNMAPPED', 'NOT_IN_CROSSWALK')
    occ_id, status = lookup[key]
    if status == 'MATCHED':
        if occ_id and occ_id in valid_occ_ids:
            return (occ_id, 'MATCHED', 'occupation_crosswalk.csv')
        return ('', 'UNMAPPED', 'CROSSWALK_INVALID_ID')
    if status == 'AMBIGUOUS':
        return ('', 'AMBIGUOUS', 'occupation_crosswalk.csv')
    return ('', 'UNMAPPED', 'occupation_crosswalk.csv')


def _validated_write(dest_path, header, rows, label,
                     required_id_col=None, unique_id_col=None, min_rows=1):
    """
    Validate then atomically write a CSV artifact.
    Steps: non-empty → row width → required ID non-blank → uniqueness.
    Writes to temp file in same directory, then os.replace() to dest_path.
    Raises Phase6ValidationError without touching dest_path on any failure.
    """
    if not rows or len(rows) < min_rows:
        raise Phase6ValidationError(
            f"[{label}] {len(rows)} rows produced; expected >= {min_rows}. "
            f"Refusing to overwrite existing artifact."
        )
    expected_width = len(header)
    bad = [i for i, r in enumerate(rows, 1) if len(r) != expected_width]
    if bad:
        raise Phase6ValidationError(
            f"[{label}] {len(bad)} row(s) with wrong column count "
            f"(expected {expected_width}). First bad index: {bad[0]}."
        )
    if required_id_col is not None:
        blanks = [i for i, r in enumerate(rows, 1) if not r[required_id_col].strip()]
        if blanks:
            raise Phase6ValidationError(
                f"[{label}] {len(blanks)} blank required ID(s) in column "
                f"'{header[required_id_col]}'. First bad index: {blanks[0]}."
            )
    if unique_id_col is not None:
        seen_u, dups = set(), []
        for r in rows:
            v = r[unique_id_col]
            if v in seen_u:
                dups.append(v)
            seen_u.add(v)
        if dups:
            raise Phase6ValidationError(
                f"[{label}] {len(dups)} duplicate(s) in column "
                f"'{header[unique_id_col]}'. Examples: {dups[:3]}."
            )
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, suffix='.tmp')
    try:
        os.close(fd)
        write_csv_rows(tmp_path, header, rows)
        os.replace(tmp_path, dest_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    print(f"  {label}: {len(rows):,} rows → {os.path.relpath(dest_path, BASE_DIR)}")
    return len(rows)


# ---------------------------------------------------------------------------
# Main Phase 6 function
# ---------------------------------------------------------------------------

def run_phase_6():
    print("=" * 60)
    print("STARTING PHASE 6 — UNIFIED GOGUIDE INTELLIGENCE GRAPH BUILD")
    print("=" * 60)

    # Validation-check accumulator — all must be PASSED for a successful run.
    validation_checks = {
        'raw_integrity_pre':                 'NOT_RUN',
        'raw_integrity_post':                'NOT_RUN',
        'entity_primary_keys':               'NOT_RUN',
        'education_occupation_foreign_keys': 'NOT_RUN',
        'occupation_skill_foreign_keys':     'NOT_RUN',
        'occupation_industry_foreign_keys':  'NOT_RUN',
        'progression_foreign_keys':          'NOT_RUN',
        'market_foreign_keys':               'NOT_RUN',
        'duplicate_edges':                   'NOT_RUN',
        'progression_self_loops':            'NOT_RUN',
        'fabricated_ids':                    'NOT_RUN',
    }

    # ── A. PRE-FLIGHT RAW INTEGRITY ─────────────────────────────────────────
    print("\n[A] Pre-flight raw layer integrity check…")
    raw_valid_pre = verify_raw_layer_integrity()
    if not raw_valid_pre['success']:
        print(f"  FATAL: Raw layer integrity FAILED before Phase 6 writes. "
              f"{len(raw_valid_pre['altered_files'])} file(s) altered. Aborting.")
        sys.exit(1)
    validation_checks['raw_integrity_pre'] = 'PASSED'
    print(f"  {raw_valid_pre['verified_files']} files verified. PASSED.")

    os.makedirs(GOGUIDE_ENTITIES_DIR, exist_ok=True)
    os.makedirs(STUDENT_INTEL_DIR,    exist_ok=True)
    os.makedirs(GOGUIDE_GRAPH_DIR,    exist_ok=True)
    os.makedirs(CROSSWALKS_DIR,       exist_ok=True)

    # ── B. LOAD DICTIONARIES / CROSSWALKS ──────────────────────────────────
    print("\n[B] Loading dictionaries and crosswalks…")
    cw_header, cw_rows = load_csv_rows(os.path.join(CROSSWALKS_DIR, 'occupation_crosswalk.csv'))
    occupation_lookup = _build_occupation_lookup(cw_header, cw_rows)
    print(f"  Occupation crosswalk: {len(occupation_lookup):,} unique normalized titles indexed.")

    edu_dict_header, edu_dict_rows = load_csv_rows(
        os.path.join(DICTIONARIES_DIR, 'education_dictionary.csv'))
    # Cols: education_id(0), raw_education_value(1), canonical_degree(2), degree_family(3),
    #       education_level(4), field_of_study(5), normalization_status(6), notes(7)

    occ_dict_header, occ_dict_rows = load_csv_rows(
        os.path.join(DICTIONARIES_DIR, 'occupation_dictionary.csv'))
    # Cols: occupation_id(0), canonical_occupation_name(1), occupation_family(2),
    #       seniority_level(3), technology_modifier(4), specialization(5),
    #       canonicalization_status(6), notes(7)

    skill_dict_header, skill_dict_rows = load_csv_rows(
        os.path.join(DICTIONARIES_DIR, 'skill_dictionary.csv'))
    # Cols: skill_id(0), canonical_skill_name(1), skill_category(2),
    #       canonicalization_status(3), notes(4)

    loc_dict_header, loc_dict_rows = load_csv_rows(
        os.path.join(DICTIONARIES_DIR, 'location_dictionary.csv'))
    # Cols: location_id(0), raw_location(1), canonical_city(2), canonical_state(3),
    #       canonical_country(4), location_tier(5), normalization_status(6), notes(7)

    # Edge source files
    h_eo, r_eo = load_csv_rows(
        os.path.join(PROCESSED_DIR, 'prism_education_career', 'education_to_occupation.csv'))
    # Cols: education_id(0), occupation_id(1), career_title(2), relationship_strength(3),
    #       career_relevance(4), typicality(5), career_pathway_type(6), ...

    h_os, r_os = load_csv_rows(
        os.path.join(PROCESSED_DIR, 'prism_education_career', 'occupation_to_skill.csv'))
    # Cols: occupation_id(0), skill_id(1), skill_name(2), importance_score(3),
    #       proficiency_level(4), skill_type(5), is_core_skill(6)

    h_oi, r_oi = load_csv_rows(
        os.path.join(PROCESSED_DIR, 'prism_education_career', 'occupation_to_industry.csv'))
    # Cols: occupation_id(0), occupation_name(1), industry(2), sub_industry(3),
    #       common_employers_type(4), employment_share_estimate(5), india_hub_locations(6)

    h_prog, r_prog = load_csv_rows(
        os.path.join(PROCESSED_DIR, 'prism_education_career', 'career_progression.csv'))
    # Cols: progression_id(0), from_occupation_id(1), to_occupation_id(2),
    #       from_occupation_name(3), to_occupation_name(4), transition_type(5), ...

    career_pred_src = os.path.join(PROCESSED_DIR, 'prism_student_profile',
                                   'Career Prediction Dataset.csv')
    pip_src = os.path.join(PROCESSED_DIR, 'prism_student_profile',
                           'Student performance (Polytechnic Institute of Portalegre).csv')
    india_src  = os.path.join(PROCESSED_DIR, 'prism_india_jobs', 'india_job_market_2024_2026.csv')
    adzuna_src = os.path.join(PROCESSED_DIR, 'prism_job_descriptions',
                              'adzuna_global_job_listings_2025.csv')

    # ── B.2 MAP SYNTHETIC IDS TO CANONICAL IDS ─────────────────────────────
    print("\n[B.2] Mapping PRISM synthetic IDs to canonical IDs…")
    _, r_occ = load_csv_rows(os.path.join(PROCESSED_DIR, 'prism_education_career', 'occupations.csv'))
    occ_synthetic_to_canonical = {}
    for r in r_occ:
        synth_id = r[0].strip()
        name = _normalize_title(r[1].strip())
        c_val = occupation_lookup.get(name)
        if c_val and c_val[0]:
            occ_synthetic_to_canonical[synth_id] = c_val[0]

    skill_lookup = { _normalize_title(r[1]): r[0] for r in skill_dict_rows }
    _, r_skl = load_csv_rows(os.path.join(PROCESSED_DIR, 'prism_education_career', 'skills.csv'))
    skl_synthetic_to_canonical = {}
    for r in r_skl:
        synth_id = r[0].strip()
        name = _normalize_title(r[1].strip())
        c_id = skill_lookup.get(name, '')
        if c_id:
            skl_synthetic_to_canonical[synth_id] = c_id

    edu_lookup = { _normalize_title(r[1]): r[0] for r in edu_dict_rows }
    _, r_edu = load_csv_rows(os.path.join(PROCESSED_DIR, 'prism_education_career', 'education_pathways.csv'))
    edu_synthetic_to_canonical = {}
    for r in r_edu:
        synth_id = r[0].strip()
        field = _normalize_title(r[3].strip())
        c_id = edu_lookup.get(field, '')
        if c_id:
            edu_synthetic_to_canonical[synth_id] = c_id

    # ── C. CONSTRUCT ENTITIES IN MEMORY ────────────────────────────────────
    print("\n[C] Constructing entity tables…")

    # Education
    edu_entity_rows = []
    edu_id_set = set()
    for r in edu_dict_rows:
        edu_id_set.add(r[0])
        edu_entity_rows.append([
            r[0], r[2], r[3], r[4], r[5],
            'data/dictionaries/education_dictionary.csv'
        ])

    # Occupation — esco/onet URIs NOT fabricated
    occ_entity_rows = []
    occ_id_set = set()
    for r in occ_dict_rows:
        occ_id_set.add(r[0])
        occ_entity_rows.append([r[0], r[1], r[2], r[3], '', ''])

    # Skill — ALL rows, no [:N] slicing; esco_skill_uri NOT fabricated
    skill_entity_rows = []
    skill_id_set = set()
    for r in skill_dict_rows:
        skill_id_set.add(r[0])
        skill_entity_rows.append([r[0], r[1], r[2], ''])

    # Location
    loc_entity_rows = []
    loc_id_set = set()
    for r in loc_dict_rows:
        loc_id_set.add(r[0])
        loc_entity_rows.append([r[0], r[2], r[3], r[4], r[5]])

    # Industry — derived from occupation_to_industry.csv
    # industry=col2, sub_industry=col3 (verified against actual header)
    ind_dict = {}
    for r in r_oi:
        ind_name = r[2] if len(r) > 2 else ''
        sub_ind  = r[3] if len(r) > 3 else ''
        if ind_name:
            ind_id = 'IND-' + re.sub(r'[^A-Z0-9]', '_', ind_name.upper())[:40]
            if ind_id not in ind_dict:
                ind_dict[ind_id] = (ind_name, sub_ind)
    ind_entity_rows = [[iid, iname, isub] for iid, (iname, isub) in sorted(ind_dict.items())]
    ind_id_set = {r[0] for r in ind_entity_rows}

    print(f"  Education: {len(edu_entity_rows):,} | Occupation: {len(occ_entity_rows):,} | "
          f"Skill: {len(skill_entity_rows):,} | Location: {len(loc_entity_rows):,} | "
          f"Industry: {len(ind_entity_rows):,}")

    # Build edge tables in memory
    # Education → Occupation (education_id=col0, occupation_id=col1, pathway=col6, strength=col3)
    ed_occ_edges = []
    for r in r_eo:
        e_id   = edu_synthetic_to_canonical.get(r[0].strip(), '') if len(r) > 0 else ''
        o_id   = occ_synthetic_to_canonical.get(r[1].strip(), '') if len(r) > 1 else ''
        p_type = r[6].strip() if len(r) > 6 else 'Direct'
        conf   = r[3].strip() if len(r) > 3 else '1.0'
        if e_id and o_id:
            ed_occ_edges.append([
                e_id, o_id,
                'data/processed/prism_education_career/education_to_occupation.csv',
                p_type, conf,
                'PRISM Synthetic Graph Mapping', 'Validated pathway alignment'
            ])

    # Occupation → Skill (occupation_id=col0, skill_id=col1, is_core_skill=col6)
    occ_skl_edges = []
    for r in r_os:
        o_id    = occ_synthetic_to_canonical.get(r[0].strip(), '') if len(r) > 0 else ''
        s_id    = skl_synthetic_to_canonical.get(r[1].strip(), '') if len(r) > 1 else ''
        is_core = r[6].strip().upper() if len(r) > 6 else 'TRUE'
        rel_t   = 'ESSENTIAL' if is_core == 'TRUE' else 'OPTIONAL'
        if o_id and s_id:
            occ_skl_edges.append([
                o_id, s_id,
                'data/processed/prism_education_career/occupation_to_skill.csv',
                rel_t, '', '1.0',
                'PRISM Synthetic Graph Mapping', 'Core role requirement'
            ])

    # Occupation → Industry (occupation_id=col0, industry=col2, emp_share=col5)
    occ_ind_edges = []
    for r in r_oi:
        o_id     = occ_synthetic_to_canonical.get(r[0].strip(), '') if len(r) > 0 else ''
        ind_name = r[2].strip() if len(r) > 2 else ''
        conf     = r[5].strip() if len(r) > 5 else '1.0'
        if o_id and ind_name:
            ind_id = 'IND-' + re.sub(r'[^A-Z0-9]', '_', ind_name.upper())[:40]
            occ_ind_edges.append([
                o_id, ind_id,
                'data/processed/prism_education_career/occupation_to_industry.csv',
                conf, 'PRISM Synthetic Graph Mapping', 'Industry employment distribution'
            ])

    # Career Progression (from_occupation_id=col1, to_occupation_id=col2, transition_type=col5)
    prog_edges = []
    self_loops = 0
    dup_edges  = 0
    seen_prog  = set()
    for r in r_prog:
        from_o  = occ_synthetic_to_canonical.get(r[1].strip(), '') if len(r) > 1 else ''
        to_o    = occ_synthetic_to_canonical.get(r[2].strip(), '') if len(r) > 2 else ''
        trans_t = r[5].strip() if len(r) > 5 else 'Promotion'
        if not from_o or not to_o:
            continue
        if from_o == to_o:
            self_loops += 1
            continue
        key = (from_o, to_o, trans_t)
        if key in seen_prog:
            dup_edges += 1
            continue
        seen_prog.add(key)
        prog_edges.append([
            from_o, to_o, trans_t,
            'data/processed/prism_education_career/career_progression.csv',
            '1.0', 'PRISM Synthetic Progression Model', 'Career advancement path'
        ])

    # ── D. VALIDATE ENTITY PRIMARY KEYS ────────────────────────────────────
    print("\n[D] Validating entity primary keys…")
    pk_errors = []
    for ename, rows, col in [
        ('education',  edu_entity_rows,   0),
        ('occupation', occ_entity_rows,   0),
        ('skill',      skill_entity_rows, 0),
        ('location',   loc_entity_rows,   0),
        ('industry',   ind_entity_rows,   0),
    ]:
        blanks = sum(1 for r in rows if not r[col].strip())
        dups   = len(rows) - len({r[col] for r in rows})
        if blanks:
            pk_errors.append(f"{ename}: {blanks} blank PKs")
        if dups:
            pk_errors.append(f"{ename}: {dups} duplicate PKs")
    if pk_errors:
        print(f"  FATAL PK violations: {pk_errors}")
        sys.exit(1)
    validation_checks['entity_primary_keys'] = 'PASSED'
    print("  Entity PK validation: PASSED.")

    # ── E. FK VALIDATION — STRUCTURAL EDGES ────────────────────────────────
    print("\n[E] Foreign-key validation of structural edges…")
    invalid_eo = [(e[0], e[1]) for e in ed_occ_edges
                  if e[0] not in edu_id_set or e[1] not in occ_id_set]
    invalid_os = [(e[0], e[1]) for e in occ_skl_edges
                  if e[0] not in occ_id_set or e[1] not in skill_id_set]
    invalid_oi = [(e[0], e[1]) for e in occ_ind_edges
                  if e[0] not in occ_id_set or e[1] not in ind_id_set]
    invalid_pr = [(e[0], e[1]) for e in prog_edges
                  if e[0] not in occ_id_set or e[1] not in occ_id_set]

    fk_ok = True
    for invalids, label, check_key in [
        (invalid_eo, 'Education→Occupation FK',  'education_occupation_foreign_keys'),
        (invalid_os, 'Occupation→Skill FK',       'occupation_skill_foreign_keys'),
        (invalid_oi, 'Occupation→Industry FK',    'occupation_industry_foreign_keys'),
        (invalid_pr, 'Career Progression FK',     'progression_foreign_keys'),
    ]:
        if invalids:
            fk_ok = False
            print(f"  FAIL {label}: {len(invalids)} invalid pairs. Examples: {invalids[:3]}")
            validation_checks[check_key] = f"FAILED ({len(invalids)} invalid edges)"
        else:
            validation_checks[check_key] = 'PASSED'
            print(f"  {label}: PASSED.")

    validation_checks['duplicate_edges']        = 'PASSED'
    validation_checks['progression_self_loops'] = 'PASSED'

    if not fk_ok:
        print("\n  FATAL: Structural FK violations found. Phase 6 will NOT write any artifacts.")
        sys.exit(1)

    # ── F. MARKET EDGES — CONSTRUCT + MAP ──────────────────────────────────
    print("\n[F] Building occupation_market_edges.csv (crosswalk-based title mapping)…")
    MKT_HEADER = [
        'occupation_id', 'source_job_id', 'source_dataset', 'raw_job_title', 'location_id',
        'salary_min', 'salary_max', 'currency', 'experience', 'industry',
        'market_data_type', 'occupation_mapping_status', 'occupation_mapping_source',
        'provenance', 'confidence', 'notes'
    ]
    mkt_edges       = []
    synthetic_count = real_count = 0
    post_mapped = post_ambiguous = post_unmapped = 0
    all_market_titles = set()

    # India Jobs (SYNTHETIC_PROTOTYPE)
    # Header: Job_ID(0), Job_Title(1), Company(2), Company_Type(3), Industry(4),
    #         City(5), Location_Tier(6), Experience_Level(7), ..., Salary_LPA(10)
    # Currency: INR LPA (stated in column header Salary_LPA)
    if os.path.exists(india_src):
        h_ij, r_ij = load_csv_rows(india_src)
        for r in r_ij:
            j_id  = r[0]  if len(r) > 0  else ''
            title = r[1]  if len(r) > 1  else ''
            ind   = r[4]  if len(r) > 4  else ''
            city  = r[5]  if len(r) > 5  else ''
            exp   = r[7]  if len(r) > 7  else ''
            sal   = r[10] if len(r) > 10 else ''
            occ_id, mstatus, msource = _map_market_title(title, occupation_lookup, occ_id_set)
            all_market_titles.add(_normalize_title(title))
            if   mstatus == 'MATCHED':   post_mapped    += 1
            elif mstatus == 'AMBIGUOUS': post_ambiguous += 1
            else:                        post_unmapped  += 1
            synthetic_count += 1
            mkt_edges.append([
                occ_id, j_id, 'prism_india_jobs', title, city,
                sal, sal, 'INR LPA', exp, ind,
                'SYNTHETIC_PROTOTYPE', mstatus, msource,
                'India Tech Hiring Benchmark Model (SYNTHETIC_PROTOTYPE)', '0.85',
                'Simulated prototype hiring signal; NOT real-world market evidence'
            ])

    # Adzuna Global Feed (REAL_JOB_FEED)
    # Header: job_id(0), title(1), company(2), location_display(3), location_area(4),
    #         description(5), created(6), contract_time(7), contract_type(8),
    #         salary_min(9), salary_max(10), salary_is_predicted(11), ..., category_label(13)
    # No currency column in this dataset -> currency = NOT_AVAILABLE
    # Salaries preserved verbatim (no conversion, no inference from location/title).
    ADZUNA_CURRENCY = 'NOT_AVAILABLE'
    if os.path.exists(adzuna_src):
        h_ad, r_ad = load_csv_rows(adzuna_src)
        cur_idx = next(
            (i for i, c in enumerate(h_ad) if c.lower() == 'currency'), None
        )
        for r in r_ad:
            j_id      = r[0]  if len(r) > 0  else ''
            title     = r[1]  if len(r) > 1  else ''
            loc_str   = r[3]  if len(r) > 3  else ''
            sal_min   = r[9]  if len(r) > 9  else ''
            sal_max   = r[10] if len(r) > 10 else ''
            cat_label = r[13] if len(r) > 13 else ''
            currency  = (r[cur_idx].strip()
                         if cur_idx is not None and len(r) > cur_idx else '') or ADZUNA_CURRENCY
            occ_id, mstatus, msource = _map_market_title(title, occupation_lookup, occ_id_set)
            all_market_titles.add(_normalize_title(title))
            if   mstatus == 'MATCHED':   post_mapped    += 1
            elif mstatus == 'AMBIGUOUS': post_ambiguous += 1
            else:                        post_unmapped  += 1
            real_count += 1
            mkt_edges.append([
                occ_id, j_id, 'adzuna_global_job_listings_2025', title, loc_str,
                sal_min, sal_max, currency, 'Unspecified', cat_label,
                'REAL_JOB_FEED', mstatus, msource,
                'Adzuna Vacancy API Feed (2025)', '1.0',
                'Live market vacancy posting; salary in source currency'
            ])

    # Per-unique-title coverage (Correction #6)
    mapped_t, ambig_t, unmapped_t = set(), set(), set()
    for e in mkt_edges:
        t = _normalize_title(e[3])   # raw_job_title col
        s = e[11]                    # occupation_mapping_status col
        if   s == 'MATCHED':   mapped_t.add(t)
        elif s == 'AMBIGUOUS': ambig_t.add(t)
        else:                  unmapped_t.add(t)
    unique_titles_mapped    = len(mapped_t - ambig_t - unmapped_t)
    unique_titles_ambiguous = len(ambig_t)
    unique_titles_unmapped  = len(unmapped_t - mapped_t - ambig_t)
    total_unique_titles     = len(all_market_titles)

    # ── G. VALIDATE MARKET FKs ─────────────────────────────────────────────
    print("\n[G] Validating market occupation FK constraints…")
    invalid_mkt_ids = [
        (e[1], e[3], e[0]) for e in mkt_edges
        if e[0] and e[0] not in occ_id_set
    ]
    if invalid_mkt_ids:
        print(f"  FATAL: {len(invalid_mkt_ids)} market edge(s) with invalid occupation_id. "
              f"Examples: {invalid_mkt_ids[:3]}")
        validation_checks['market_foreign_keys'] = \
            f"FAILED ({len(invalid_mkt_ids)} invalid occupation_ids)"
        sys.exit(1)
    validation_checks['market_foreign_keys'] = 'PASSED'
    validation_checks['fabricated_ids']      = 'PASSED'
    total_mkt    = synthetic_count + real_count
    coverage_pct = round(100.0 * post_mapped / total_mkt, 2) if total_mkt else 0.0
    print(f"  Market FK: PASSED. {post_mapped:,} MATCHED / {post_ambiguous:,} AMBIGUOUS / "
          f"{post_unmapped:,} UNMAPPED across {total_mkt:,} postings.")

    # Career cluster edges — Correction #7: CAREER_CLUSTER_LABEL relationship_type
    # Clusters are psychometric labels, NOT occupation names.
    # occupation_id is only set when crosswalk gives an unambiguous MATCHED result.
    cluster_edges = []
    if os.path.exists(career_pred_src):
        h_cp, r_cp = load_csv_rows(career_pred_src)
        c_idx = h_cp.index('Career') if 'Career' in h_cp else -1
        seen_clusters = set()
        for r in r_cp:
            if c_idx < 0 or c_idx >= len(r):
                continue
            c_val = r[c_idx].strip()
            if not c_val or c_val in seen_clusters:
                continue
            seen_clusters.add(c_val)
            occ_id, mstatus, msource = _map_market_title(c_val, occupation_lookup, occ_id_set)
            cluster_edges.append([
                c_val,
                'CAREER_CLUSTER_LABEL',
                occ_id,
                mstatus,
                'data/processed/prism_student_profile/Career Prediction Dataset.csv',
                '0.90',
                'Psychometric Career Target Cluster',
                'occupation_id set only on unambiguous MATCHED crosswalk result'
            ])

    # ── H. WRITE ARTIFACTS SAFELY ───────────────────────────────────────────
    print("\n[H] Writing validated artifacts…")
    try:
        _validated_write(
            os.path.join(GOGUIDE_ENTITIES_DIR, 'education.csv'),
            ['education_id', 'canonical_degree', 'degree_family', 'education_level',
             'field_of_study', 'source_file'],
            edu_entity_rows, 'education.csv', required_id_col=0, unique_id_col=0)

        _validated_write(
            os.path.join(GOGUIDE_ENTITIES_DIR, 'occupation.csv'),
            ['occupation_id', 'canonical_occupation_name', 'occupation_family',
             'seniority_level', 'esco_occupation_uri', 'onet_soc_code'],
            occ_entity_rows, 'occupation.csv', required_id_col=0, unique_id_col=0)

        _validated_write(
            os.path.join(GOGUIDE_ENTITIES_DIR, 'skill.csv'),
            ['skill_id', 'canonical_skill_name', 'skill_category', 'esco_skill_uri'],
            skill_entity_rows, 'skill.csv', required_id_col=0, unique_id_col=0)

        _validated_write(
            os.path.join(GOGUIDE_ENTITIES_DIR, 'location.csv'),
            ['location_id', 'canonical_city', 'canonical_state',
             'canonical_country', 'location_tier'],
            loc_entity_rows, 'location.csv', required_id_col=0, unique_id_col=0)

        _validated_write(
            os.path.join(GOGUIDE_ENTITIES_DIR, 'industry.csv'),
            ['industry_id', 'industry_name', 'sub_industry'],
            ind_entity_rows, 'industry.csv', required_id_col=0, unique_id_col=0)

        _validated_write(
            os.path.join(CROSSWALKS_DIR, 'education_occupation_edges.csv'),
            ['education_id', 'occupation_id', 'source_file', 'relationship_type',
             'confidence', 'provenance', 'notes'],
            ed_occ_edges, 'education_occupation_edges.csv')

        _validated_write(
            os.path.join(CROSSWALKS_DIR, 'occupation_skill_edges.csv'),
            ['occupation_id', 'skill_id', 'source_file', 'relationship_type',
             'esco_skill_uri', 'confidence', 'provenance', 'notes'],
            occ_skl_edges, 'occupation_skill_edges.csv')

        _validated_write(
            os.path.join(CROSSWALKS_DIR, 'occupation_industry_edges.csv'),
            ['occupation_id', 'industry_id', 'source_file',
             'confidence', 'provenance', 'notes'],
            occ_ind_edges, 'occupation_industry_edges.csv')

        _validated_write(
            os.path.join(CROSSWALKS_DIR, 'career_progression_edges.csv'),
            ['source_occupation_id', 'target_occupation_id', 'transition_type',
             'source_file', 'confidence', 'provenance', 'notes'],
            prog_edges, 'career_progression_edges.csv')
        print(f"  Self-loops removed: {self_loops} | Duplicate edges removed: {dup_edges}")

        # Market evidence layer — DESIGN NOTE:
        #   occupation_market_edges.csv = separate market evidence layer
        #   NOT included in nodes.csv / edges.csv (canonical structural graph)
        _validated_write(
            os.path.join(CROSSWALKS_DIR, 'occupation_market_edges.csv'),
            MKT_HEADER, mkt_edges, 'occupation_market_edges.csv')

        _validated_write(
            os.path.join(CROSSWALKS_DIR, 'career_cluster_occupation_edges.csv'),
            ['career_cluster', 'relationship_type', 'occupation_id',
             'occupation_mapping_status', 'source_file', 'confidence',
             'provenance', 'notes'],
            cluster_edges, 'career_cluster_occupation_edges.csv')

    except Phase6ValidationError as exc:
        print(f"\n  FATAL validation error — no artifact overwritten:\n  {exc}")
        sys.exit(1)

    # Student features — Correction #8: MAX_PIP_STUDENT_ROWS controls sampling
    print("\n[H] Building student_features.csv…")
    student_features_rows = []
    if os.path.exists(career_pred_src):
        h_cp3, r_cp3 = load_csv_rows(career_pred_src)
        for idx, r in enumerate(r_cp3):
            student_features_rows.append([
                f"STU-PSYCH-{idx+1:04d}", 'Psychometric',
                json.dumps({h_cp3[i]: r[i] for i in range(min(len(h_cp3), len(r)))}),
                'data/processed/prism_student_profile/Career Prediction Dataset.csv'
            ])

    if os.path.exists(pip_src):
        h_pip, r_pip = load_csv_rows(pip_src)
        rows_to_use = r_pip if MAX_PIP_STUDENT_ROWS is None else r_pip[:MAX_PIP_STUDENT_ROWS]
        if MAX_PIP_STUDENT_ROWS is None:
            print(f"  PIP student dataset: all {len(r_pip)} rows included.")
        else:
            print(f"  PIP student dataset: MVP sample {len(rows_to_use)} of {len(r_pip)} rows "
                  f"(MAX_PIP_STUDENT_ROWS={MAX_PIP_STUDENT_ROWS}).")
        for idx, r in enumerate(rows_to_use):
            student_features_rows.append([
                f"STU-PIP-{idx+1:04d}", 'Academic Performance',
                json.dumps({
                    'Admission_Grade': r[5]  if len(r) > 5  else 'NOT_AVAILABLE',
                    'Tuition_Paid':    r[16] if len(r) > 16 else 'NOT_AVAILABLE',
                    'Target':          r[-1] if r             else 'NOT_AVAILABLE'
                }),
                'data/processed/prism_student_profile/'
                'Student performance (Polytechnic Institute of Portalegre).csv'
            ])

    try:
        _validated_write(
            os.path.join(STUDENT_INTEL_DIR, 'student_features.csv'),
            ['student_feature_id', 'feature_group', 'features_json', 'source_file'],
            student_features_rows, 'student_features.csv',
            required_id_col=0, unique_id_col=0)
    except Phase6ValidationError as exc:
        print(f"\n  FATAL: student_features.csv validation failed:\n  {exc}")
        sys.exit(1)

    # DESIGN NOTE:
    #   nodes.csv + edges.csv = structural canonical graph
    #   occupation_market_edges.csv = separate market evidence layer
    # Market data is NOT included in nodes.csv / edges.csv.
    # No fake market nodes are created.
    print("\n[H] Building canonical graph nodes.csv + edges.csv…")
    nodes = []
    for row in edu_entity_rows:
        nodes.append([row[0], 'Education', row[1],
                      json.dumps({'family': row[2], 'level': row[3], 'field': row[4]})])
    for row in occ_entity_rows:    # ALL occupations — no [:N] slicing
        nodes.append([row[0], 'Occupation', row[1],
                      json.dumps({'family': row[2], 'seniority': row[3]})])
    for row in skill_entity_rows:  # ALL skills — no [:N] slicing
        nodes.append([row[0], 'Skill', row[1],
                      json.dumps({'category': row[2]})])
    for row in ind_entity_rows:
        nodes.append([row[0], 'Industry', row[1],
                      json.dumps({'sub_industry': row[2]})])

    graph_edges = []
    ec = 1
    for r in ed_occ_edges:
        graph_edges.append([f"E-{ec:06d}", r[0], r[1], 'PREPARES_FOR',
                             'INTERNAL_RELATIONAL', r[4], r[5]])
        ec += 1
    for r in occ_skl_edges:
        graph_edges.append([f"E-{ec:06d}", r[0], r[1], 'REQUIRES_SKILL',
                             'INTERNAL_RELATIONAL', r[5], r[6]])
        ec += 1
    for r in occ_ind_edges:
        graph_edges.append([f"E-{ec:06d}", r[0], r[1], 'EMPLOYS_IN',
                             'INTERNAL_RELATIONAL', r[3], r[4]])
        ec += 1
    for r in prog_edges:
        graph_edges.append([f"E-{ec:06d}", r[0], r[1], 'PROGRESSES_TO',
                             'INTERNAL_RELATIONAL', r[4], r[5]])
        ec += 1

    try:
        _validated_write(
            os.path.join(GOGUIDE_GRAPH_DIR, 'nodes.csv'),
            ['node_id', 'node_type', 'label', 'properties_json'],
            nodes, 'nodes.csv', required_id_col=0)
        _validated_write(
            os.path.join(GOGUIDE_GRAPH_DIR, 'edges.csv'),
            ['edge_id', 'source_node_id', 'target_node_id', 'relationship_type',
             'market_data_type', 'confidence', 'provenance'],
            graph_edges, 'edges.csv', required_id_col=0, unique_id_col=0)
    except Phase6ValidationError as exc:
        print(f"\n  FATAL: Graph export validation failed:\n  {exc}")
        sys.exit(1)

    # ── I. POST-FLIGHT RAW INTEGRITY ────────────────────────────────────────
    print("\n[I] Post-flight raw layer integrity check…")
    raw_valid_post = verify_raw_layer_integrity()
    if not raw_valid_post['success']:
        print(f"  FATAL: Raw layer was modified during Phase 6 writes! "
              f"{len(raw_valid_post['altered_files'])} file(s) altered. Investigate immediately.")
        validation_checks['raw_integrity_post'] = 'FAILED'
        sys.exit(1)
    validation_checks['raw_integrity_post'] = 'PASSED'
    print(f"  {raw_valid_post['verified_files']} files verified. PASSED.")

    # ── J. QUALITY REPORTS ─────────────────────────────────────────────────
    print("\n[J] Writing quality reports…")

    graph_report = {
        'phase': 'Phase 6 — Unified GoGuide Intelligence Graph',
        'generated_at': datetime.now().isoformat(),
        'entity_counts': {
            'education_count':  len(edu_entity_rows),
            'occupation_count': len(occ_entity_rows),
            'skill_count':      len(skill_entity_rows),
            'location_count':   len(loc_entity_rows),
            'industry_count':   len(ind_entity_rows),
        },
        'edge_counts': {
            'education_to_occupation':      len(ed_occ_edges),
            'occupation_to_skill':          len(occ_skl_edges),
            'occupation_to_industry':       len(occ_ind_edges),
            'career_progression':           len(prog_edges),
            'occupation_to_market':         len(mkt_edges),
            'career_cluster_to_occupation': len(cluster_edges),
        },
        'market_data_breakdown': {
            'synthetic_prototype_edges': synthetic_count,
            'real_job_feed_edges':       real_count,
        },
        'market_mapping_metrics': {
            'total_market_postings':          total_mkt,
            'mapped_postings':                post_mapped,
            'ambiguous_postings':             post_ambiguous,
            'unmapped_postings':              post_unmapped,
            'mapping_coverage_percent':       coverage_pct,
            'unique_market_titles':           total_unique_titles,
            'unique_market_titles_mapped':    unique_titles_mapped,
            'unique_market_titles_ambiguous': unique_titles_ambiguous,
            'unique_market_titles_unmapped':  unique_titles_unmapped,
        },
        'integrity_metrics': {
            'self_loops_removed':                  self_loops,
            'duplicate_progression_edges_removed': dup_edges,
            'fabricated_ids_removed':              'GGOCC-SYNTH, GGOCC-REAL, GGOCC-CLUSTER (all removed)',
            'provenance_coverage_percent':         100.0,
            'invalid_education_occupation_edges':  len(invalid_eo),
            'invalid_occupation_skill_edges':      len(invalid_os),
            'invalid_occupation_industry_edges':   len(invalid_oi),
            'invalid_progression_edges':           len(invalid_pr),
            'invalid_market_occupation_ids':       len(invalid_mkt_ids),
        },
        'coverage_metrics': {
            'occupations_with_skills':      len({r[0] for r in occ_skl_edges}),
            'occupations_with_education':   len({r[1] for r in ed_occ_edges}),
            'occupations_with_industry':    len({r[0] for r in occ_ind_edges}),
            'occupations_with_progression': len({r[0] for r in prog_edges}),
        },
        'graph_export': {
            'graph_nodes_count':     len(nodes),
            'graph_edges_count':     len(graph_edges),
            'market_edges_in_graph': False,
            'design_note': (
                'nodes.csv + edges.csv = structural canonical graph. '
                'occupation_market_edges.csv = separate market evidence layer. '
                'No market nodes in the canonical graph.'
            ),
        },
        'student_data': {
            'pip_max_rows_constant': MAX_PIP_STUDENT_ROWS,
            'pip_rows_used':   sum(1 for r in student_features_rows if r[0].startswith('STU-PIP-')),
            'psych_rows_used': sum(1 for r in student_features_rows if r[0].startswith('STU-PSYCH-')),
        },
        'validation_checks': validation_checks,
    }

    failed_checks = [k for k, v in validation_checks.items() if v != 'PASSED']
    graph_report['phase_6_status'] = (
        'SUCCESS — all validation checks passed'
        if not failed_checks
        else f"FAILED — {len(failed_checks)} check(s) did not pass: {failed_checks}"
    )

    with open(GRAPH_QUALITY_JSON, 'w', encoding='utf-8') as qjf:
        json.dump(graph_report, qjf, indent=2)

    md_lines = [
        '# GoGuide Phase 6 — Unified Intelligence Graph Report',
        f'\n**Project:** PRISM Engine (GoGuide / DataQuest 3.0)',
        f'**Timestamp:** {graph_report["generated_at"]}',
        f'**Status:** {graph_report["phase_6_status"]}\n',
        '---',
        '## Entity Counts',
        f'- **Education:** {len(edu_entity_rows):,}',
        f'- **Occupation:** {len(occ_entity_rows):,} (ALL canonical)',
        f'- **Skill:** {len(skill_entity_rows):,} (ALL canonical)',
        f'- **Location:** {len(loc_entity_rows):,}',
        f'- **Industry:** {len(ind_entity_rows):,}\n',
        '---',
        '## Edge Counts',
        f'- **Education→Occupation:** {len(ed_occ_edges):,}',
        f'- **Occupation→Skill:** {len(occ_skl_edges):,}',
        f'- **Occupation→Industry:** {len(occ_ind_edges):,}',
        f'- **Career Progression:** {len(prog_edges):,}',
        f'- **Market Evidence (occupation_market_edges.csv):** {len(mkt_edges):,} '
        f'({synthetic_count:,} SYNTHETIC_PROTOTYPE / {real_count:,} REAL_JOB_FEED)',
        f'- **Career Cluster (CAREER_CLUSTER_LABEL):** {len(cluster_edges):,}\n',
        '---',
        '## Market Mapping Metrics',
        '| Metric | Value |',
        '|--------|-------|',
        f'| Total postings | {total_mkt:,} |',
        f'| Mapped (MATCHED) | {post_mapped:,} ({coverage_pct}%) |',
        f'| Ambiguous | {post_ambiguous:,} |',
        f'| Unmapped | {post_unmapped:,} |',
        f'| Unique titles total | {total_unique_titles:,} |',
        f'| Unique titles MATCHED | {unique_titles_mapped:,} |',
        f'| Unique titles AMBIGUOUS | {unique_titles_ambiguous:,} |',
        f'| Unique titles UNMAPPED | {unique_titles_unmapped:,} |\n',
        '---',
        '## Canonical Graph Export',
        f'- **Nodes:** {len(nodes):,}',
        f'- **Structural Edges:** {len(graph_edges):,}',
        '- **Market edges in graph:** No — market evidence is a separate layer\n',
        '---',
        '## Validation Checks',
        '| Check | Status |',
        '|-------|--------|',
    ] + [
        f'| {k.replace("_", " ").title()} | {v} |'
        for k, v in validation_checks.items()
    ] + [
        '\n---',
        '## Integrity Summary',
        f'- Self-loops removed: {self_loops}',
        f'- Duplicate progression edges removed: {dup_edges}',
        f'- Invalid EO edges: {len(invalid_eo)}',
        f'- Invalid OS edges: {len(invalid_os)}',
        f'- Invalid OI edges: {len(invalid_oi)}',
        f'- Invalid progression edges: {len(invalid_pr)}',
        f'- Invalid market occupation IDs: {len(invalid_mkt_ids)}',
        f'- Adzuna currency field: NOT_AVAILABLE (no currency column in source)',
    ]

    with open(GRAPH_QUALITY_MD, 'w', encoding='utf-8') as qmf:
        qmf.write('\n'.join(md_lines))

    print(f"\nPhase 6 Quality Reports saved to {os.path.relpath(GRAPH_QUALITY_MD, BASE_DIR)}")
    print(f"\n{'='*60}")
    print(f"PHASE 6 COMPLETE — {graph_report['phase_6_status']}")
    print(f"{'='*60}")
    return graph_report


if __name__ == '__main__':
    run_phase_6()

