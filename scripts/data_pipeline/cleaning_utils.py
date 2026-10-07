"""
GoGuide PRISM Engine - Data Cleaning & Normalization Utilities Framework
"""

import re
try:
    from .config import PLACEHOLDER_NULLS, PII_COLUMNS_TO_STRIP
except ImportError:
    from config import PLACEHOLDER_NULLS, PII_COLUMNS_TO_STRIP

def clean_header_field(field_name):
    """Strip whitespace, tabs, and non-printable characters from column header."""
    if field_name is None:
        return ""
    cleaned = field_name.strip()
    cleaned = re.sub(r'[\t\r\n]', '', cleaned)
    return cleaned

def clean_value(val):
    """Standardize string value, converting placeholder strings to NULL."""
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in PLACEHOLDER_NULLS:
        return None
    return val_str

def filter_pii_columns(header):
    """Return filtered header list with high-risk PII fields removed, along with indices to keep."""
    keep_indices = []
    cleaned_header = []
    
    for idx, col in enumerate(header):
        norm_col = col.strip().lower()
        if norm_col not in PII_COLUMNS_TO_STRIP:
            keep_indices.append(idx)
            cleaned_header.append(col)
            
    return cleaned_header, keep_indices

def normalize_skill_string(skill_text):
    """Clean and standardize skill strings."""
    if not skill_text:
        return []
    cleaned = skill_text.strip()
    parts = re.split(r'[,;/|]', cleaned)
    results = [p.strip() for p in parts if p.strip()]
    return results

def normalize_degree_name(degree_raw):
    """Normalize degree and qualification names to canonical format."""
    if not degree_raw:
        return None
    val = degree_raw.strip()
    lower_val = val.lower()
    
    if lower_val in {'b.tech', 'btech', 'b.e.', 'be', 'bachelor of technology', 'bachelor of engineering'}:
        return 'B.Tech (Bachelor of Technology)'
    elif lower_val in {'m.tech', 'mtech', 'm.e.', 'me', 'master of technology', 'master of engineering'}:
        return 'M.Tech (Master of Technology)'
    elif lower_val in {'mba', 'master of business administration'}:
        return 'MBA (Master of Business Administration)'
    elif lower_val in {'b.sc', 'bsc', 'bachelor of science'}:
        return 'B.Sc (Bachelor of Science)'
        
    return val
