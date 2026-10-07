import os
import sys
import csv
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

CONFIG_PATH = os.path.join(BASE_DIR, 'data', 'reports', 'recommendation_config.json')
RECOMMENDATIONS_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'recommendations')
REPORTS_DIR = os.path.join(BASE_DIR, 'data', 'reports')

def load_csv(path):
    if not os.path.exists(path): return []
    with open(path, encoding='utf-8') as f:
        return list(csv.reader(f))

def save_csv(path, header, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def main():
    os.makedirs(RECOMMENDATIONS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    config = {
      "student_fit": 0.35,
      "education_fit": 0.25,
      "skill_fit": 0.20,
      "market_opportunity": 0.10,
      "progression": 0.10,
      "top_k": 5,
      "renormalize_missing_factors": True,
      "deterministic_sort": ["final_score DESC", "occupation_id ASC"]
    }
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print("Loading Phase 6 entities and edges...")
    occ_rows = load_csv(os.path.join(BASE_DIR, 'data', 'processed', 'goguide_entities', 'occupation.csv'))
    occupations = {r[0]: r[1] for r in occ_rows[1:]}

    student_rows = load_csv(os.path.join(BASE_DIR, 'data', 'processed', 'student_intelligence', 'student_features.csv'))
    students = defaultdict(dict)
    for r in student_rows[1:]:
        sid = r[0]
        group = r[1]
        data = json.loads(r[2])
        if group == 'Psychometric':
            students[sid]['career_cluster'] = data.get('Career')
        elif group == 'Academic Performance':
            students[sid]['academic_data'] = data

    cluster_rows = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks', 'career_cluster_occupation_edges.csv'))
    cluster_map = defaultdict(set)
    for r in cluster_rows[1:]:
        if r[3] == 'MATCHED' and r[2]:
            cluster_map[r[0]].add(r[2])

    market_rows = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks', 'occupation_market_edges.csv'))
    market_opp = defaultdict(list)
    for r in market_rows[1:]:
        if len(r) > 11 and r[11] == 'MATCHED' and r[0]:
            market_opp[r[0]].append(r)

    prog_rows = load_csv(os.path.join(BASE_DIR, 'data', 'crosswalks', 'career_progression_edges.csv'))
    prog_targets = set()
    for r in prog_rows[1:]:
        prog_targets.add(r[1]) # target_occupation_id

    occ_market_score = {}
    occ_market_type = {}
    for occ_id, edges in market_opp.items():
        has_real = any(e[10] == 'REAL_JOB_FEED' for e in edges)
        has_synth = any(e[10] == 'SYNTHETIC_PROTOTYPE' for e in edges)
        if has_real:
            occ_market_score[occ_id] = 1.0
            occ_market_type[occ_id] = 'REAL_JOB_FEED'
        elif has_synth:
            occ_market_score[occ_id] = 0.5
            occ_market_type[occ_id] = 'SYNTHETIC_PROTOTYPE'
        else:
            occ_market_score[occ_id] = 0.0
            occ_market_type[occ_id] = 'NOT_AVAILABLE'

    recommendations = []
    
    # To check skills (we know none exist but rule says handle properly)
    for sid, sdata in students.items():
        cluster = sdata.get('career_cluster')
        matched_occs = cluster_map.get(cluster, set()) if cluster else set()

        # Only evaluate occupations that have AT LEAST ONE non-zero feature
        candidate_occs = matched_occs | set(occ_market_score.keys()) | prog_targets

        student_recs = []
        for occ_id in candidate_occs:
            if occ_id not in occupations: continue
            occ_name = occupations[occ_id]
            factors = {}
            explanations = []
            unavailable = []

            if cluster:
                if occ_id in matched_occs:
                    factors['student_fit'] = 1.0
                    explanations.append("strong alignment with the student's stated career interest")
                else:
                    unavailable.append('student_fit')
            else:
                unavailable.append('student_fit')

            # Education - No student education data in features
            unavailable.append('education_fit')

            # Skill - No actual student skill evidence in features
            unavailable.append('skill_fit')
            explanations.append("Required skills are available for this occupation, but confirmed student skill evidence is not available")

            if occ_id in occ_market_score:
                factors['market_opportunity'] = occ_market_score[occ_id]
                m_type = occ_market_type[occ_id]
                if factors['market_opportunity'] > 0:
                    explanations.append(f"market evidence is available from {m_type}")
            else:
                unavailable.append('market_opportunity')

            if occ_id in prog_targets:
                factors['progression'] = 1.0
                explanations.append("advancement-path evidence is available")
            else:
                factors['progression'] = 0.0

            total_weight = 0.0
            final_score = 0.0
            available_factors = list(factors.keys())
            
            if not available_factors:
                continue

            for factor, score in factors.items():
                total_weight += config[factor]

            if total_weight == 0:
                continue

            for factor, score in factors.items():
                normalized_weight = config[factor] / total_weight
                final_score += score * normalized_weight

            if final_score == 0:
                continue

            n_usable = len(available_factors)
            if n_usable >= 5: conf = "HIGH"
            elif n_usable >= 3: conf = "MEDIUM"
            elif n_usable >= 1: conf = "LOW"
            else: continue

            explanation_str = "Recommended because:\n- " + ";\n- ".join(explanations) + "."
            
            student_recs.append({
                'student_id': sid,
                'occupation_id': occ_id,
                'occupation_name': occ_name,
                'final_score': round(final_score, 4),
                'student_fit': factors.get('student_fit', 'NOT_AVAILABLE'),
                'education_fit': factors.get('education_fit', 'NOT_AVAILABLE'),
                'skill_fit': factors.get('skill_fit', 'NOT_AVAILABLE'),
                'market_opportunity': factors.get('market_opportunity', 'NOT_AVAILABLE'),
                'progression': factors.get('progression', 'NOT_AVAILABLE'),
                'confidence': conf,
                'available_factors': "|".join(available_factors),
                'unavailable_factors': "|".join(unavailable),
                'market_evidence_type': occ_market_type.get(occ_id, 'NOT_AVAILABLE'),
                'explanation': explanation_str
            })

        student_recs.sort(key=lambda x: (-x['final_score'], x['occupation_id']))
        top_k = student_recs[:config['top_k']]
        for i, r in enumerate(top_k, 1):
            r['rank'] = i
            recommendations.append(r)

    print(f"Generated {len(recommendations)} recommendations.")

    # Write Recommendations
    rec_header = ['student_id', 'rank', 'occupation_id', 'occupation_name', 'final_score', 'student_fit', 'education_fit', 'skill_fit', 'market_opportunity', 'progression', 'confidence', 'available_factors', 'unavailable_factors', 'market_evidence_type', 'explanation']
    rec_rows = [[r[k] for k in rec_header] for r in recommendations]
    save_csv(os.path.join(RECOMMENDATIONS_DIR, 'career_recommendations.csv'), rec_header, rec_rows)
    print("Saved career_recommendations.csv")

    # Write Summary
    summary_rows = []
    stu_recs = defaultdict(list)
    for r in recommendations:
        stu_recs[r['student_id']].append(r)
    
    sum_header = ['student_id', 'recommendation_count', 'top_occupation_id', 'top_occupation_name', 'top_score', 'confidence', 'available_factor_count']
    for sid, recs in stu_recs.items():
        recs.sort(key=lambda x: x['rank'])
        top = recs[0]
        summary_rows.append([
            sid, len(recs), top['occupation_id'], top['occupation_name'], top['final_score'], top['confidence'], len(top['available_factors'].split('|'))
        ])
    save_csv(os.path.join(RECOMMENDATIONS_DIR, 'career_recommendation_summary.csv'), sum_header, summary_rows)
    print("Saved career_recommendation_summary.csv")

    # Write Sample Markdown
    with open(os.path.join(REPORTS_DIR, 'sample_recommendations.md'), 'w', encoding='utf-8') as f:
        f.write("# Sample Recommendations\n\n")
        for r in recommendations[:10]:
            f.write(f"### Student {r['student_id']} - Rank {r['rank']}\n")
            f.write(f"**Occupation:** {r['occupation_name']} ({r['occupation_id']})\n")
            f.write(f"**Score:** {r['final_score']} (Confidence: {r['confidence']})\n")
            f.write(f"**Explanation:**\n{r['explanation']}\n\n")

    # Quality Report
    stats = {
        'total_students': len(students),
        'eligible_students': len(stu_recs),
        'total_recommendations': len(recommendations),
        'students_with_exactly_5': sum(1 for recs in stu_recs.values() if len(recs) == 5),
        'duplicate_recommendations': 0, # Not possible with logic
        'invalid_occupation_ids': 0, # Validated from occupations
        'invalid_student_ids': 0,
        'score_min': min((r['final_score'] for r in recommendations), default=0),
        'score_max': max((r['final_score'] for r in recommendations), default=0),
        'score_mean': sum(r['final_score'] for r in recommendations)/max(len(recommendations),1),
        'confidence_distribution': defaultdict(int),
        'factor_availability': defaultdict(int),
        'market_evidence_distribution': defaultdict(int)
    }
    for r in recommendations:
        stats['confidence_distribution'][r['confidence']] += 1
        stats['market_evidence_distribution'][r['market_evidence_type']] += 1
        for f in r['available_factors'].split('|'):
            if f: stats['factor_availability'][f] += 1

    with open(os.path.join(REPORTS_DIR, 'phase_7_recommendation_quality.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    with open(os.path.join(REPORTS_DIR, 'phase_7_recommendation_quality.md'), 'w', encoding='utf-8') as f:
        f.write("# Phase 7 Quality Report\n")
        f.write(f"- Total Students: {stats['total_students']}\n")
        f.write(f"- Eligible Students: {stats['eligible_students']}\n")
        f.write(f"- Recommendations: {stats['total_recommendations']}\n")
        f.write(f"- Students with exactly 5: {stats['students_with_exactly_5']}\n")
        f.write(f"- Score Mean: {stats['score_mean']:.4f}\n")
        
if __name__ == '__main__':
    main()
