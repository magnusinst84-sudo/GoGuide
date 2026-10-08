import os
import csv
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PROC = os.path.join(BASE_DIR, 'data', 'processed')

def load_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    return (rows[0] if rows else []), (rows[1:] if len(rows) > 1 else [])

class PathwayEngine:
    _instance = None
    
    def __init__(self):
        self.edu_pathways = {}
        self.occ_to_edu = {}
        self._initialized = False
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PathwayEngine()
        return cls._instance
        
    def initialize(self):
        if self._initialized: return
        
        headers, rows = load_csv(os.path.join(PROC, 'prism_education_career', 'education_pathways.csv'))
        for r in rows:
            if len(r) > 0:
                self.edu_pathways[r[0]] = {headers[i]: r[i] for i in range(len(headers))}
                
        h_eo, eo_rows = load_csv(os.path.join(PROC, 'prism_education_career', 'education_to_occupation.csv'))
        for r in eo_rows:
            if len(r) > 1:
                edu_id, occ_id = r[0], r[1]
                if occ_id not in self.occ_to_edu: self.occ_to_edu[occ_id] = []
                self.occ_to_edu[occ_id].append(edu_id)
        
        self._initialized = True
        
    def get_pathway(self, occupation_id: str) -> Dict[str, Any]:
        self.initialize()
        
        edu_ids = self.occ_to_edu.get(occupation_id, [])
        options = []
        for eid in edu_ids:
            if eid in self.edu_pathways:
                options.append(self.edu_pathways[eid])
                
        if not options:
            return {
                "status": "UNAVAILABLE",
                "reason": f"No canonical education pathway found for occupation {occupation_id}"
            }
            
        return {
            "status": "AVAILABLE",
            "occupation_id": occupation_id,
            "education_options": options
        }

def analyze_pathway(occupation_id: str) -> Dict[str, Any]:
    return PathwayEngine.get_instance().get_pathway(occupation_id)