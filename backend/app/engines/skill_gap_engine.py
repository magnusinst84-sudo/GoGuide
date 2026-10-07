import os
import csv
from typing import Dict, Any, List
from app.data.repositories.skill_repository import SkillRepository

# Conservative explicit mapping from 8 UI dimensions to canonical skills
# UI skills: mathematics, statistics, programming, logic, communication, design, biology, electronics
UI_TO_CANONICAL = {
    'mathematics': ['mathematics', 'algebra', 'calculus', 'quantitative'],
    'statistics': ['statistics', 'data analysis', 'statistical reasoning', 'probability'],
    'programming': ['programming', 'software', 'coding', 'python', 'java', 'c++', 'software development'],
    'logic': ['logical', 'analytical', 'problem solving', 'critical thinking'],
    'communication': ['communication', 'writing', 'presentation', 'verbal', 'interpersonal'],
    'design': ['design', 'ux', 'visual design', 'graphic design', 'ui design'],
    'biology': ['biology', 'life science', 'biological', 'anatomy'],
    'electronics': ['electronics', 'electrical', 'hardware', 'circuit']
}

def analyze_skill_gap(profile: Dict[str, Any], occupation_id: str) -> Dict[str, Any]:
    repo = SkillRepository()
    req_skills = repo.get_required_skills(occupation_id)
    
    student_skills = profile.get('skills', {})
    if hasattr(student_skills, 'model_dump'):
        student_skills = student_skills.model_dump()
        
    strengths = []
    gaps = []
    unassessed = []
    
    matched_req_skills = 0
    total_req_skills = len(req_skills)

    for rs in req_skills:
        rs_lower = rs.skill_name.lower()
        
        # Check if this canonical skill maps to any UI skill
        mapped_ui_skill = None
        for ui_sk, canon_keywords in UI_TO_CANONICAL.items():
            if any(k in rs_lower for k in canon_keywords):
                mapped_ui_skill = ui_sk
                break
                
        if mapped_ui_skill:
            # We have a rating from 0-100
            rating = student_skills.get(mapped_ui_skill, 0.0)
            if rating >= 75:
                strengths.append({"skill_name": rs.skill_name, "student_rating": rating, "assessment": "strong"})
                matched_req_skills += 1
            elif rating >= 50:
                strengths.append({"skill_name": rs.skill_name, "student_rating": rating, "assessment": "adequate"})
                matched_req_skills += 0.5
            else:
                gaps.append({"skill_name": rs.skill_name, "student_rating": rating, "assessment": "gap", "reason": f"{mapped_ui_skill} rating is low ({rating})"})
        else:
            # Cannot be safely mapped
            unassessed.append(rs.skill_name)
            
    coverage_score = (matched_req_skills / total_req_skills) if total_req_skills > 0 else 0.0
    
    return {
        "occupation_id": occupation_id,
        "strengths": strengths,
        "gaps": gaps,
        "unassessed_skills": unassessed,
        "coverage_score": coverage_score,
        "total_required_skills": total_req_skills
    }