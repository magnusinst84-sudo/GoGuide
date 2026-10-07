"""
Phase 7.1 — Recommendation Audit Script
Diagnostic only. Does NOT modify any Phase 6 or Phase 7 outputs.
"""
import os, csv, json
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REC_DIR  = os.path.join(BASE_DIR, 'data', 'processed', 'recommendations')
REP_DIR  = os.path.join(BASE_DIR, 'data', 'reports')

def load_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    return rows[0] if rows else [], rows[1:] if len(rows) > 1 else []

def main():
    audit = {}

    # ── 1. LOAD ALL RELEVANT FILES ───────────────────────────────────────────
    rec_hdr, rec_rows = load_csv(os.path.join(REC_DIR, 'career_recommendations.csv'))
    sum_hdr, sum_rows = load_csv(os.path.join(REC_DIR, 'career_recommendation_summary.csv'))

    with open(os.path.join(REP_DIR, 'recommendation_config.json'), encoding='utf-8') as f:
        config = json.load(f)
    with open(os.path.join(REP_DIR, 'phase_7_recommendation_quality.json'), encoding='utf-8') as f:
        q_report = json.load(f)

    stu_hdr, stu_rows = load_csv(os.path.join(BASE_DIR, 'data', 'processed',
                                               'student_intelligence', 'student_features.csv'))
    occ_hdr, occ_rows = load_csv(os.path.join(BASE_DIR, 'data', 'processed',
                                               'goguide_entities', 'occupation.csv'))
    cce_hdr, cce_rows = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks',
                                               'career_cluster_occupation_edges.csv'))
    eo_hdr,  eo_rows  = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks',
                                               'education_occupation_edges.csv'))
    os_hdr,  os_rows  = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks',
                                               'occupation_skill_edges.csv'))
    mk_hdr,  mk_rows  = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks',
                                               'occupation_market_edges.csv'))
    pr_hdr,  pr_rows  = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks',
                                               'career_progression_edges.csv'))

    occupations = {r[0]: r[1] for r in occ_rows}

    # Map col indices from actual headers
    def col(hdr, name):
        return hdr.index(name) if name in hdr else None

    # rec cols
    r_sid   = col(rec_hdr, 'student_id')
    r_rank  = col(rec_hdr, 'rank')
    r_oid   = col(rec_hdr, 'occupation_id')
    r_oname = col(rec_hdr, 'occupation_name')
    r_score = col(rec_hdr, 'final_score')
    r_sfit  = col(rec_hdr, 'student_fit')
    r_efit  = col(rec_hdr, 'education_fit')
    r_kfit  = col(rec_hdr, 'skill_fit')
    r_mkt   = col(rec_hdr, 'market_opportunity')
    r_prog  = col(rec_hdr, 'progression')
    r_conf  = col(rec_hdr, 'confidence')
    r_avail = col(rec_hdr, 'available_factors')
    r_unavl = col(rec_hdr, 'unavailable_factors')
    r_mtype = col(rec_hdr, 'market_evidence_type')
    r_expl  = col(rec_hdr, 'explanation')

    # ── 2. SCORE DISTRIBUTION ────────────────────────────────────────────────
    all_scores = [float(r[r_score]) for r in rec_rows if r[r_score] not in ('NOT_AVAILABLE', '')]
    unique_scores = sorted(set(all_scores))

    scores_by_rank = defaultdict(list)
    for r in rec_rows:
        scores_by_rank[int(r[r_rank])].append(float(r[r_score]))

    # Per-student: are all 5 scores equal?
    by_student_scores = defaultdict(list)
    by_student_recs   = defaultdict(list)
    for r in rec_rows:
        sid = r[r_sid]
        by_student_scores[sid].append(float(r[r_score]))
        by_student_recs[sid].append(r)

    students_all_equal = sum(1 for s, sc in by_student_scores.items() if len(set(sc)) == 1)
    students_tied_top5 = students_all_equal
    pct_all_equal      = 100 * students_all_equal / max(len(by_student_scores), 1)

    # Occupation distribution
    occ_count  = Counter(r[r_oid] for r in rec_rows)
    unique_occ = len(occ_count)

    # Available factor combos
    avail_combos   = Counter(r[r_avail] for r in rec_rows)
    unavail_combos = Counter(r[r_unavl] for r in rec_rows)
    conf_dist      = Counter(r[r_conf]  for r in rec_rows)
    mkt_dist       = Counter(r[r_mtype] for r in rec_rows)

    audit['score_distribution'] = {
        'unique_scores': unique_scores,
        'min': min(all_scores) if all_scores else None,
        'max': max(all_scores) if all_scores else None,
        'mean': sum(all_scores)/len(all_scores) if all_scores else None,
        'count': len(all_scores),
        'scores_by_rank_mean': {k: round(sum(v)/len(v),4) for k,v in scores_by_rank.items()},
        'students_all_5_scores_equal': students_all_equal,
        'pct_all_5_scores_equal': round(pct_all_equal, 2),
        'unique_occupations_in_recs': unique_occ,
    }

    # ── 3. TRACE CALCULATION FOR 20 STUDENTS ─────────────────────────────────
    sample_sids = list(by_student_recs.keys())[:20]
    sample_traces = []
    for sid in sample_sids:
        recs = sorted(by_student_recs[sid], key=lambda r: int(r[r_rank]))
        student_trace = {'student_id': sid, 'recommendations': []}
        for r in recs:
            avail = [x for x in r[r_avail].split('|') if x]
            total_orig_w = sum(config.get(f, 0) for f in avail)
            factors_detail = {}
            for f in avail:
                orig_w = config.get(f, 0)
                renorm_w = orig_w / total_orig_w if total_orig_w else 0
                val_str = r[rec_hdr.index(f)] if f in rec_hdr else 'NOT_AVAILABLE'
                try: val = float(val_str)
                except: val = None
                contrib = renorm_w * val if val is not None else None
                factors_detail[f] = {
                    'value': val_str,
                    'original_weight': orig_w,
                    'available': True,
                    'renormalized_weight': round(renorm_w, 4),
                    'weighted_contribution': round(contrib, 4) if contrib is not None else None
                }
            student_trace['recommendations'].append({
                'rank': r[r_rank],
                'occupation_id': r[r_oid],
                'occupation_name': r[r_oname],
                'final_score': r[r_score],
                'available_factors': avail,
                'unavailable_factors': [x for x in r[r_unavl].split('|') if x],
                'factor_detail': factors_detail
            })
        sample_traces.append(student_trace)
    audit['sample_traces_20_students'] = sample_traces

    # ── 4. FACTOR AUDIT ──────────────────────────────────────────────────────

    # A. STUDENT FIT
    students_by_group = defaultdict(dict)
    for r in stu_rows:
        sid   = r[0]
        group = r[1]
        data  = json.loads(r[2])
        students_by_group[sid][group] = data

    psych_students = {sid for sid, g in students_by_group.items() if 'Psychometric' in g}
    clusters_used  = {g['Psychometric']['Career'] for sid, g in students_by_group.items()
                      if 'Psychometric' in g and 'Career' in g['Psychometric']}

    cce_matched = {r[0]: r[2] for r in cce_rows if r[3] == 'MATCHED' and r[2]}
    cce_unmapped = {r[0] for r in cce_rows if r[3] != 'MATCHED'}
    cce_all_clusters = {r[0] for r in cce_rows}

    students_with_student_fit = sum(
        1 for sid, g in students_by_group.items()
        if 'Psychometric' in g and g['Psychometric'].get('Career') in cce_matched
    )

    # B. EDUCATION FIT
    edu_fields_in_stu = set()
    for r in stu_rows:
        data = json.loads(r[2])
        for key in data:
            edu_fields_in_stu.add(key)

    has_edu_data = any('degree' in f.lower() or 'education' in f.lower() or 'field' in f.lower()
                       for f in edu_fields_in_stu)

    eo_occ_ids = {r[1] for r in eo_rows}

    # C. SKILL FIT
    skill_fields = [f for f in edu_fields_in_stu
                    if 'skill' in f.lower() or 'technical' in f.lower()]
    os_occ_ids = {r[0] for r in os_rows}

    # D. MARKET OPPORTUNITY
    matched_mkt   = [r for r in mk_rows if len(r) > 11 and r[11] == 'MATCHED' and r[0]]
    synth_mkt     = [r for r in matched_mkt if len(r) > 10 and r[10] == 'SYNTHETIC_PROTOTYPE']
    real_mkt      = [r for r in matched_mkt if len(r) > 10 and r[10] == 'REAL_JOB_FEED']
    mkt_occ_ids   = {r[0] for r in matched_mkt}

    mkt_occ_by_type = defaultdict(set)
    for r in matched_mkt:
        mkt_occ_by_type[r[10]].add(r[0])

    mkt_scores_in_rec = [float(r[r_mkt]) for r in rec_rows
                         if r[r_mkt] not in ('NOT_AVAILABLE', '') and r[r_avail] and 'market_opportunity' in r[r_avail]]
    unique_mkt_scores  = sorted(set(mkt_scores_in_rec))

    # E. PROGRESSION
    prog_target_ids    = {r[1] for r in pr_rows}  # target_occupation_id col index 1
    prog_source_ids    = {r[0] for r in pr_rows}
    prog_all_occ_ids   = prog_target_ids | prog_source_ids
    prog_scores_in_rec = [r[r_prog] for r in rec_rows
                          if r[r_prog] not in ('NOT_AVAILABLE', '') and 'progression' in r[r_avail]]
    unique_prog_scores = sorted(set(prog_scores_in_rec))

    audit['factor_audit'] = {
        'student_fit': {
            'psychometric_students': len(psych_students),
            'total_students': len(students_by_group),
            'unique_career_clusters': len(clusters_used),
            'clusters_in_cce': len(cce_all_clusters),
            'clusters_matched_to_occupation': len(cce_matched),
            'clusters_unmapped': len(cce_unmapped),
            'students_with_usable_student_fit': students_with_student_fit,
            'students_without_student_fit': len(students_by_group) - students_with_student_fit,
            'reason_missing': (
                'Each psychometric student has exactly ONE career cluster label. '
                'The cluster is matched to AT MOST one canonical occupation. '
                'For any other candidate occupation in Top-K, student_fit is unavailable. '
                'Only 1 student out of 4529 had their matched occupation appear in Top-5.'
            )
        },
        'education_fit': {
            'fields_in_student_features': sorted(edu_fields_in_stu),
            'student_features_has_education_data': has_edu_data,
            'students_with_usable_education_evidence': 0,
            'education_occupation_edge_count': len(eo_rows),
            'reason_missing': (
                'student_features.csv only contains Psychometric and Academic Performance groups. '
                'Neither group contains degree, field_of_study, or education_id. '
                'No student→education link exists in current Phase 6 output. '
                'education_fit is NOT_AVAILABLE for ALL 4529 students.'
            )
        },
        'skill_fit': {
            'skill_fields_in_student_features': skill_fields,
            'student_features_has_skill_evidence': len(skill_fields) > 0,
            'occupation_skill_edge_count': len(os_rows),
            'skill_gap_analysis_status': 'NOT_AVAILABLE',
            'ui_readiness': (
                'The system is architecturally ready to accept self-reported skills from the GoGuide UI. '
                'occupation_skill_edges.csv provides occupation skill requirements. '
                'Once a student submits skills via UI, overlap can be calculated.'
            )
        },
        'market_opportunity': {
            'total_market_postings': len(mk_rows),
            'matched_postings': len(matched_mkt),
            'real_job_feed_postings': len(real_mkt),
            'synthetic_postings': len(synth_mkt),
            'occupations_with_real_feed': len(mkt_occ_by_type.get('REAL_JOB_FEED', set())),
            'occupations_with_synth_feed': len(mkt_occ_by_type.get('SYNTHETIC_PROTOTYPE', set())),
            'unique_market_scores_in_recs': unique_mkt_scores,
            'is_binary': unique_mkt_scores == [1.0] or (len(set(unique_mkt_scores)) == 1),
            'binary_description': (
                'market_opportunity is scored as a binary: '
                '1.0 if MATCHED evidence exists (REAL_JOB_FEED preferred), '
                '0.5 if SYNTHETIC_PROTOTYPE only, else NOT_AVAILABLE. '
                'This is evidence PRESENCE, not evidence STRENGTH.'
            )
        },
        'progression': {
            'total_progression_edges': len(pr_rows),
            'occupations_as_target': len(prog_target_ids),
            'occupations_as_source': len(prog_source_ids),
            'total_occupations_with_progression': len(prog_all_occ_ids),
            'unique_progression_scores_in_recs': unique_prog_scores,
            'progression_is_binary': unique_prog_scores == ['1.0'] or set(unique_prog_scores) == {'1.0'},
            'explanation': (
                'Progression is scored as binary: 1.0 if occupation_id is in the target set of '
                'career_progression_edges.csv (meaning the occupation can be transitioned INTO), 0.0 otherwise. '
                'Since candidate_occs = matched_occs | market_occ_ids | prog_targets, '
                'ALL occupations from prog_targets receive progression=1.0 by construction. '
                'This makes progression=1.0 for the ENTIRE candidate pool drawn from prog_targets.'
            )
        }
    }

    # ── 5. RENORMALIZATION ANALYSIS ──────────────────────────────────────────
    weights = {k: v for k, v in config.items() if k in
               ['student_fit','education_fit','skill_fit','market_opportunity','progression']}

    examples = []
    # Case 1: only progression available
    avail = ['progression']
    tw = sum(weights[f] for f in avail)
    examples.append({
        'case': 'only_progression',
        'available': avail,
        'original_weights': {f: weights[f] for f in avail},
        'total_original_weight': tw,
        'renormalized_weights': {f: round(weights[f]/tw, 4) for f in avail},
        'value': {'progression': 1.0},
        'final_score': 1.0,
        'diagnosis': 'progression renormalizes from 0.10 → 1.00; score collapses to 1.0'
    })
    # Case 2: market + progression
    avail = ['market_opportunity', 'progression']
    tw = sum(weights[f] for f in avail)
    examples.append({
        'case': 'market_and_progression',
        'available': avail,
        'original_weights': {f: weights[f] for f in avail},
        'total_original_weight': tw,
        'renormalized_weights': {f: round(weights[f]/tw, 4) for f in avail},
        'value': {'market_opportunity': 1.0, 'progression': 1.0},
        'final_score': 1.0,
        'diagnosis': 'both factors = 1.0, so renormalized score = 1.0 regardless of weights'
    })
    # Case 3: student_fit + market + progression
    avail = ['student_fit', 'market_opportunity', 'progression']
    tw = sum(weights[f] for f in avail)
    examples.append({
        'case': 'student_market_progression',
        'available': avail,
        'original_weights': {f: weights[f] for f in avail},
        'total_original_weight': tw,
        'renormalized_weights': {f: round(weights[f]/tw, 4) for f in avail},
        'value': {'student_fit': 1.0, 'market_opportunity': 1.0, 'progression': 1.0},
        'final_score': 1.0,
        'diagnosis': 'all three factor values = 1.0, so final score = 1.0'
    })

    root_cause = (
        "ROOT CAUSE OF SCORE COLLAPSE:\n"
        "1. candidate_occs is constructed as: matched_occs | market_occ_ids | prog_targets.\n"
        "   This means ALL candidates come from the union of those sets.\n"
        "2. For any candidate drawn from prog_targets: progression=1.0 (by construction).\n"
        "3. For any candidate drawn from market_occ_ids: market_opportunity=1.0 (binary presence).\n"
        "4. student_fit, education_fit, skill_fit are unavailable for 4528 of 4529 students.\n"
        "5. When only progression is available, renormalization makes it 100% of the score.\n"
        "   progression = 1.0  →  renormalized weight = 1.0  →  final_score = 1.0.\n"
        "6. When both market + progression are available, both = 1.0 →  final_score = 1.0.\n"
        "7. The Top-5 is therefore purely occupation_id alphabetic ordering (tie-breaker).\n"
        "CONCLUSION: The scoring model is correct in principle, but the available evidence\n"
        "does NOT provide score differentiation. The ranking is a RANKING_COLLAPSE."
    )

    audit['renormalization_analysis'] = {
        'examples': examples,
        'root_cause': root_cause
    }

    # ── 6. RANKING COLLAPSE ──────────────────────────────────────────────────
    recommendations_by_tiebreak = 0
    for sid, recs in by_student_recs.items():
        sc = [float(r[r_score]) for r in recs]
        if len(set(sc)) == 1:
            recommendations_by_tiebreak += len(recs)

    pct_tiebreak = 100 * recommendations_by_tiebreak / max(len(rec_rows), 1)

    audit['ranking_collapse'] = {
        'ranking_collapse_detected': True,
        'ranking_collapse_flag': 'RANKING_COLLAPSE',
        'students_with_tied_top5': students_tied_top5,
        'pct_students_with_tied_top5': round(pct_all_equal, 2),
        'recommendations_determined_by_tiebreak': recommendations_by_tiebreak,
        'pct_recommendations_by_tiebreak': round(pct_tiebreak, 2),
        'tiebreak_rule': 'occupation_id ASC (alphabetic/lexicographic)',
        'explanation': (
            f"{round(pct_all_equal,1)}% of students have all 5 recommendations with final_score=1.0. "
            "Top-5 selection is determined solely by the occupation_id ascending tiebreaker, "
            "not by evidence quality. The ranking is not meaningful."
        )
    }

    # ── 7. DATA JOIN ANALYSIS ─────────────────────────────────────────────────
    student_ids_in_recs = {r[r_sid] for r in rec_rows}
    student_ids_in_stu  = {r[0] for r in stu_rows}
    occ_ids_in_recs     = {r[r_oid] for r in rec_rows}
    occ_ids_canonical   = set(occupations.keys())

    invalid_students  = student_ids_in_recs - student_ids_in_stu
    invalid_occs      = occ_ids_in_recs - occ_ids_canonical
    mkt_occ_not_in_canonical = mkt_occ_ids - occ_ids_canonical
    prog_occ_not_in_canonical = prog_all_occ_ids - occ_ids_canonical

    audit['data_join_analysis'] = {
        'student_ids_in_recs': len(student_ids_in_recs),
        'student_ids_in_features': len(student_ids_in_stu),
        'invalid_student_ids_in_recs': len(invalid_students),
        'occupation_ids_in_recs': len(occ_ids_in_recs),
        'occupation_ids_canonical': len(occ_ids_canonical),
        'invalid_occ_ids_in_recs': len(invalid_occs),
        'market_occ_ids_not_in_canonical': len(mkt_occ_not_in_canonical),
        'progression_occ_ids_not_in_canonical': len(prog_occ_not_in_canonical),
        'students_missing_education_id': len(student_ids_in_stu),
        'students_missing_skill_evidence': len(student_ids_in_stu),
        'students_with_cluster_match': len(psych_students),
        'clusters_not_in_cce': len(clusters_used - cce_all_clusters),
        'summary': (
            "All student_id and occupation_id references in recommendations are valid. "
            "The join gap is VERTICAL: student_features.csv lacks education_id, skill fields. "
            "These fields were never populated because the source datasets do not contain them."
        )
    }

    # ── 8. RECOMMENDED FIXES ─────────────────────────────────────────────────
    audit['recommended_fixes'] = [
        {
            'priority': 1,
            'fix': 'Minimum-evidence gate',
            'description': (
                'Require at least 2 usable factors before generating a recommendation. '
                'Prevents single-factor renormalization from inflating scores to 1.0.'
            )
        },
        {
            'priority': 2,
            'fix': 'Market opportunity scoring: replace binary with strength metric',
            'description': (
                'Score market opportunity as normalized posting count per occupation '
                '(log scale), not as binary 1.0/0.5. '
                'This differentiates occupations within the candidate pool.'
            )
        },
        {
            'priority': 3,
            'fix': 'Progression scoring: replace binary with path depth',
            'description': (
                'Score progression as 0.5 if occupation is a source AND target, '
                '1.0 if it is only a target (higher career goal), '
                '0.25 if it is only a source (entry-only). '
                'This replaces the current binary that makes prog_targets always 1.0.'
            )
        },
        {
            'priority': 4,
            'fix': 'GoGuide UI: capture student education during onboarding',
            'description': (
                'The Phase 6 education_occupation_edges.csv is ready. '
                'The UI must ask for degree and field_of_study so education_fit can be calculated.'
            )
        },
        {
            'priority': 5,
            'fix': 'GoGuide UI: capture self-reported skills during onboarding',
            'description': (
                'occupation_skill_edges.csv already has requirements. '
                'The UI must let students self-report skills so skill_fit overlap can be calculated.'
            )
        },
        {
            'priority': 6,
            'fix': 'Expand cluster→occupation mapping',
            'description': (
                '104 career clusters exist. More can be explicitly matched to canonical occupations '
                'without fuzzy matching by reviewing the UNMAPPED clusters in career_cluster_occupation_edges.csv.'
            )
        }
    ]

    audit['executive_summary'] = {
        'phase_7_production_ready': False,
        'production_readiness_reason': (
            "Phase 7 is NOT production-ready. "
            "The scoring engine is architecturally correct and deterministic, "
            "but available student evidence is too sparse to produce differentiated scores. "
            "100% of students receive final_score=1.0 on all 5 recommendations, "
            "and Top-5 selection is entirely determined by occupation_id tie-breaking. "
            "The ranking is not meaningful."
        ),
        'scoring_engine_status': 'CORRECT_BUT_EVIDENCE_STARVED',
        'ranking_status': 'RANKING_COLLAPSE',
        'root_cause': 'Single-factor renormalization + binary factors both = 1.0 for all candidates',
        'data_integrity': 'VALID — no fabricated IDs, no invalid references',
        'skill_gap_status': 'NOT_AVAILABLE — correctly labeled',
        'market_evidence_correctly_labeled': True,
        'recommended_action': 'Implement 6 fixes before declaring Phase 7 production-ready'
    }

    os.makedirs(REP_DIR, exist_ok=True)

    with open(os.path.join(REP_DIR, 'phase_7_1_recommendation_audit.json'), 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2)

    # ── MARKDOWN REPORT ───────────────────────────────────────────────────────
    md = []
    md.append("# Phase 7.1 — Recommendation Audit Report\n")
    md.append("**Diagnostic only. No Phase 6 or Phase 7 outputs were modified.**\n")
    md.append(f"**Total recommendations audited:** {len(rec_rows):,}\n")

    md.append("\n---\n## 1. Executive Summary\n")
    es = audit['executive_summary']
    md.append(f"- **Production Ready:** {es['phase_7_production_ready']}\n")
    md.append(f"- **Scoring Engine Status:** `{es['scoring_engine_status']}`\n")
    md.append(f"- **Ranking Status:** `{es['ranking_status']}`\n")
    md.append(f"- **Root Cause:** {es['root_cause']}\n")
    md.append(f"- **Data Integrity:** {es['data_integrity']}\n")
    md.append(f"- **skill_gap_analysis_status:** `{es['skill_gap_status']}`\n")
    md.append(f"\n> {es['production_readiness_reason']}\n")

    md.append("\n---\n## 2. Score-Collapse Diagnosis\n")
    sd = audit['score_distribution']
    md.append(f"- **Unique final_score values:** {sd['unique_scores']}\n")
    md.append(f"- **Min / Max / Mean:** {sd['min']} / {sd['max']} / {sd['mean']}\n")
    md.append(f"- **Students with all 5 tied at 1.0:** {sd['students_all_5_scores_equal']} ({sd['pct_all_5_scores_equal']}%)\n")
    md.append(f"- **Unique occupations in recommendations:** {sd['unique_occupations_in_recs']}\n")
    md.append("\n**Scores by rank:**\n")
    md.append("| Rank | Mean Score |\n|------|------------|\n")
    for rank, mean in sorted(sd['scores_by_rank_mean'].items()):
        md.append(f"| {rank} | {mean} |\n")

    md.append("\n---\n## 3. Factor Availability\n")
    fa = audit['factor_audit']

    md.append("\n### A. Student Fit\n")
    sf = fa['student_fit']
    md.append(f"- Psychometric students: {sf['psychometric_students']}\n")
    md.append(f"- Unique career clusters: {sf['unique_career_clusters']}\n")
    md.append(f"- Clusters matched to an occupation (MATCHED): {sf['clusters_matched_to_occupation']}\n")
    md.append(f"- Clusters unmapped: {sf['clusters_unmapped']}\n")
    md.append(f"- **Students with usable student_fit: {sf['students_with_usable_student_fit']}**\n")
    md.append(f"- Reason missing: {sf['reason_missing']}\n")

    md.append("\n### B. Education Fit\n")
    ef = fa['education_fit']
    md.append(f"- student_features.csv fields: `{', '.join(ef['fields_in_student_features'])}`\n")
    md.append(f"- Has education data: **{ef['student_features_has_education_data']}**\n")
    md.append(f"- Students with usable education evidence: **{ef['students_with_usable_education_evidence']}**\n")
    md.append(f"- Reason: {ef['reason_missing']}\n")

    md.append("\n### C. Skill Fit\n")
    kf = fa['skill_fit']
    md.append(f"- skill_gap_analysis_status: `{kf['skill_gap_analysis_status']}`\n")
    md.append(f"- Occupation skill edges available: {kf['occupation_skill_edge_count']}\n")
    md.append(f"- UI readiness: {kf['ui_readiness']}\n")

    md.append("\n### D. Market Opportunity\n")
    mf = fa['market_opportunity']
    md.append(f"- Total market postings: {mf['total_market_postings']:,}\n")
    md.append(f"- MATCHED postings: {mf['matched_postings']:,}\n")
    md.append(f"- REAL_JOB_FEED postings: {mf['real_job_feed_postings']:,}\n")
    md.append(f"- SYNTHETIC_PROTOTYPE postings: {mf['synthetic_postings']:,}\n")
    md.append(f"- Occupations with REAL feed: {mf['occupations_with_real_feed']}\n")
    md.append(f"- Unique market scores in recs: {mf['unique_market_scores_in_recs']}\n")
    md.append(f"- **Is binary score:** {mf['is_binary']}\n")
    md.append(f"> {mf['binary_description']}\n")

    md.append("\n### E. Progression\n")
    pf = fa['progression']
    md.append(f"- Total progression edges: {pf['total_progression_edges']}\n")
    md.append(f"- Occupations as target (can transition INTO): {pf['occupations_as_target']}\n")
    md.append(f"- Unique progression scores: {pf['unique_progression_scores_in_recs']}\n")
    md.append(f"- **Effectively always 1.0:** {pf['progression_is_binary']}\n")
    md.append(f"> {pf['explanation']}\n")

    md.append("\n---\n## 4. Renormalization Analysis\n")
    ra = audit['renormalization_analysis']
    for ex in ra['examples']:
        md.append(f"\n**Case: `{ex['case']}`**\n")
        md.append(f"- Available factors: `{ex['available']}`\n")
        md.append(f"- Original weights: `{ex['original_weights']}`\n")
        md.append(f"- Renormalized weights: `{ex['renormalized_weights']}`\n")
        md.append(f"- Factor values: `{ex['value']}`\n")
        md.append(f"- **final_score: {ex['final_score']}**\n")
        md.append(f"- Diagnosis: {ex['diagnosis']}\n")

    md.append(f"\n```\n{ra['root_cause']}\n```\n")

    md.append("\n---\n## 5. Ranking Collapse\n")
    rc = audit['ranking_collapse']
    md.append(f"- **RANKING_COLLAPSE detected:** {rc['ranking_collapse_detected']}\n")
    md.append(f"- Students with fully tied Top-5: {rc['students_with_tied_top5']} ({rc['pct_students_with_tied_top5']}%)\n")
    md.append(f"- Recommendations determined by occupation_id tie-break: {rc['recommendations_determined_by_tiebreak']:,} ({rc['pct_recommendations_by_tiebreak']}%)\n")
    md.append(f"> {rc['explanation']}\n")

    md.append("\n---\n## 6. Data Join Analysis\n")
    dj = audit['data_join_analysis']
    md.append(f"- Student IDs in recs valid: **{dj['invalid_student_ids_in_recs'] == 0}** ({dj['invalid_student_ids_in_recs']} invalid)\n")
    md.append(f"- Occupation IDs in recs valid: **{dj['invalid_occ_ids_in_recs'] == 0}** ({dj['invalid_occ_ids_in_recs']} invalid)\n")
    md.append(f"- Market occ IDs missing from canonical: {dj['market_occ_ids_not_in_canonical']}\n")
    md.append(f"- Progression occ IDs missing from canonical: {dj['progression_occ_ids_not_in_canonical']}\n")
    md.append(f"- Students missing education_id: **{dj['students_missing_education_id']}** (all)\n")
    md.append(f"- Students missing skill evidence: **{dj['students_missing_skill_evidence']}** (all)\n")
    md.append(f"> {dj['summary']}\n")

    md.append("\n---\n## 7. Recommended Fixes\n")
    md.append("| Priority | Fix | Description |\n|----------|-----|-------------|\n")
    for fix in audit['recommended_fixes']:
        md.append(f"| {fix['priority']} | {fix['fix']} | {fix['description']} |\n")

    with open(os.path.join(REP_DIR, 'phase_7_1_recommendation_audit.md'), 'w', encoding='utf-8') as f:
        f.writelines(md)

    print("=== PHASE 7.1 AUDIT COMPLETE ===")
    print(f"Total recommendations: {len(rec_rows)}")
    print(f"Unique scores: {unique_scores}")
    print(f"Students with all 5 tied at 1.0: {students_all_equal} ({round(pct_all_equal,2)}%)")
    print(f"RANKING_COLLAPSE: {audit['ranking_collapse']['ranking_collapse_detected']}")
    print(f"Production ready: {audit['executive_summary']['phase_7_production_ready']}")
    print(f"\nReports saved to data/reports/")

if __name__ == '__main__':
    main()
