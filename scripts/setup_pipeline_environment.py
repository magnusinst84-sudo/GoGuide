import os
import shutil
import hashlib
import json
import csv

ROOT = r'C:\Users\TANMAY\Desktop\PROJECT\DataQuest'
DATA_DIR = os.path.join(ROOT, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
CROSSWALKS_DIR = os.path.join(DATA_DIR, 'crosswalks')
DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
PIPELINE_DIR = os.path.join(ROOT, 'scripts', 'data_pipeline')

DOMAINS = [
    'prism_education_career',
    'prism_student_profile',
    'prism_india_jobs',
    'prism_occupation_intelligence',
    'prism_esco',
    'prism_resume_intelligence',
    'prism_job_descriptions'
]

csv.field_size_limit(10_000_000)

print("Starting pipeline directory & environment setup...")

# 1. Create directory structure
dirs_to_create = [
    RAW_DIR,
    PROCESSED_DIR,
    CROSSWALKS_DIR,
    DICTIONARIES_DIR,
    REPORTS_DIR,
    PIPELINE_DIR
]

for d in DOMAINS:
    dirs_to_create.append(os.path.join(RAW_DIR, d))
    dirs_to_create.append(os.path.join(PROCESSED_DIR, d))

for dpath in dirs_to_create:
    os.makedirs(dpath, exist_ok=True)
    print(f"Directory ready: {os.path.relpath(dpath, ROOT)}")

# 2. Safely populate data/raw/ by copying existing domain directories if not already present
for d in DOMAINS:
    src_domain_dir = os.path.join(DATA_DIR, d)
    tgt_domain_dir = os.path.join(RAW_DIR, d)
    
    if os.path.exists(src_domain_dir):
        for root_path, dirs, files in os.walk(src_domain_dir):
            rel_sub = os.path.relpath(root_path, src_domain_dir)
            target_sub = tgt_domain_dir if rel_sub == '.' else os.path.join(tgt_domain_dir, rel_sub)
            os.makedirs(target_sub, exist_ok=True)
            
            for f in files:
                src_file = os.path.join(root_path, f)
                tgt_file = os.path.join(target_sub, f)
                if not os.path.exists(tgt_file):
                    shutil.copy2(src_file, tgt_file)

print("Populated data/raw/ safely.")
