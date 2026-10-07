"""
GoGuide PRISM Engine - Phase 2 Structural & PII Cleaning Script
"""

import os
import sys
import json
import csv
import re
from datetime import datetime

# Set path for pipeline imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import BASE_DIR, DATA_DIR, RAW_DIR, PROCESSED_DIR, REPORTS_DIR, DOMAINS, PLACEHOLDER_NULLS, PII_COLUMNS_TO_STRIP
from io_utils import compute_file_hashes, inspect_file_metadata, load_csv_rows, write_csv_rows
from audit_utils import verify_raw_layer_integrity

csv.field_size_limit(10_000_000)

PHASE2_JSON_REPORT = os.path.join(REPORTS_DIR, 'phase_2_structural_cleaning.json')
CLEANING_LOG_MD = os.path.join(REPORTS_DIR, 'CLEANING_LOG.md')

def clean_header_field(h):
    """Normalize header string, fixing whitespace and known tab anomalies."""
    if not h:
        return ""
    cleaned = h.strip()
    cleaned = re.sub(r'[\t\r\n]', '', cleaned)
    return cleaned

def clean_cell_value(val):
    """Trim string cell value and convert placeholder null strings to empty string (NULL in CSV)."""
    if val is None:
        return ""
    val_str = str(val).strip()
    if val_str.lower() in PLACEHOLDER_NULLS:
        return ""
    return val_str

def is_row_completely_empty(row):
    """Check if all cells in a row are empty/null."""
    return all(cell is None or str(cell).strip() == "" or str(cell).strip().lower() in PLACEHOLDER_NULLS for cell in row)

def run_phase_2_cleaning():
    print("Starting Phase 2 — Structural Cleaning & PII Cleaning...")
    
    provenance_records = []
    pii_findings = []
    
    total_files_processed = 0
    total_rows_before = 0
    total_rows_after = 0
    total_rows_removed = 0
    total_cols_removed = 0
    
    # Iterate through all domain directories in data/raw/
    for domain in DOMAINS:
        raw_domain_dir = os.path.join(RAW_DIR, domain)
        proc_domain_dir = os.path.join(PROCESSED_DIR, domain)
        
        if not os.path.exists(raw_domain_dir):
            continue
            
        for root_path, dirs, files in os.walk(raw_domain_dir):
            rel_sub = os.path.relpath(root_path, raw_domain_dir)
            target_sub_dir = proc_domain_dir if rel_sub == '.' else os.path.join(proc_domain_dir, rel_sub)
            os.makedirs(target_sub_dir, exist_ok=True)
            
            for f in sorted(files):
                if f == 'README.md':
                    # Copy README without modification
                    shutil_src = os.path.join(root_path, f)
                    shutil_tgt = os.path.join(target_sub_dir, f)
                    if not os.path.exists(shutil_tgt):
                        with open(shutil_src, 'r', encoding='utf-8', errors='replace') as r_in:
                            with open(shutil_tgt, 'w', encoding='utf-8') as r_out:
                                r_out.write(r_in.read())
                    continue
                    
                raw_filepath = os.path.join(root_path, f)
                proc_filepath = os.path.join(target_sub_dir, f)
                ext = os.path.splitext(f)[1].lower()
                
                rel_raw_path = os.path.relpath(raw_filepath, BASE_DIR).replace('\\', '/')
                rel_proc_path = os.path.relpath(proc_filepath, BASE_DIR).replace('\\', '/')
                
                transformations = []
                cols_removed = []
                cols_renamed = []
                
                if ext == '.csv':
                    total_files_processed += 1
                    header, raw_rows = load_csv_rows(raw_filepath)
                    rows_before = len(raw_rows)
                    total_rows_before += rows_before
                    
                    # 1. Header structural cleaning
                    cleaned_header = []
                    for col in header:
                        norm_col = clean_header_field(col)
                        if norm_col != col:
                            cols_renamed.append(f"'{col}' -> '{norm_col}'")
                            transformations.append(f"Fixed header anomaly/whitespace: '{col}' -> '{norm_col}'")
                        cleaned_header.append(norm_col)
                    
                    # 2. PII Cleaning for prism_resume_intelligence/01_people.csv
                    keep_indices = list(range(len(cleaned_header)))
                    if domain == 'prism_resume_intelligence' and f == '01_people.csv':
                        pii_indices = []
                        new_header = []
                        new_keep_indices = []
                        
                        for idx, col in enumerate(cleaned_header):
                            if col.lower() in PII_COLUMNS_TO_STRIP:
                                cols_removed.append(col)
                                pii_indices.append(idx)
                                pii_findings.append({
                                    'file': rel_proc_path,
                                    'column': col,
                                    'action': 'REMOVED_PII_FIELD'
                                })
                            else:
                                new_header.append(col)
                                new_keep_indices.append(idx)
                                
                        cleaned_header = new_header
                        keep_indices = new_keep_indices
                        total_cols_removed += len(cols_removed)
                        transformations.append(f"Stripped PII contact columns: {cols_removed}")
                    
                    # 3. Row cleaning (value trimming, null placeholder conversion, empty row dropping)
                    cleaned_rows = []
                    empty_rows_dropped = 0
                    
                    for row in raw_rows:
                        if is_row_completely_empty(row):
                            empty_rows_dropped += 1
                            continue
                            
                        cleaned_row = []
                        for idx in keep_indices:
                            cell_val = row[idx] if idx < len(row) else ""
                            c_val = clean_cell_value(cell_val)
                            cleaned_row.append(c_val)
                            
                        cleaned_rows.append(cleaned_row)
                        
                    rows_after = len(cleaned_rows)
                    rows_removed = empty_rows_dropped
                    total_rows_after += rows_after
                    total_rows_removed += rows_removed
                    
                    if empty_rows_dropped > 0:
                        transformations.append(f"Dropped {empty_rows_dropped} completely empty rows")
                        
                    transformations.append("Trimmed cell whitespace & normalized placeholder nulls to empty string")
                    
                    # Write cleaned CSV to processed layer
                    write_csv_rows(proc_filepath, cleaned_header, cleaned_rows)
                    
                    provenance_records.append({
                        'raw_source': rel_raw_path,
                        'processed_output': rel_proc_path,
                        'rows_before': rows_before,
                        'rows_after': rows_after,
                        'rows_removed': rows_removed,
                        'cols_before': len(header),
                        'cols_after': len(cleaned_header),
                        'cols_removed': cols_removed,
                        'cols_renamed': cols_renamed,
                        'transformations': transformations,
                        'timestamp': datetime.now().isoformat(),
                        'script': 'scripts/data_pipeline/execute_phase2_cleaning.py'
                    })
                    
                elif ext == '.json':
                    total_files_processed += 1
                    with open(raw_filepath, 'r', encoding='utf-8', errors='replace') as json_in:
                        json_data = json.load(json_in)
                    
                    rows_before = len(json_data) if isinstance(json_data, list) else 1
                    total_rows_before += rows_before
                    
                    # For JSON, write structured copy to processed
                    os.makedirs(os.path.dirname(proc_filepath), exist_ok=True)
                    with open(proc_filepath, 'w', encoding='utf-8') as json_out:
                        json.dump(json_data, json_out, indent=2)
                        
                    rows_after = rows_before
                    total_rows_after += rows_after
                    
                    provenance_records.append({
                        'raw_source': rel_raw_path,
                        'processed_output': rel_proc_path,
                        'rows_before': rows_before,
                        'rows_after': rows_after,
                        'rows_removed': 0,
                        'cols_before': len(json_data[0].keys()) if isinstance(json_data, list) and len(json_data) > 0 else 0,
                        'cols_after': len(json_data[0].keys()) if isinstance(json_data, list) and len(json_data) > 0 else 0,
                        'cols_removed': [],
                        'cols_renamed': [],
                        'transformations': ["Copied JSON dataset structure into processed layer"],
                        'timestamp': datetime.now().isoformat(),
                        'script': 'scripts/data_pipeline/execute_phase2_cleaning.py'
                    })

    # Output machine-readable JSON report
    report_data = {
        'phase': 'Phase 2 — Structural & PII Cleaning',
        'generated_at': datetime.now().isoformat(),
        'total_files_processed': total_files_processed,
        'total_rows_before': total_rows_before,
        'total_rows_after': total_rows_after,
        'total_rows_removed': total_rows_removed,
        'total_cols_removed': total_cols_removed,
        'pii_findings': pii_findings,
        'provenance_records': provenance_records
    }
    
    with open(PHASE2_JSON_REPORT, 'w', encoding='utf-8') as rf:
        json.dump(report_data, rf, indent=2)
        
    print(f"Phase 2 JSON report written to {os.path.relpath(PHASE2_JSON_REPORT, BASE_DIR)}")
    
    # Update CLEANING_LOG.md
    log_lines = [
        "# GoGuide PRISM Data Cleaning Log",
        f"\n**Project:** PRISM Engine (GoGuide / DataQuest 3.0)",
        f"**Pipeline Script:** `scripts/data_pipeline/execute_phase2_cleaning.py`",
        f"**Phase 2 Completion Timestamp:** {datetime.now().isoformat()}",
        f"**Status:** Phase 2 (Structural & PII Cleaning) Successfully Executed\n",
        "---",
        "## Summary Metrics",
        f"- **Files Processed:** {total_files_processed}",
        f"- **Total Rows Before:** {total_rows_before:,}",
        f"- **Total Rows After:** {total_rows_after:,}",
        f"- **Total Empty Rows Removed:** {total_rows_removed}",
        f"- **PII Contact Columns Stripped:** 4 (`name`, `email`, `phone`, `linkedin` in `01_people.csv`)\n",
        "---",
        "## Detailed File Provenance Log",
        "\n| Source Raw File | Processed Output | Rows Before | Rows After | Rows Removed | Cols Removed | Header Fixes | Transformations |",
        "|---|---|---|---|---|---|---|---|"
    ]
    
    for pr in provenance_records:
        r_src = pr['raw_source']
        r_out = pr['processed_output']
        r_bef = f"{pr['rows_before']:,}"
        r_aft = f"{pr['rows_after']:,}"
        r_rem = pr['rows_removed']
        c_rem = ", ".join(pr['cols_removed']) if pr['cols_removed'] else "None"
        c_ren = ", ".join(pr['cols_renamed']) if pr['cols_renamed'] else "None"
        trans = "; ".join(pr['transformations'])
        
        log_lines.append(f"| `{r_src}` | `{r_out}` | {r_bef} | {r_aft} | {r_rem} | {c_rem} | {c_ren} | {trans} |")
        
    with open(CLEANING_LOG_MD, 'w', encoding='utf-8') as lf:
        lf.write("\n".join(log_lines))
        
    print(f"Updated CLEANING_LOG.md at {os.path.relpath(CLEANING_LOG_MD, BASE_DIR)}")
    return report_data

if __name__ == '__main__':
    run_phase_2_cleaning()
