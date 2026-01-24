"""
Utility functions for WorldHeritage.guide
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from slugify import slugify
import requests
from PIL import Image

# Handle imports for both package and direct execution
try:
    from .config import PATHS, LOGGING, IMAGE_CONFIG, DATA_QUALITY
except ImportError:
    from config import PATHS, LOGGING, IMAGE_CONFIG, DATA_QUALITY

# Setup logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    handlers=[
        logging.FileHandler(LOGGING['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# DATA QUALITY
# ============================================

def calculate_completeness_score(site_data: Dict) -> int:
    """
    Calculate data completeness score (0-100)

    Args:
        site_data: Site data dictionary

    Returns:
        Completeness score (0-100)
    """
    score = 0
    scoring = DATA_QUALITY['scoring']

    for field, points in scoring['critical_fields'].items():
        if site_data.get(field):
            score += points

    for field, points in scoring['important_fields'].items():
        if site_data.get(field):
            score += points

    for field, points in scoring['nice_to_have'].items():
        if site_data.get(field):
            score += points

    return min(score, 100)

def calculate_image_quality_score(image_meta: Dict) -> int:
    """
    Calculate image quality score (0-100)

    Args:
        image_meta: Image metadata

    Returns:
        Quality score (0-100)
    """
    score = 0

    # Resolution (30 points)
    width = image_meta.get('width', 0)
    height = image_meta.get('height', 0)

    if width >= 2048 and height >= 1536:
        score += 30
    elif width >= 1920 and height >= 1080:
        score += 25
    elif width >= 1280 and height >= 720:
        score += 20
    elif width >= 1024 and height >= 768:
        score += 15
    else:
        score += 5

    # Aspect ratio (20 points)
    if height > 0:
        aspect = width / height
        if 1.3 <= aspect <= 1.8:
            score += 20
        elif 1.2 <= aspect <= 2.0:
            score += 15
        else:
            score += 5

    # File size (15 points)
    size_mb = image_meta.get('size_bytes', 0) / 1_000_000
    if 0.5 <= size_mb <= 3:
        score += 15
    elif 0.2 <= size_mb <= 5:
        score += 10
    else:
        score += 5

    # Relevance (20 points)
    title = image_meta.get('title', '').lower()
    site_name = image_meta.get('site_name', '').lower()

    if site_name in title:
        score += 20
    elif any(word in title for word in site_name.split()):
        score += 15
    else:
        score += 5

    # License (15 points)
    license = image_meta.get('license', '')
    if license in ['CC0', 'Public Domain']:
        score += 15
    elif license.startswith('CC BY'):
        score += 12
    elif license.startswith('CC BY-SA'):
        score += 10
    else:
        score += 5

    return min(score, 100)

# ============================================
# FILE I/O
# ============================================

def save_json(data: Any, filepath: Path, pretty: bool = True) -> None:
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2 if pretty else None)
    logger.info(f"Saved JSON: {filepath}")

def load_json(filepath: Path) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================
# SLUG GENERATION
# ============================================

def generate_slug(name: str) -> str:
    """
    Generate URL-friendly slug

    Example:
        "Neuschwanstein Castle" -> "neuschwanstein-castle"
    """
    return slugify(name, max_length=100)

# ============================================
# IMAGE UTILITIES
# ============================================

def download_image(url: str, save_path: Path) -> bool:
    """Download image from URL"""
    # Required headers for Wikimedia
    headers = {
        'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide; contact@worldheritage.guide) Python/requests',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Downloaded: {save_path.name}")
        return True

    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def optimize_image(input_path: Path, output_path: Path,
                   width: int = None, quality: int = 85) -> bool:
    """Optimize and convert image to WebP"""
    try:
        img = Image.open(input_path)

        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        if width and img.width > width:
            ratio = width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((width, new_height), Image.Resampling.LANCZOS)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, 'WebP', quality=quality, method=6)

        logger.info(f"Optimized: {output_path.name}")
        return True

    except Exception as e:
        logger.error(f"Failed to optimize {input_path}: {e}")
        return False

def get_image_metadata(filepath: Path) -> Dict:
    """Get image dimensions and size"""
    try:
        img = Image.open(filepath)
        return {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'size_bytes': filepath.stat().st_size,
        }
    except Exception as e:
        logger.error(f"Failed to get metadata for {filepath}: {e}")
        return {}

# ============================================
# VALIDATION
# ============================================

def validate_coordinates(coords: Any) -> bool:
    """Validate latitude/longitude"""
    if not coords or not isinstance(coords, (list, tuple)):
        return False
    if len(coords) != 2:
        return False
    lat, lng = coords
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return False
    return True

# ============================================
# LOGGING HELPERS
# ============================================

def log_progress(current: int, total: int, prefix: str = '') -> None:
    """Log progress with percentage"""
    percent = (current / total) * 100
    logger.info(f"{prefix} Progress: {current}/{total} ({percent:.1f}%)")
