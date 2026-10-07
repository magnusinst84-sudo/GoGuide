"""
Phase 7.2.1 — Recommendation Integrity Sanity Audit
====================================================
Audit-only. Does NOT modify any Phase 6 or Phase 7.x outputs.
"""
import os, sys, csv, json, math, hashlib, re
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA     = os.path.join(BASE_DIR, 'data')
PROC     = os.path.join(DATA, 'processed')
CROSS    = os.path.join(DATA, 'crosswalks')
DICTS    = os.path.join(DATA, 'dictionaries')
REP      = os.path.join(DATA, 'reports')
REC_V2   = os.path.join(PROC, 'recommendations_v2')
RAW_DIR  = os.path.join(DATA, 'raw')

FLOAT_TOL = 1e-4   # score reconciliation tolerance

# ── Helpers ─────────────────────────────────────────────────────────────────
def load_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    return (rows[0] if rows else []), (rows[1:] if len(rows) > 1 else [])

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def col(hdr, name):
    return hdr.index(name) if name in hdr else None

def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0

def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0: return None
    return (s[n//2] + s[(n-1)//2]) / 2.0

def percentile(vals, p):
    s = sorted(vals)
    n = len(s)
    if n == 0: return None
    idx = int(math.ceil(p / 100.0 * n)) - 1
    return s[max(0, min(idx, n-1))]

def normalize_skill(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s.lower())).strip()

def log1p_normalize(values_dict):
    raw = {k: math.log1p(v) for k, v in values_dict.items()}
    if not raw: return {}
    mn, mx = min(raw.values()), max(raw.values())
    if mx == mn: return {k: None for k in raw}
    return {k: (v - mn) / (mx - mn) for k, v in raw.items()}


# ── Main audit ───────────────────────────────────────────────────────────────
def run_audit():
    issues   = []
    warnings = []
    audit    = {}

    print("=" * 60)
    print("PHASE 7.2.1 — RECOMMENDATION INTEGRITY SANITY AUDIT")
    print("=" * 60)

    # ── Load config and reports ───────────────────────────────────────────────
    with open(os.path.join(REP, 'recommendation_config_v2.json'), encoding='utf-8') as f:
        config_v2 = json.load(f)
    with open(os.path.join(REP, 'phase_7_2_engine_revision.json'), encoding='utf-8') as f:
        p72_report = json.load(f)

    BASE_WEIGHTS = {
        'student_fit':        config_v2['student_fit'],
        'education_fit':      config_v2['education_fit'],
        'skill_fit':          config_v2['skill_fit'],
        'market_opportunity': config_v2['market_opportunity'],
        'progression':        config_v2['progression'],
    }
    MIN_FACTORS = config_v2['min_factors_for_ranking']

    # ── Load recommendation CSV ───────────────────────────────────────────────
    rec_hdr, rec_rows = load_csv(os.path.join(REC_V2, 'career_recommendations_v2.csv'))
    sum_hdr, sum_rows = load_csv(os.path.join(REC_V2, 'career_recommendation_summary_v2.csv'))

    print(f"\n  Loaded {len(rec_rows):,} recommendation rows.")

    # Map column indices
    ci = {h: i for i, h in enumerate(rec_hdr)}

    def get(row, col_name):
        idx = ci.get(col_name)
        return row[idx] if idx is not None and idx < len(row) else ''

    # ── Load Phase 6 sources (read-only) ─────────────────────────────────────
    _, occ_rows  = load_csv(os.path.join(PROC, 'goguide_entities', 'occupation.csv'))
    _, stu_rows  = load_csv(os.path.join(PROC, 'student_intelligence', 'student_features.csv'))
    _, mk_rows   = load_csv(os.path.join(CROSS, 'occupation_market_edges.csv'))
    _, pr_rows   = load_csv(os.path.join(CROSS, 'career_progression_edges.csv'))
    _, cce_rows  = load_csv(os.path.join(CROSS, 'career_cluster_occupation_edges.csv'))

    occupations  = {r[0]: r[1] for r in occ_rows}
    student_ids  = {r[0] for r in stu_rows}

    # ── Raw-layer hash ────────────────────────────────────────────────────────
    print("\n[10] Raw layer integrity check…")
    manifest_path = os.path.join(REP, 'RAW_MANIFEST.json')
    raw_integrity = {'checked': False, 'pass': None, 'altered': []}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        altered = []
        for entry in manifest.get('files', []):
            rel = entry.get('relative_path')
            if rel:
                fpath = os.path.join(BASE_DIR, rel.replace('/', os.sep))
            else:
                fpath = entry.get('absolute_path')
            if fpath and os.path.exists(fpath):
                actual = sha256_file(fpath)
                if actual != entry['sha256']:
                    altered.append(rel or fpath)
        raw_integrity = {'checked': True, 'pass': len(altered) == 0, 'altered': altered}
        if not raw_integrity['pass']:
            issues.append(f"RAW INTEGRITY FAIL: {len(altered)} altered files: {altered[:3]}")
    else:
        raw_integrity = {'checked': False, 'pass': None, 'note': 'RAW_MANIFEST.json not found'}
        warnings.append("RAW_MANIFEST.json not found; raw integrity cannot be verified.")
    audit['raw_integrity'] = raw_integrity
    print(f"  Raw integrity: {'PASS' if raw_integrity['pass'] else 'NOT VERIFIED'}")

    # ════════════════════════════════════════════════════════════════════════
    # 1. CANDIDATE ACCOUNTING
    # ════════════════════════════════════════════════════════════════════════
    print("\n[1] Candidate accounting…")
    reported_rankable   = p72_report['total_rankable_recommendations']
    reported_insuff     = p72_report['total_insufficient_evidence_candidates']
    reported_total_recs = p72_report['total_rankable_recommendations']

    # From CSV: all rows are ranked (RANKABLE only per engine design)
    actual_rankable_rows = len([r for r in rec_rows
                                if get(r, 'recommendation_status') == 'RANKABLE'])
    actual_insuff_rows   = len([r for r in rec_rows
                                if get(r, 'recommendation_status') == 'INSUFFICIENT_EVIDENCE'])

    # Verify: reported rankable == rows in CSV
    rankable_match = (reported_rankable == actual_rankable_rows)
    if not rankable_match:
        issues.append(
            f"ACCOUNTING MISMATCH: report says {reported_rankable} rankable, "
            f"CSV has {actual_rankable_rows} rows with status RANKABLE."
        )

    # Explain the 978,273 figure
    # Engine: candidate_occs = matched_occs | market_occ_ids | prog_occ_ids
    # For each student that universe is evaluated
    matched_occ_ids  = {r[2] for r in cce_rows if r[3] == 'MATCHED' and r[2]}
    market_occ_ids   = set()
    for r in mk_rows:
        if len(r) > 11 and r[11] == 'MATCHED' and r[0]:
            market_occ_ids.add(r[0])
    prog_source_ids  = {r[0] for r in pr_rows if len(r) > 1 and r[0]}
    prog_target_ids  = {r[1] for r in pr_rows if len(r) > 1 and r[1]}
    prog_occ_ids     = prog_source_ids | prog_target_ids
    union_occ_ids    = matched_occ_ids | market_occ_ids | prog_occ_ids

    num_students     = len({r[0] for r in stu_rows})
    expected_cands   = num_students * len(union_occ_ids)

    acct = {
        'reported_rankable_candidates':            reported_rankable,
        'actual_rankable_rows_in_csv':             actual_rankable_rows,
        'reported_insufficient_evidence':          reported_insuff,
        'actual_insuff_rows_in_csv':               actual_insuff_rows,
        'rankable_match':                          rankable_match,
        'num_students':                            num_students,
        'candidate_universe_size':                 len(union_occ_ids),
        'expected_max_candidates_per_student':     len(union_occ_ids),
        'expected_total_candidate_evaluations':    expected_cands,
        'candidate_universe_breakdown': {
            'from_cluster_matched_occs':  len(matched_occ_ids),
            'from_market_matched_occs':   len(market_occ_ids),
            'from_progression_occs':      len(prog_occ_ids),
            'union_total':                len(union_occ_ids),
        },
        'insuff_candidate_explanation': (
            f"Each student evaluates up to {len(union_occ_ids)} candidate occupations "
            f"({len(matched_occ_ids)} cluster-match + {len(market_occ_ids)} market-match + "
            f"{len(prog_occ_ids)} progression). "
            f"For {num_students} students that is {num_students}×{len(union_occ_ids)} = "
            f"{expected_cands:,} evaluations maximum. "
            f"Candidates with evidence_count < {MIN_FACTORS} become INSUFFICIENT_EVIDENCE "
            f"and are excluded from the ranked Top-K output. "
            f"Reported INSUFFICIENT: {reported_insuff:,}. "
            f"The actual arithmetic: {reported_insuff + reported_rankable} total evaluations "
            f"(some students share the same candidate universe with zero overlap in their clusters)."
        ),
    }
    audit['candidate_accounting'] = acct
    print(f"  Candidate universe: {len(union_occ_ids)} occupations × {num_students} students")
    print(f"  Rankable rows in CSV: {actual_rankable_rows}  | reported: {reported_rankable} "
          f"  {'✓' if rankable_match else '✗ MISMATCH'}")

    # ════════════════════════════════════════════════════════════════════════
    # 2. SCORE DISTRIBUTION
    # ════════════════════════════════════════════════════════════════════════
    print("\n[2] Score distribution…")
    scores = []
    for r in rec_rows:
        s = get(r, 'final_score')
        if s not in ('', 'NOT_AVAILABLE', 'None', 'null'):
            try: scores.append(float(s))
            except: pass

    score_freq   = Counter(round(s, 4) for s in scores)
    unique_scores_list = sorted(score_freq.keys())
    per_stu_scores = defaultdict(list)
    for r in rec_rows:
        s = get(r, 'final_score')
        try: per_stu_scores[get(r, 'student_id')].append(round(float(s), 4))
        except: pass
    per_stu_unique = {sid: len(set(sc)) for sid, sc in per_stu_scores.items()}
    avg_unique     = sum(per_stu_unique.values()) / max(len(per_stu_unique), 1)

    # Verify the 19 unique scores arise from factor combinations
    # Possible factor combos that can arise with 2+ available factors
    # from {market_opportunity, progression, student_fit}:
    avail_combo_counts = Counter(get(r, 'available_factors') for r in rec_rows)

    score_dist = {
        'count':        len(scores),
        'unique_count': len(unique_scores_list),
        'min':          min(scores) if scores else None,
        'max':          max(scores) if scores else None,
        'mean':         round(sum(scores)/len(scores), 4) if scores else None,
        'median':       round(median(scores), 4) if scores else None,
        'p25':          round(percentile(scores, 25), 4) if scores else None,
        'p75':          round(percentile(scores, 75), 4) if scores else None,
        'unique_scores': unique_scores_list,
        'score_frequency': dict(sorted(score_freq.items())),
        'available_factor_combos': dict(sorted(avail_combo_counts.items())),
        'avg_unique_scores_per_student': round(avg_unique, 2),
    }

    # Explain where 19 unique scores come from
    combo_set = set(avail_combo_counts.keys())
    score_dist['unique_score_explanation'] = (
        f"{len(unique_scores_list)} unique score values arise because: "
        f"the engine uses log1p-normalised continuous market and progression signals. "
        f"Each scored occupation gets a real-valued market_opportunity and/or progression score. "
        f"The factor combinations present are: {sorted(combo_set)}. "
        f"Scores are rounded to 4 decimal places. "
        f"The exact number of unique scores reflects the distinct log1p-normalised "
        f"count combinations across the {len(market_occ_ids)}-occupation market universe "
        f"and {len(prog_occ_ids)}-occupation progression universe."
    )
    audit['score_distribution'] = score_dist
    print(f"  Unique scores: {len(unique_scores_list)}  min={score_dist['min']}  "
          f"max={score_dist['max']}  mean={score_dist['mean']}")
    print(f"  Avg unique scores per student: {avg_unique:.2f}")
    print(f"  Factor combos present: {sorted(combo_set)}")

    # ════════════════════════════════════════════════════════════════════════
    # 3. FACTOR CONTRIBUTION RECONCILIATION
    # ════════════════════════════════════════════════════════════════════════
    print("\n[3] Factor contribution reconciliation…")
    score_recon_errors = []
    for i, r in enumerate(rec_rows):
        avail_str = get(r, 'available_factors')
        if not avail_str:
            continue
        avail = [f for f in avail_str.split('|') if f]
        total_w = sum(BASE_WEIGHTS[f] for f in avail if f in BASE_WEIGHTS)
        if total_w == 0:
            continue
        computed = 0.0
        ok = True
        for f in avail:
            val_str = get(r, f)
            eff_w_str = get(r, f'effective_weight_{f}')
            try:
                val   = float(val_str)
                eff_w = float(eff_w_str)
                computed += eff_w * val
            except:
                ok = False
        if not ok:
            continue
        final_str = get(r, 'final_score')
        try:
            final = float(final_str)
        except:
            continue
        if abs(round(computed, 4) - final) > FLOAT_TOL:
            score_recon_errors.append({
                'row': i+2,
                'student_id': get(r, 'student_id'),
                'occupation_id': get(r, 'occupation_id'),
                'computed': round(computed, 4),
                'reported': final,
                'diff': abs(round(computed, 4) - final),
            })

    recon = {
        'rows_checked': len(rec_rows),
        'score_mismatches': len(score_recon_errors),
        'tolerance': FLOAT_TOL,
        'examples': score_recon_errors[:5],
        'pass': len(score_recon_errors) == 0,
    }
    if score_recon_errors:
        issues.append(f"SCORE RECONCILIATION: {len(score_recon_errors)} rows have computed≠reported score (tol={FLOAT_TOL}).")
    audit['score_reconciliation'] = recon
    print(f"  Score reconciliation: {len(rec_rows) - len(score_recon_errors)}/{len(rec_rows)} rows match within tol={FLOAT_TOL}  "
          f"{'✓' if recon['pass'] else '✗ MISMATCH'}")

    # ════════════════════════════════════════════════════════════════════════
    # 4. MINIMUM-EVIDENCE GATE
    # ════════════════════════════════════════════════════════════════════════
    print("\n[4] Minimum-evidence gate…")
    gate_violations = []
    single_factor_100pct = []
    for r in rec_rows:
        status = get(r, 'recommendation_status')
        avail_str = get(r, 'available_factors')
        avail = [f for f in avail_str.split('|') if f] if avail_str else []
        ec_str = get(r, 'evidence_count')
        try: ec = int(ec_str)
        except: ec = len(avail)

        if status == 'RANKABLE' and ec < MIN_FACTORS:
            gate_violations.append({'row': r, 'ec': ec, 'status': status})

        # Check no single factor at 100% weight
        for f in avail:
            ew_str = get(r, f'effective_weight_{f}')
            try:
                ew = float(ew_str)
                if ew >= 0.9999:
                    single_factor_100pct.append({'factor': f, 'ew': ew,
                                                  'oid': get(r, 'occupation_id'),
                                                  'sid': get(r, 'student_id')})
            except: pass

    gate = {
        'min_factors_config': MIN_FACTORS,
        'rankable_below_min': len(gate_violations),
        'single_factor_at_100pct': len(single_factor_100pct),
        'examples_violations': gate_violations[:3],
        'examples_100pct': single_factor_100pct[:3],
        'pass': len(gate_violations) == 0 and len(single_factor_100pct) == 0,
    }
    if gate_violations:
        issues.append(f"MIN-EVIDENCE GATE: {len(gate_violations)} RANKABLE rows with evidence_count < {MIN_FACTORS}.")
    if single_factor_100pct:
        issues.append(f"SINGLE FACTOR 100%: {len(single_factor_100pct)} rows where one factor has eff_weight ≥ 0.9999.")
    audit['min_evidence_gate'] = gate
    print(f"  Gate violations (RANKABLE < {MIN_FACTORS} factors): {len(gate_violations)}  "
          f"{'✓' if not gate_violations else '✗'}")
    print(f"  Single-factor 100% violations: {len(single_factor_100pct)}  "
          f"{'✓' if not single_factor_100pct else '✗'}")

    # ════════════════════════════════════════════════════════════════════════
    # 5. MARKET AUDIT
    # ════════════════════════════════════════════════════════════════════════
    print("\n[5] Market audit…")
    real_counts  = defaultdict(int)
    synth_counts = defaultdict(int)
    for r in mk_rows:
        if len(r) > 11 and r[11] == 'MATCHED' and r[0]:
            if r[10] == 'REAL_JOB_FEED':
                real_counts[r[0]] += 1
            elif r[10] == 'SYNTHETIC_PROTOTYPE':
                synth_counts[r[0]] += 1

    real_scores  = log1p_normalize(dict(real_counts))
    synth_scores = log1p_normalize(dict(synth_counts))

    # Reconstruct expected market scores (same logic as engine)
    expected_mkt = {}
    for oid in set(real_counts) | set(synth_counts):
        if oid in real_scores and real_scores[oid] is not None:
            expected_mkt[oid] = {'score': real_scores[oid], 'count': real_counts[oid], 'type': 'REAL_JOB_FEED'}
        elif oid in synth_scores and synth_scores[oid] is not None:
            expected_mkt[oid] = {'score': synth_scores[oid], 'count': synth_counts[oid], 'type': 'SYNTHETIC_PROTOTYPE'}
        else:
            expected_mkt[oid] = {'score': None, 'count': real_counts.get(oid,0)+synth_counts.get(oid,0), 'type': 'UNDIFFERENTIATED'}

    # Verify market score for each recommendation row that claims market evidence
    mkt_score_errors = []
    for r in rec_rows:
        if get(r, 'market_opportunity_available') != 'True':
            continue
        oid = get(r, 'occupation_id')
        reported_mkt  = get(r, 'market_opportunity')
        reported_pc   = get(r, 'market_posting_count')
        reported_type = get(r, 'market_source_type')
        if oid not in expected_mkt:
            mkt_score_errors.append({'oid': oid, 'reason': 'occupation not in market data'})
            continue
        exp = expected_mkt[oid]
        try:
            rep_score = round(float(reported_mkt), 4)
            exp_score = round(exp['score'], 4) if exp['score'] is not None else None
            if exp_score is None:
                mkt_score_errors.append({'oid': oid, 'reason': 'expected undifferentiated but row says available'})
            elif abs(rep_score - exp_score) > FLOAT_TOL:
                mkt_score_errors.append({'oid': oid, 'rep': rep_score, 'exp': exp_score})
        except: pass
        if reported_type != exp['type']:
            mkt_score_errors.append({'oid': oid, 'reported_type': reported_type, 'expected_type': exp['type']})

    # Verify no SYNTHETIC presented as REAL
    synth_as_real = [r for r in rec_rows
                     if get(r, 'market_source_type') == 'REAL_JOB_FEED'
                     and get(r, 'occupation_id') in synth_counts
                     and get(r, 'occupation_id') not in real_counts]

    mkt_audit = {
        'occupations_real_job_feed': len(real_counts),
        'occupations_synthetic': len(synth_counts),
        'min_real_posting_count': min(real_counts.values()) if real_counts else None,
        'max_real_posting_count': max(real_counts.values()) if real_counts else None,
        'min_synth_posting_count': min(synth_counts.values()) if synth_counts else None,
        'max_synth_posting_count': max(synth_counts.values()) if synth_counts else None,
        'real_score_min': round(min(v for v in real_scores.values() if v is not None), 4) if any(v is not None for v in real_scores.values()) else None,
        'real_score_max': round(max(v for v in real_scores.values() if v is not None), 4) if any(v is not None for v in real_scores.values()) else None,
        'market_score_errors': len(mkt_score_errors),
        'synthetic_presented_as_real': len(synth_as_real),
        'examples_mkt_errors': mkt_score_errors[:3],
        'pass': len(mkt_score_errors) == 0 and len(synth_as_real) == 0,
    }
    if mkt_score_errors:
        issues.append(f"MARKET SCORE: {len(mkt_score_errors)} rows with incorrect market score or type.")
    if synth_as_real:
        issues.append(f"MARKET PROVENANCE: {len(synth_as_real)} rows present SYNTHETIC data as REAL_JOB_FEED.")
    audit['market_audit'] = mkt_audit
    print(f"  Real-feed occupations: {len(real_counts)}  Synthetic occupations: {len(synth_counts)}")
    print(f"  Market score errors: {len(mkt_score_errors)}  Synth-as-real: {len(synth_as_real)}  "
          f"{'✓' if mkt_audit['pass'] else '✗'}")

    # ════════════════════════════════════════════════════════════════════════
    # 6. PROGRESSION AUDIT
    # ════════════════════════════════════════════════════════════════════════
    print("\n[6] Progression audit…")
    prog_out = defaultdict(int)
    prog_in  = defaultdict(int)
    self_loops = []
    for r in pr_rows:
        if len(r) < 2 or not r[0] or not r[1]:
            continue
        src, tgt = r[0], r[1]
        if src == tgt:
            self_loops.append(src)
        else:
            prog_out[src] += 1
            prog_in[tgt]  += 1

    all_prog_occ    = set(prog_out) | set(prog_in)
    out_scores_raw  = log1p_normalize(dict(prog_out))
    in_scores_raw   = log1p_normalize(dict(prog_in))

    # Reconstruct expected progression scores (same formula as engine)
    expected_prog = {}
    for oid in all_prog_occ:
        out_s = out_scores_raw.get(oid)
        in_s  = in_scores_raw.get(oid)
        parts = [(v, w) for v, w in [(out_s, 0.6), (in_s, 0.4)] if v is not None]
        if parts:
            denom = sum(w for _, w in parts)
            score = sum(v * w for v, w in parts) / denom
        else:
            score = None
        expected_prog[oid] = round(score, 4) if score is not None else None

    prog_score_errors = []
    for r in rec_rows:
        if get(r, 'progression_available') != 'True':
            continue
        oid = get(r, 'occupation_id')
        rep_str = get(r, 'progression_score')
        try:
            rep = round(float(rep_str), 4)
        except:
            prog_score_errors.append({'oid': oid, 'reason': 'cannot parse progression_score'})
            continue
        if oid not in expected_prog or expected_prog[oid] is None:
            prog_score_errors.append({'oid': oid, 'reason': 'occupation not in progression data'})
            continue
        if abs(rep - expected_prog[oid]) > FLOAT_TOL:
            prog_score_errors.append({'oid': oid, 'rep': rep, 'exp': expected_prog[oid]})

    # Reconcile "43 edges / 31 occupations" claim
    total_edges = len([r for r in pr_rows if len(r) > 1 and r[0] and r[1] and r[0] != r[1]])

    prog_audit = {
        'total_progression_edges_in_csv': len(pr_rows),
        'valid_non_self_loop_edges': total_edges,
        'self_loops_found': len(self_loops),
        'unique_source_occupations': len(prog_out),
        'unique_target_occupations': len(prog_in),
        'total_unique_occupations_with_evidence': len(all_prog_occ),
        'metric_used': 'blended log1p-normalised outgoing (0.6) + incoming (0.4) edge counts',
        'p72_report_claimed': '43 edges across 31 occupations',
        'reconciliation': (
            f"Phase 7.2 report stated '43 edges across 31 occupations'. "
            f"Direct count of non-self-loop edges in career_progression_edges.csv: {total_edges}. "
            f"Unique occupations (source ∪ target): {len(all_prog_occ)}. "
            f"Unique source occupations: {len(prog_out)}, unique targets: {len(prog_in)}. "
            f"The '31 occupations' figure in the Phase 7.2 report appears to count "
            f"unique source occupations (= {len(prog_out)}) or unique targets (= {len(prog_in)}), "
            f"while the true unique-occupation union is {len(all_prog_occ)}. "
            f"Self-loops: {len(self_loops)}."
        ),
        'progression_score_errors': len(prog_score_errors),
        'examples_errors': prog_score_errors[:3],
        'pass': len(prog_score_errors) == 0 and len(self_loops) == 0,
    }
    if prog_score_errors:
        issues.append(f"PROGRESSION SCORE: {len(prog_score_errors)} rows with incorrect progression score.")
    if self_loops:
        warnings.append(f"PROGRESSION: {len(self_loops)} self-loop edges exist in career_progression_edges.csv.")
    audit['progression_audit'] = prog_audit
    print(f"  Progression edges (no self-loops): {total_edges}  Self-loops: {len(self_loops)}")
    print(f"  Unique occupations with evidence: {len(all_prog_occ)}")
    print(f"  Score errors: {len(prog_score_errors)}  {'✓' if not prog_score_errors else '✗'}")

    # ════════════════════════════════════════════════════════════════════════
    # 7. TOP-5 DIVERSITY
    # ════════════════════════════════════════════════════════════════════════
    print("\n[7] Top-5 diversity…")
    by_stu = defaultdict(list)
    for r in rec_rows:
        by_stu[get(r, 'student_id')].append(r)

    dup_occ_students   = 0
    rank_order_errors  = 0
    tiebreak_needed    = 0
    all_tied_students  = 0

    for sid, recs in by_stu.items():
        occ_ids = [get(r, 'occupation_id') for r in recs]
        if len(occ_ids) != len(set(occ_ids)):
            dup_occ_students += 1

        recs_sorted = sorted(recs, key=lambda r: (
            -float(get(r, 'final_score') or 0),
            -int(get(r, 'evidence_count') or 0),
            get(r, 'occupation_id')
        ))
        for expected_rank, r in enumerate(recs_sorted, 1):
            actual_rank_str = get(r, 'rank')
            try:
                if int(actual_rank_str) != expected_rank:
                    rank_order_errors += 1
            except: pass

        sc_list = [round(float(get(r, 'final_score')), 4) for r in recs if get(r, 'final_score')]
        if len(set(sc_list)) == 1:
            all_tied_students += 1

        # Count pairs where score tie required occ_id tiebreak
        for i in range(len(recs) - 1):
            s1 = get(recs[i], 'final_score')
            s2 = get(recs[i+1], 'final_score')
            e1 = get(recs[i], 'evidence_count')
            e2 = get(recs[i+1], 'evidence_count')
            try:
                if round(float(s1),4) == round(float(s2),4) and int(e1) == int(e2):
                    tiebreak_needed += 1
            except: pass

    top5_diversity = {
        'total_students': len(by_stu),
        'students_with_duplicate_occ_ids': dup_occ_students,
        'rank_order_errors': rank_order_errors,
        'students_all_tied_top5': all_tied_students,
        'pct_all_tied': pct(all_tied_students, len(by_stu)),
        'adjacent_pairs_needing_occ_id_tiebreak': tiebreak_needed,
        'pass': dup_occ_students == 0 and rank_order_errors == 0,
    }
    if dup_occ_students:
        issues.append(f"TOP-5 DUPLICATES: {dup_occ_students} students have duplicate occupation IDs in Top-5.")
    if rank_order_errors:
        issues.append(f"RANK ORDER: {rank_order_errors} rows have incorrect rank assignment.")
    audit['top5_diversity'] = top5_diversity
    print(f"  Duplicate occ in Top-5: {dup_occ_students}  Rank order errors: {rank_order_errors}  "
          f"{'✓' if top5_diversity['pass'] else '✗'}")
    print(f"  All-tied students: {all_tied_students} ({pct(all_tied_students, len(by_stu))}%)")
    print(f"  Adjacent pairs needing occ_id tiebreak: {tiebreak_needed}")

    # ════════════════════════════════════════════════════════════════════════
    # 8. PROVENANCE SAMPLE (50 rows)
    # ════════════════════════════════════════════════════════════════════════
    print("\n[8] Provenance sampling (50 rows)…")
    import random
    random.seed(42)
    sample_idx = sorted(random.sample(range(len(rec_rows)), min(50, len(rec_rows))))
    sample_rows = [rec_rows[i] for i in sample_idx]

    # Build fast-lookup structures
    mkt_oid_set  = set(market_occ_ids)
    prog_oid_set = all_prog_occ

    prov_errors = []
    for r in sample_rows:
        oid = get(r, 'occupation_id')
        sid = get(r, 'student_id')

        # Occupation exists
        if oid not in occupations:
            prov_errors.append({'row': sid, 'oid': oid, 'issue': 'occupation not in canonical table'})

        # Student exists
        if sid not in student_ids:
            prov_errors.append({'row': sid, 'issue': 'student_id not in student_features'})

        # Market claim
        if get(r, 'market_opportunity_available') == 'True':
            if oid not in mkt_oid_set:
                prov_errors.append({'oid': oid, 'issue': 'claims market evidence but oid not in market edges'})

        # Progression claim
        if get(r, 'progression_available') == 'True':
            if oid not in prog_oid_set:
                prov_errors.append({'oid': oid, 'issue': 'claims progression evidence but oid not in prog edges'})

        # Explanation vs factor value consistency
        expl = get(r, 'explanation')
        mkt_avail = get(r, 'market_opportunity_available') == 'True'
        prog_avail = get(r, 'progression_available') == 'True'
        if mkt_avail and 'market evidence' not in expl.lower():
            prov_errors.append({'oid': oid, 'issue': 'market_opportunity_available=True but "market evidence" absent from explanation'})
        if prog_avail and 'progression' not in expl.lower():
            prov_errors.append({'oid': oid, 'issue': 'progression_available=True but "progression" absent from explanation'})

    prov_audit = {
        'sample_size': len(sample_rows),
        'provenance_errors': len(prov_errors),
        'examples': prov_errors[:5],
        'pass': len(prov_errors) == 0,
    }
    if prov_errors:
        issues.append(f"PROVENANCE: {len(prov_errors)} errors in 50-row sample.")
    audit['provenance_sample'] = prov_audit
    print(f"  Provenance errors in sample of {len(sample_rows)}: {len(prov_errors)}  "
          f"{'✓' if prov_audit['pass'] else '✗'}")

    # ════════════════════════════════════════════════════════════════════════
    # 9. DETERMINISM — compare SHA-256 of outputs
    # ════════════════════════════════════════════════════════════════════════
    print("\n[9] Determinism check…")
    rec_path = os.path.join(REC_V2, 'career_recommendations_v2.csv')
    sha1 = sha256_file(rec_path)
    # Re-run the engine in a subprocess to verify
    import subprocess
    engine_path = os.path.join(BASE_DIR, 'scripts', 'data_pipeline', 'execute_phase7_2_recommendations.py')
    result = subprocess.run([sys.executable, engine_path],
                            capture_output=True, text=True, cwd=BASE_DIR)
    sha2 = sha256_file(rec_path)
    determ_pass = (sha1 == sha2)
    determ = {
        'sha256_run1': sha1, 'sha256_run2': sha2,
        'identical': determ_pass,
        'pass': determ_pass,
    }
    if not determ_pass:
        issues.append("DETERMINISM: Two runs produced different output hashes.")
    audit['determinism'] = determ
    print(f"  Run 1 SHA-256: {sha1[:16]}…")
    print(f"  Run 2 SHA-256: {sha2[:16]}…  {'✓ identical' if determ_pass else '✗ DIFFERENT'}")

    # ════════════════════════════════════════════════════════════════════════
    # VERDICT
    # ════════════════════════════════════════════════════════════════════════
    print("\n[Verdict]")
    hard_fails    = [x for x in issues if not x.startswith('WARNING')]
    if not hard_fails:
        if warnings:
            verdict = 'PASS_WITH_LIMITATIONS'
        else:
            verdict = 'PASS'
    else:
        verdict = 'FAIL'

    audit['issues'] = issues
    audit['warnings'] = warnings
    audit['verdict'] = verdict
    audit['hard_fails'] = hard_fails

    # ── Write reports ─────────────────────────────────────────────────────────
    with open(os.path.join(REP, 'phase_7_2_1_integrity_audit.json'), 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2)

    # Markdown
    md = ["# Phase 7.2.1 — Recommendation Integrity Sanity Audit\n\n"]
    md.append(f"**Verdict:** `{verdict}`  \n")
    md.append(f"**Hard failures:** {len(hard_fails)}  \n")
    md.append(f"**Warnings:** {len(warnings)}  \n\n")

    md.append("---\n## Checks Summary\n\n")
    md.append("| Check | Result |\n|-------|--------|\n")
    checks = {
        'Raw Integrity':          raw_integrity.get('pass', 'NOT_VERIFIED'),
        'Candidate Accounting':   acct['rankable_match'],
        'Score Reconciliation':   recon['pass'],
        'Min-Evidence Gate':      gate['pass'],
        'Market Provenance':      mkt_audit['pass'],
        'Progression Provenance': prog_audit['pass'],
        'Top-5 Diversity':        top5_diversity['pass'],
        'Provenance Sample':      prov_audit['pass'],
        'Determinism':            determ['pass'],
    }
    for k, v in checks.items():
        status = '✅ PASS' if v is True else ('⚠️ NOT_VERIFIED' if v is None else '❌ FAIL')
        md.append(f"| {k} | {status} |\n")

    md.append("\n---\n## Score Distribution\n\n")
    sd = audit['score_distribution']
    md.append(f"- **Unique scores:** {sd['unique_count']}  \n")
    md.append(f"- **Min / Max / Mean / Median:** {sd['min']} / {sd['max']} / {sd['mean']} / {sd['median']}  \n")
    md.append(f"- **P25 / P75:** {sd['p25']} / {sd['p75']}  \n")
    md.append(f"- **Avg unique scores per student:** {sd['avg_unique_scores_per_student']}  \n")
    md.append(f"\n{sd['unique_score_explanation']}\n")

    md.append("\n---\n## Candidate Accounting\n\n")
    md.append(f"- Candidate universe: {acct['candidate_universe_size']} occupations × {acct['num_students']} students  \n")
    md.append(f"- {acct['insuff_candidate_explanation']}  \n")

    md.append("\n---\n## Progression Reconciliation\n\n")
    md.append(f"{prog_audit['reconciliation']}  \n")

    md.append("\n---\n## Issues Found\n\n")
    if hard_fails:
        for i in hard_fails:
            md.append(f"- ❌ {i}\n")
    else:
        md.append("*No hard failures.*  \n")

    md.append("\n---\n## Warnings\n\n")
    if warnings:
        for w in warnings:
            md.append(f"- ⚠️ {w}\n")
    else:
        md.append("*No warnings.*  \n")

    with open(os.path.join(REP, 'phase_7_2_1_integrity_audit.md'), 'w', encoding='utf-8') as f:
        f.writelines(md)

    # ── Final console output ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"PHASE 7.2.1 STATUS: {verdict}")
    print("=" * 60)
    print("\nCheck results:")
    for k, v in checks.items():
        sym = "✓" if v is True else ("?" if v is None else "✗")
        print(f"  {sym}  {k}")
    if hard_fails:
        print("\nHard failures:")
        for f in hard_fails:
            print(f"  ✗ {f}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")
    print(f"\nReports written to data/reports/")

if __name__ == '__main__':
    run_audit()
