#!/usr/bin/env python3
"""
Encoding Fix Script for AquaTrak Project
Re-encodes all text files as UTF-8 without BOM to resolve CI encoding issues.
"""

import os
import sys
import codecs
from pathlib import Path

# File extensions to process
EXTENSIONS = ('.py', '.json', '.txt', '.ini', '.md', '.csv', '.yml', '.yaml', '.toml', '.cfg')

# Directories to skip
SKIP_DIRS = {
    '__pycache__', '.git', 'node_modules', '.venv', 'venv', 'env', 
    '.pytest_cache', '.mypy_cache', '.coverage', 'dist', 'build'
}

def is_text_file(filename):
    """Check if file should be processed based on extension."""
    return filename.lower().endswith(EXTENSIONS)

def should_skip_directory(dirname):
    """Check if directory should be skipped."""
    return dirname in SKIP_DIRS

def fix_file_encoding(filepath):
    """Fix encoding of a single file."""
    try:
        # Read file as bytes
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        # Check for BOM
        has_bom = False
        if raw.startswith(codecs.BOM_UTF8):
            raw = raw[len(codecs.BOM_UTF8):]
            has_bom = True
            print(f"  - Removed UTF-8 BOM from: {filepath}")
        elif raw.startswith(codecs.BOM_UTF16_LE):
            raw = raw[len(codecs.BOM_UTF16_LE):]
            has_bom = True
            print(f"  - Removed UTF-16 LE BOM from: {filepath}")
        elif raw.startswith(codecs.BOM_UTF16_BE):
            raw = raw[len(codecs.BOM_UTF16_BE):]
            has_bom = True
            print(f"  - Removed UTF-16 BE BOM from: {filepath}")
        
        # Check for 0xFF byte at position 0 (common cause of UnicodeDecodeError)
        if raw and raw[0] == 0xFF:
            print(f"  - Found 0xFF byte at position 0 in: {filepath}")
            has_bom = True
        
        # Try to decode the content
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            # Try alternative encodings
            for encoding in ['utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']:
                try:
                    text = raw.decode(encoding)
                    print(f"  - Decoded with {encoding}: {filepath}")
                    has_bom = True
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"  - FAILED to decode: {filepath}")
                return False
        
        # Write back as UTF-8 (no BOM)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        
        return has_bom
        
    except Exception as e:
        print(f"  - Error processing {filepath}: {e}")
        return False

def main():
    """Main function to process all files."""
    print("🔧 AquaTrak Encoding Fix Script")
    print("=" * 50)
    
    # Get project root (script directory)
    root = Path(__file__).parent.absolute()
    print(f"Processing files in: {root}")
    
    fixed_files = []
    total_files = 0
    
    # Walk through all directories
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip unwanted directories
        dirnames[:] = [d for d in dirnames if not should_skip_directory(d)]
        
        for filename in filenames:
            if is_text_file(filename):
                filepath = Path(dirpath) / filename
                total_files += 1
                
                print(f"Processing: {filepath.relative_to(root)}")
                
                if fix_file_encoding(filepath):
                    fixed_files.append(str(filepath.relative_to(root)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ENCODING FIX SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {total_files}")
    print(f"Files with encoding issues fixed: {len(fixed_files)}")
    
    if fixed_files:
        print("\nFixed files:")
        for file in fixed_files:
            print(f"  ✓ {file}")
        print(f"\n✅ Successfully fixed {len(fixed_files)} files with encoding issues.")
        print("💡 Please commit and push these changes to resolve CI encoding errors.")
    else:
        print("\n✅ No encoding issues found in text files.")
        print("💡 The UnicodeDecodeError might be caused by:")
        print("   - A file not detected by this script")
        print("   - A file being read in binary mode in CI")
        print("   - A file with mixed encodings")
    
    return len(fixed_files)

if __name__ == '__main__':
    try:
        fixed_count = main()
        sys.exit(0 if fixed_count == 0 else 1)
    except KeyboardInterrupt:
        print("\n❌ Script interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Script failed with error: {e}")
        sys.exit(1) 