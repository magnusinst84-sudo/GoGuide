"""
GoGuide PRISM Engine - Data Cleaning & Integration Pipeline Configuration
"""

import os

# Base Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
CROSSWALKS_DIR = os.path.join(DATA_DIR, 'crosswalks')
DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

# Key Pipeline Artifacts
RAW_MANIFEST_JSON = os.path.join(REPORTS_DIR, 'RAW_MANIFEST.json')
RAW_MANIFEST_MD = os.path.join(REPORTS_DIR, 'RAW_MANIFEST.md')
CLEANING_LOG_MD = os.path.join(REPORTS_DIR, 'CLEANING_LOG.md')

# Domain List
DOMAINS = [
    'prism_education_career',
    'prism_student_profile',
    'prism_india_jobs',
    'prism_occupation_intelligence',
    'prism_esco',
    'prism_resume_intelligence',
    'prism_job_descriptions'
]

# Standard Placeholder Null Strings
PLACEHOLDER_NULLS = {
    'n/a', 'na', 'null', 'none', '-', 'unknown', 'not available',
    'n.a.', 'n/a.', 'nil', 'nan', ''
}

# High-Risk PII Fields to Strip
PII_COLUMNS_TO_STRIP = {'name', 'email', 'phone', 'linkedin'}

# Hash Algorithm for Manifests
HASH_ALGORITHMS = ['sha256', 'md5']
