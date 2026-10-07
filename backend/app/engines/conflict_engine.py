def preference_alignment(student_vector: list, parent_vector: list) -> float:
    if len(student_vector) != len(parent_vector) or len(student_vector) == 0:
        return 0.0
    
    dot_product = sum(s * p for s, p in zip(student_vector, parent_vector))
    mag_s = sum(s * s for s in student_vector) ** 0.5
    mag_p = sum(p * p for p in parent_vector) ** 0.5
    
    if mag_s == 0 or mag_p == 0:
        return 0.0
        
    cos_sim = dot_product / (mag_s * mag_p)
    return 1 - cos_sim
