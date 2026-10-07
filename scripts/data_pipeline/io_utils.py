"""
GoGuide PRISM Engine - Data Pipeline File I/O Utilities
"""

import os
import csv
import json
import hashlib

try:
    from .config import DATA_DIR, RAW_DIR, PROCESSED_DIR
except ImportError:
    from config import DATA_DIR, RAW_DIR, PROCESSED_DIR

csv.field_size_limit(10_000_000)

def compute_file_hashes(filepath):
    """Compute SHA256 and MD5 hashes for a given file."""
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            md5.update(chunk)
            
    return {
        'sha256': sha256.hexdigest(),
        'md5': md5.hexdigest()
    }

def inspect_file_metadata(filepath, rel_path=None):
    """Inspect file dimensions, format, row/column counts, and header schema."""
    if rel_path is None:
        rel_path = os.path.relpath(filepath, DATA_DIR)
        
    size_bytes = os.path.getsize(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    hashes = compute_file_hashes(filepath)
    
    metadata = {
        'relative_path': rel_path.replace('\\', '/'),
        'filename': os.path.basename(filepath),
        'extension': ext,
        'size_bytes': size_bytes,
        'size_mb': round(size_bytes / (1024 * 1024), 2),
        'sha256': hashes['sha256'],
        'md5': hashes['md5'],
        'rows': 0,
        'cols': 0,
        'header': []
    }
    
    if ext == '.csv':
        with open(filepath, 'r', encoding='utf-8', errors='replace') as infile:
            reader = csv.reader(infile)
            try:
                header = next(reader)
                metadata['header'] = header
                metadata['cols'] = len(header)
                row_count = sum(1 for _ in reader)
                metadata['rows'] = row_count
            except StopIteration:
                metadata['header'] = []
                metadata['cols'] = 0
                metadata['rows'] = 0
    elif ext == '.json':
        with open(filepath, 'r', encoding='utf-8', errors='replace') as infile:
            try:
                data = json.load(infile)
                if isinstance(data, list):
                    metadata['rows'] = len(data)
                    if len(data) > 0 and isinstance(data[0], dict):
                        metadata['header'] = list(data[0].keys())
                        metadata['cols'] = len(metadata['header'])
                elif isinstance(data, dict):
                    metadata['rows'] = len(data)
                    metadata['header'] = list(data.keys())
                    metadata['cols'] = len(metadata['header'])
            except Exception:
                pass
                
    return metadata

def load_csv_rows(filepath):
    """Load all rows from a CSV file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [row for row in reader]
    return header, rows

def write_csv_rows(filepath, header, rows):
    """Write rows to a CSV file safely."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(rows)
