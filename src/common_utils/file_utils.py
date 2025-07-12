# This code is proprietary to AquaTrak. Unauthorized use is strictly prohibited.

"""
File utility functions for AquaTrak
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import uuid
from datetime import datetime

# Optional imports for GIS functionality
try:
    import rasterio
    from rasterio.transform import from_bounds
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from fastapi import UploadFile

from .exceptions import FileError

def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)

def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as JSON file"""
    try:
        ensure_directory(str(filepath.parent))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise FileError(f"Failed to save JSON file {filepath}: {str(e)}")

def load_json(filepath: Path) -> Dict[str, Any]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise FileError(f"Failed to load JSON file {filepath}: {str(e)}")

def save_geotiff(data, filepath: Path, metadata: Dict) -> None:
    """Save data as GeoTIFF file"""
    if not (RASTERIO_AVAILABLE and NUMPY_AVAILABLE):
        raise FileError("GeoTIFF functionality requires rasterio and numpy to be installed.")
    try:
        ensure_directory(str(filepath.parent))
        with rasterio.open(
            filepath,
            'w',
            driver='GTiff',
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs=metadata.get('crs'),
            transform=metadata.get('transform')
        ) as dst:
            dst.write(data, 1)
    except Exception as e:
        raise FileError(f"Failed to save GeoTIFF file {filepath}: {str(e)}")

def load_geotiff(filepath: Path):
    """Load data from GeoTIFF file"""
    if not (RASTERIO_AVAILABLE and NUMPY_AVAILABLE):
        raise FileError("GeoTIFF functionality requires rasterio and numpy to be installed.")
    try:
        with rasterio.open(filepath) as src:
            data = src.read(1)
            metadata = {
                'crs': src.crs,
                'transform': src.transform,
                'width': src.width,
                'height': src.height,
                'bounds': src.bounds
            }
            return data, metadata
    except Exception as e:
        raise FileError(f"Failed to load GeoTIFF file {filepath}: {str(e)}")

async def save_uploaded_file(upload_file: UploadFile, subdirectory: str = "") -> str:
    """Save uploaded file and return file path"""
    try:
        # Create upload directory
        upload_dir = Path("uploads") / subdirectory
        ensure_directory(str(upload_dir))
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = Path(upload_file.filename).suffix
        filename = f"{timestamp}_{unique_id}{extension}"
        
        filepath = upload_dir / filename
        
        # Save file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return str(filepath)
        
    except Exception as e:
        raise FileError(f"Failed to save uploaded file: {str(e)}")

def get_file_size(filepath: Path) -> int:
    """Get file size in bytes"""
    try:
        return filepath.stat().st_size
    except Exception as e:
        raise FileError(f"Failed to get file size for {filepath}: {str(e)}")

def get_file_extension(filepath: Path) -> str:
    """Get file extension"""
    return filepath.suffix.lower()

def is_valid_file_type(filepath: Path, allowed_extensions: list) -> bool:
    """Check if file type is allowed"""
    return get_file_extension(filepath) in allowed_extensions

def cleanup_temp_files(temp_dir: Path, max_age_hours: int = 24) -> None:
    """Clean up temporary files older than specified age"""
    try:
        current_time = datetime.now()
        for filepath in temp_dir.rglob("*"):
            if filepath.is_file():
                file_age = current_time - datetime.fromtimestamp(filepath.stat().st_mtime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    filepath.unlink()
    except Exception as e:
        raise FileError(f"Failed to cleanup temp files: {str(e)}")

def create_temp_directory(prefix: str = "aquatrak_") -> Path:
    """Create temporary directory"""
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        return temp_dir
    except Exception as e:
        raise FileError(f"Failed to create temp directory: {str(e)}")

def copy_file_with_metadata(src: Path, dst: Path) -> None:
    """Copy file with metadata preservation"""
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        raise FileError(f"Failed to copy file from {src} to {dst}: {str(e)}")

def move_file_with_metadata(src: Path, dst: Path) -> None:
    """Move file with metadata preservation"""
    try:
        ensure_directory(str(dst.parent))
        shutil.move(str(src), str(dst))
    except Exception as e:
        raise FileError(f"Failed to move file from {src} to {dst}: {str(e)}")

def delete_file_safely(filepath: Path) -> bool:
    """Safely delete file, return True if successful"""
    try:
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    except Exception as e:
        raise FileError(f"Failed to delete file {filepath}: {str(e)}")

def get_file_hash(filepath: Path, algorithm: str = "md5") -> str:
    """Calculate file hash"""
    import hashlib
    
    try:
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        raise FileError(f"Failed to calculate file hash for {filepath}: {str(e)}")

def validate_file_integrity(filepath: Path, expected_hash: str, algorithm: str = "md5") -> bool:
    """Validate file integrity using hash"""
    try:
        actual_hash = get_file_hash(filepath, algorithm)
        return actual_hash == expected_hash
    except Exception as e:
        raise FileError(f"Failed to validate file integrity for {filepath}: {str(e)}")

def create_file_backup(filepath: Path, backup_dir: Path = None) -> Path:
    """Create backup of file"""
    try:
        if backup_dir is None:
            backup_dir = filepath.parent / "backups"
        
        ensure_directory(str(backup_dir))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        backup_path = backup_dir / backup_filename
        
        copy_file_with_metadata(filepath, backup_path)
        return backup_path
        
    except Exception as e:
        raise FileError(f"Failed to create backup for {filepath}: {str(e)}")

def get_directory_size(directory: Path) -> int:
    """Calculate total size of directory in bytes"""
    try:
        total_size = 0
        for filepath in directory.rglob("*"):
            if filepath.is_file():
                total_size += filepath.stat().st_size
        return total_size
    except Exception as e:
        raise FileError(f"Failed to calculate directory size for {directory}: {str(e)}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB" 