import os
import csv
import math
from collections import defaultdict
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE_DIR, 'data')
PROC = os.path.join(DATA, 'processed')
CROSS = os.path.join(DATA, 'crosswalks')
DICTS = os.path.join(DATA, 'dictionaries')

BASE_WEIGHTS = {
    'student_fit':        0.35,
    'education_fit':      0.25,
    'skill_fit':          0.20,
    'market_opportunity': 0.10,
    'progression':        0.10,
}
MIN_FACTORS = 2

def load_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    return (rows[0] if rows else []), (rows[1:] if len(rows) > 1 else [])

def log1p_normalize(values_dict):
    raw = {k: math.log1p(v) for k, v in values_dict.items()}
    if not raw:
        return {}
    mn, mx = min(raw.values()), max(raw.values())
    if mx == mn:
        return {k: None for k in raw}
    return {k: (v - mn) / (mx - mn) for k, v in raw.items()}

def normalize_skill(s):
    import re
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s.lower())).strip()

class RecommendationEngine:
    _instance = None

    def __init__(self):
        self.graph = {}
        self._initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RecommendationEngine()
        return cls._instance

    def initialize(self):
        if self._initialized:
            return
        
        _, occ_rows = load_csv(os.path.join(PROC, 'goguide_entities', 'occupation.csv'))
        occupations = {r[0]: r[1] for r in occ_rows}
        
        _, cce_rows = load_csv(os.path.join(CROSS, 'career_cluster_occupation_edges.csv'))
        cluster_to_occ = defaultdict(set)
        occ_to_cluster = {}
        for r in cce_rows:
            if r[3] == 'MATCHED' and r[2]:
                cluster_to_occ[r[0]].add(r[2])
                occ_to_cluster[r[2]] = r[0]

        _, eo_rows = load_csv(os.path.join(CROSS, 'education_occupation_edges.csv'))
        edu_to_occ = defaultdict(list)
        for r in eo_rows:
            edu_to_occ[r[0]].append((r[1], r[3]))

        _, edu_dict_rows = load_csv(os.path.join(DICTS, 'education_dictionary.csv'))
        field_to_edu_id = {}
        for r in edu_dict_rows:
            fos = r[5].strip().lower() if len(r) > 5 else ''
            raw = r[1].strip().lower()
            if fos: field_to_edu_id[fos] = r[0]
            if raw: field_to_edu_id[raw] = r[0]

        _, os_rows = load_csv(os.path.join(CROSS, 'occupation_skill_edges.csv'))
        occ_required_skills = defaultdict(set)
        for r in os_rows:
            if r[3] == 'ESSENTIAL':
                occ_required_skills[r[0]].add(r[1])

        _, sk_dict_rows = load_csv(os.path.join(DICTS, 'skill_dictionary.csv'))
        skill_name_to_id = {normalize_skill(r[1]): r[0] for r in sk_dict_rows}

        _, mk_rows = load_csv(os.path.join(CROSS, 'occupation_market_edges.csv'))
        real_counts = defaultdict(int)
        synth_counts = defaultdict(int)
        for r in mk_rows:
            if len(r) > 11 and r[11] == 'MATCHED' and r[0]:
                if r[10] == 'REAL_JOB_FEED': real_counts[r[0]] += 1
                elif r[10] == 'SYNTHETIC_PROTOTYPE': synth_counts[r[0]] += 1
        
        real_scores = log1p_normalize(real_counts)
        synth_scores = log1p_normalize(synth_counts)
        market_scores = {}
        for oid in set(real_counts) | set(synth_counts):
            if oid in real_scores and real_scores[oid] is not None:
                market_scores[oid] = {'score': real_scores[oid], 'posting_count': real_counts[oid], 'source_type': 'REAL_JOB_FEED', 'mapping_status': 'MATCHED'}
            elif oid in synth_scores and synth_scores[oid] is not None:
                market_scores[oid] = {'score': synth_scores[oid], 'posting_count': synth_counts[oid], 'source_type': 'SYNTHETIC_PROTOTYPE', 'mapping_status': 'MATCHED'}
            else:
                market_scores[oid] = {'score': None, 'posting_count': real_counts.get(oid,0)+synth_counts.get(oid,0), 'source_type': 'REAL_JOB_FEED' if oid in real_counts else 'SYNTHETIC_PROTOTYPE', 'mapping_status': 'MATCHED_UNDIFFERENTIATED'}

        _, pr_rows = load_csv(os.path.join(CROSS, 'career_progression_edges.csv'))
        prog_out_count = defaultdict(int)
        prog_in_count = defaultdict(int)
        for r in pr_rows:
            if len(r) > 1 and r[0] and r[1]:
                prog_out_count[r[0]] += 1
                prog_in_count[r[1]] += 1
        out_scores = log1p_normalize(dict(prog_out_count))
        in_scores = log1p_normalize(dict(prog_in_count))
        progression_scores = {}
        for oid in set(prog_out_count) | set(prog_in_count):
            out_s = out_scores.get(oid)
            in_s = in_scores.get(oid)
            parts = [x for x in [(out_s, 0.6), (in_s, 0.4)] if x[0] is not None]
            if parts:
                denom = sum(w for _, w in parts)
                score = sum(v*w for v, w in parts) / denom
            else: score = None
            progression_scores[oid] = {'score': round(score, 4) if score is not None else None, 'out_edges': prog_out_count.get(oid, 0), 'in_edges': prog_in_count.get(oid, 0)}

        self.graph = {
            'occupations': occupations,
            'cluster_to_occ': cluster_to_occ,
            'occ_to_cluster': occ_to_cluster,
            'edu_to_occ': edu_to_occ,
            'field_to_edu_id': field_to_edu_id,
            'occ_required_skills': occ_required_skills,
            'skill_name_to_id': skill_name_to_id,
            'market_scores': market_scores,
            'progression_scores': progression_scores
        }
        self._initialized = True

    def recommend(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        self.initialize()
        
        target_career = profile.get('target_career')
        cluster = None
        if target_career:
            tc_lower = target_career.lower()
            for oid, name in self.graph['occupations'].items():
                if name.lower() == tc_lower:
                    cluster = self.graph['occ_to_cluster'].get(oid)
                    break
        
        stream = profile.get('academic_stream')
        student_edu_id = None
        if stream:
            student_edu_id = self.graph['field_to_edu_id'].get(stream.lower())

        matched_occs = self.graph['cluster_to_occ'].get(cluster, set()) if cluster else set()
        candidate_occs = matched_occs | set(self.graph['market_scores'].keys()) | set(self.graph['progression_scores'].keys())
        if student_edu_id:
            candidate_occs |= {oid for oid, _ in self.graph['edu_to_occ'].get(student_edu_id, [])}
        
        if not candidate_occs:
            candidate_occs = set(self.graph['occupations'].keys())

        results = []
        for occ_id in candidate_occs:
            if occ_id not in self.graph['occupations']: continue
            occ_name = self.graph['occupations'][occ_id]

            if cluster and occ_id in matched_occs:
                student_fit, student_fit_avail = 1.0, True
            else:
                student_fit, student_fit_avail = None, False
            
            edu_fit_avail = False
            education_fit = None
            if student_edu_id:
                occ_rels = [rel for oid, rel in self.graph['edu_to_occ'].get(student_edu_id, []) if oid == occ_id]
                if occ_rels:
                    rel = occ_rels[0]
                    education_fit = 1.0 if rel == 'DIRECT' else (0.6 if rel in ('COMMON', 'RELATED') else None)
                    edu_fit_avail = education_fit is not None

            skill_fit_avail = False
            skill_fit = None

            mkt = self.graph['market_scores'].get(occ_id)
            if mkt and mkt['score'] is not None:
                market_opportunity, mkt_avail = round(mkt['score'], 4), True
            else:
                market_opportunity, mkt_avail = None, False

            prog = self.graph['progression_scores'].get(occ_id)
            if prog and prog['score'] is not None:
                progression_score, prog_avail = round(prog['score'], 4), True
            else:
                progression_score, prog_avail = None, False

            factor_values = {
                'student_fit': (student_fit, student_fit_avail),
                'education_fit': (education_fit, edu_fit_avail),
                'skill_fit': (skill_fit, skill_fit_avail),
                'market_opportunity': (market_opportunity, mkt_avail),
                'progression': (progression_score, prog_avail),
            }
            available = {f: v for f, (v, a) in factor_values.items() if a and v is not None}
            evidence_count = len(available)

            if evidence_count >= MIN_FACTORS:
                total_w = sum(BASE_WEIGHTS[f] for f in available)
                eff = {f: BASE_WEIGHTS[f] / total_w for f in available}
                final_score = round(sum(eff[f] * v for f, v in available.items()), 4)
                status = 'RANKABLE'
            else:
                eff = {f: 0.0 for f in available}
                final_score = None
                status = 'INSUFFICIENT_EVIDENCE'
            
            if status == 'RANKABLE':
                # Map for frontend expected schema
                fit_val = available.get('student_fit', final_score)
                mkt_val = available.get('market_opportunity', final_score)
                
                results.append({
                    'occupation_id': occ_id,
                    'occupation_name': occ_name,
                    'title': occ_name,
                    'cluster': cluster if cluster else 'General',
                    'category': cluster if cluster else 'General',
                    'final_score': final_score,
                    'composite_score': final_score,
                    'fit_score': fit_val,
                    'market_score': mkt_val,
                    'financial_score': 0.8, # fallback
                    'risk_score': 0.8,      # fallback
                    'conflict_score': 0.0,
                    'evidence_count': evidence_count,
                    'status': status,
                    'factors': available,
                    'effective_weights': eff
                })
        
        results.sort(key=lambda x: (-x['final_score'], -x['evidence_count'], x['occupation_id']))
        return results[:5]

def get_recommendations(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    return RecommendationEngine.get_instance().recommend(profile)