"""
GoGuide PRISM Engine - Audit & Verification Utilities
"""

import os
import json

try:
    from .io_utils import compute_file_hashes, inspect_file_metadata
    from .config import RAW_MANIFEST_JSON
except ImportError:
    from io_utils import compute_file_hashes, inspect_file_metadata
    from config import RAW_MANIFEST_JSON

def verify_raw_layer_integrity(manifest_filepath=RAW_MANIFEST_JSON):
    """
    Verify that all raw source files remain byte-for-byte unchanged by comparing
    current file SHA256 and MD5 hashes against the recorded raw manifest.
    """
    if not os.path.exists(manifest_filepath):
        return {
            'success': False,
            'message': f"Manifest file not found at {manifest_filepath}",
            'verified_files': 0,
            'altered_files': []
        }
        
    with open(manifest_filepath, 'r', encoding='utf-8') as f:
        manifest_data = json.load(f)
        
    verified_count = 0
    altered_files = []
    
    for file_record in manifest_data.get('files', []):
        abs_path = os.path.abspath(file_record['absolute_path'])
        
        if not os.path.exists(abs_path):
            altered_files.append({
                'filepath': file_record['relative_path'],
                'reason': 'File Missing'
            })
            continue
            
        curr_hashes = compute_file_hashes(abs_path)
        
        if curr_hashes['sha256'] != file_record['sha256'] or curr_hashes['md5'] != file_record['md5']:
            altered_files.append({
                'filepath': file_record['relative_path'],
                'expected_sha256': file_record['sha256'],
                'actual_sha256': curr_hashes['sha256'],
                'reason': 'Hash Mismatch (File Altered)'
            })
        else:
            verified_count += 1
            
    success = len(altered_files) == 0
    return {
        'success': success,
        'message': "100% Raw Layer Integrity Verified. Zero raw files modified." if success else f"FAILURE: {len(altered_files)} files modified.",
        'verified_files': verified_count,
        'altered_files': altered_files
    }
