"""
Script 2: Fetch and Optimize Images
Downloads images from Wikimedia Commons and optimizes them
"""

import os
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import requests
from tqdm import tqdm
from PIL import Image

# Handle imports for both package and direct execution
try:
    from .config import (
        PROJECT, PATHS, IMAGE_CONFIG, API_KEYS, DATA_QUALITY
    )
    from .utils import (
        load_json, save_json, generate_slug,
        calculate_image_quality_score, download_image,
        optimize_image, get_image_metadata, logger
    )
except ImportError:
    from config import (
        PROJECT, PATHS, IMAGE_CONFIG, API_KEYS, DATA_QUALITY
    )
    from utils import (
        load_json, save_json, generate_slug,
        calculate_image_quality_score, download_image,
        optimize_image, get_image_metadata, logger
    )

# ============================================
# WIKIMEDIA COMMONS API
# ============================================

def search_wikimedia_images(site_name: str, limit: int = 20) -> List[Dict]:
    """
    Search Wikimedia Commons for images of a site

    Args:
        site_name: Name of the heritage site
        limit: Max images to retrieve

    Returns:
        List of image dictionaries
    """

    # Wikimedia Commons API endpoint
    API_URL = "https://commons.wikimedia.org/w/api.php"

    # Required headers for Wikimedia
    headers = {
        'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide; contact@worldheritage.guide) Python/requests',
        'Accept': 'application/json',
    }

    # Search query
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': f'"{site_name}"',
        'gsrlimit': limit,
        'gsrnamespace': 6,  # File namespace
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime|extmetadata',
        'iiurlwidth': 2048,
    }

    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'query' not in data or 'pages' not in data['query']:
            return []

        images = []
        for page_id, page in data['query']['pages'].items():
            if 'imageinfo' not in page:
                continue

            info = page['imageinfo'][0]

            # Extract metadata
            metadata = info.get('extmetadata', {})

            image = {
                'title': page.get('title', '').replace('File:', ''),
                'url': info.get('url'),
                'width': info.get('width', 0),
                'height': info.get('height', 0),
                'size_bytes': info.get('size', 0),
                'mime': info.get('mime', ''),
                'license': metadata.get('LicenseShortName', {}).get('value', 'Unknown'),
                'photographer': metadata.get('Artist', {}).get('value', 'Unknown'),
                'description': metadata.get('ImageDescription', {}).get('value', ''),
            }

            images.append(image)

        return images

    except Exception as e:
        logger.error(f"Wikimedia search failed for '{site_name}': {e}")
        return []

def get_wikidata_image(wikidata_image_url: str) -> Optional[Dict]:
    """
    Get image info from Wikidata image URL

    Args:
        wikidata_image_url: Direct Wikimedia image URL

    Returns:
        Image dictionary or None
    """

    if not wikidata_image_url:
        return None

    # Required headers for Wikimedia
    headers = {
        'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide; contact@worldheritage.guide) Python/requests',
    }

    try:
        # Get image dimensions
        response = requests.head(wikidata_image_url, headers=headers, timeout=10)
        size_bytes = int(response.headers.get('Content-Length', 0))

        # Download to get dimensions
        temp_response = requests.get(wikidata_image_url, headers=headers, timeout=30, stream=True)
        img = Image.open(temp_response.raw)

        return {
            'title': wikidata_image_url.split('/')[-1],
            'url': wikidata_image_url,
            'width': img.width,
            'height': img.height,
            'size_bytes': size_bytes,
            'mime': f"image/{img.format.lower()}",
            'license': 'Wikimedia Commons',
            'photographer': 'Wikidata',
            'description': 'Primary image from Wikidata',
        }

    except Exception as e:
        logger.error(f"Failed to get Wikidata image: {e}")
        return None

# ============================================
# SATELLITE IMAGERY FALLBACK
# ============================================

def get_mapbox_satellite(coordinates: List[float], site_slug: str) -> Optional[str]:
    """
    Get Mapbox satellite image as fallback

    Args:
        coordinates: [lat, lng]
        site_slug: Site slug for filename

    Returns:
        Path to downloaded satellite image or None
    """

    token = API_KEYS.get('mapbox')
    if not token:
        logger.warning("Mapbox token not found. Skipping satellite fallback.")
        return None

    lat, lng = coordinates
    zoom = IMAGE_CONFIG['fallback']['zoom']

    # Mapbox Static Images API
    url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lng},{lat},{zoom},0/1280x720@2x?access_token={token}"

    try:
        # Create images directory
        images_dir = PATHS['images'] / site_slug
        images_dir.mkdir(parents=True, exist_ok=True)

        # Download
        save_path = images_dir / 'satellite-original.jpg'

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded satellite image: {site_slug}")
        return str(save_path)

    except Exception as e:
        logger.error(f"Mapbox satellite failed for {site_slug}: {e}")
        return None

# ============================================
# IMAGE PROCESSING
# ============================================

def score_and_filter_images(images: List[Dict], site_name: str,
                             min_score: int = 50) -> List[Dict]:
    """
    Score images and filter by quality threshold

    Args:
        images: List of image dictionaries
        site_name: Site name for relevance scoring
        min_score: Minimum quality score

    Returns:
        Filtered and scored images, sorted by score
    """

    scored = []

    for img in images:
        # Add site name for relevance scoring
        img['site_name'] = site_name

        # Calculate score
        score = calculate_image_quality_score(img)

        if score >= min_score:
            img['quality_score'] = score
            scored.append(img)

    # Sort by score (highest first)
    scored.sort(key=lambda x: x['quality_score'], reverse=True)

    return scored

def download_and_optimize_images(images: List[Dict], site_slug: str,
                                  max_images: int = 10) -> List[Dict]:
    """
    Download and optimize images

    Args:
        images: Scored image list
        site_slug: Site slug for directory
        max_images: Maximum images to download

    Returns:
        List of processed image metadata
    """

    # Create directories
    images_dir = PATHS['images'] / site_slug
    raw_dir = images_dir / 'raw'
    optimized_dir = images_dir / 'optimized'

    raw_dir.mkdir(parents=True, exist_ok=True)
    optimized_dir.mkdir(parents=True, exist_ok=True)

    processed = []

    for i, img in enumerate(images[:max_images], 1):
        try:
            # Generate filename
            ext = img['url'].split('.')[-1].split('?')[0][:4]  # Get extension
            filename = f"{i:02d}-{hashlib.md5(img['url'].encode()).hexdigest()[:8]}"

            # Download original to raw directory
            raw_path = raw_dir / f"{filename}.{ext}"
            if download_image(img['url'], raw_path):

                # Optimize to WebP and create srcset
                srcset_images = {}

                for width in IMAGE_CONFIG['optimization']['srcset_widths']:
                    output_path = optimized_dir / f"{filename}-{width}w.webp"

                    if optimize_image(
                        raw_path,
                        output_path,
                        width=width,
                        quality=IMAGE_CONFIG['optimization']['quality']
                    ):
                        srcset_images[f'{width}w'] = str(output_path.relative_to(PATHS['images']))

                # Delete raw file after optimization to save space
                try:
                    raw_path.unlink()
                    logger.debug(f"Cleaned up raw file: {raw_path.name}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not delete raw file {raw_path}: {cleanup_error}")

                # Save metadata (without raw_path since we deleted it)
                processed.append({
                    'index': i,
                    'original_url': img['url'],
                    'title': img['title'],
                    'quality_score': img['quality_score'],
                    'license': img['license'],
                    'photographer': img.get('photographer', 'Unknown'),
                    'srcset': srcset_images,
                    'alt_text': f"{img['title']} - Heritage site",
                })

        except Exception as e:
            logger.error(f"Failed to process image {i} for {site_slug}: {e}")
            continue

    # Clean up empty raw directory
    try:
        if raw_dir.exists() and not any(raw_dir.iterdir()):
            raw_dir.rmdir()
            logger.debug(f"Removed empty raw directory for {site_slug}")
    except Exception as e:
        logger.warning(f"Could not remove raw directory: {e}")

    return processed

# ============================================
# MAIN PROCESSING
# ============================================

def process_site_images(site: Dict) -> Dict:
    """
    Process images for a single site

    Args:
        site: Site dictionary from Wikidata

    Returns:
        Image metadata dictionary
    """

    site_name = site['name']
    site_slug = generate_slug(site_name)

    logger.info(f"Processing images for: {site_name}")

    # Collect images from multiple sources
    all_images = []

    # 1. Wikidata primary image
    if site.get('wikidata_image'):
        wikidata_img = get_wikidata_image(site['wikidata_image'])
        if wikidata_img:
            all_images.append(wikidata_img)

    # 2. Search Wikimedia Commons
    commons_images = search_wikimedia_images(site_name, limit=30)
    all_images.extend(commons_images)

    # Score and filter
    min_score = DATA_QUALITY.get('image_quality_minimum', 50)
    scored_images = score_and_filter_images(all_images, site_name, min_score)

    logger.info(f"Found {len(scored_images)} quality images for {site_name}")

    # Download and optimize
    target = IMAGE_CONFIG['per_site']['target']
    processed_images = download_and_optimize_images(
        scored_images,
        site_slug,
        max_images=target
    )

    # Fallback: Satellite image if no images found
    if not processed_images and IMAGE_CONFIG['fallback']['use_satellite']:
        logger.info(f"No images found. Using satellite fallback for {site_name}")

        satellite_path = get_mapbox_satellite(site['coordinates'], site_slug)

        if satellite_path:
            # Optimize satellite image
            images_dir = PATHS['images'] / site_slug
            optimized_dir = images_dir / 'optimized'
            optimized_dir.mkdir(parents=True, exist_ok=True)

            srcset_images = {}
            for width in IMAGE_CONFIG['optimization']['srcset_widths']:
                output_path = optimized_dir / f"satellite-{width}w.webp"
                optimize_image(
                    Path(satellite_path),
                    output_path,
                    width=width,
                    quality=IMAGE_CONFIG['optimization']['quality']
                )
                srcset_images[f'{width}w'] = str(output_path.relative_to(PATHS['images']))

            # Delete original satellite file after optimization
            try:
                Path(satellite_path).unlink()
                logger.debug(f"Cleaned up original satellite file: {satellite_path}")
            except Exception as e:
                logger.warning(f"Could not delete satellite file {satellite_path}: {e}")

            processed_images.append({
                'index': 1,
                'original_url': 'Mapbox Satellite',
                'title': f"{site_name} - Satellite View",
                'quality_score': 50,
                'license': 'Mapbox',
                'photographer': 'Mapbox',
                'srcset': srcset_images,
                'alt_text': f"{site_name} - Aerial satellite view",
                'type': 'satellite',
            })

    # Save metadata
    metadata = {
        'site_name': site_name,
        'site_slug': site_slug,
        'wikidata_id': site['wikidata_id'],
        'total_images': len(processed_images),
        'images': processed_images,
        'processed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    metadata_path = PATHS['images'] / site_slug / 'metadata.json'
    save_json(metadata, metadata_path)

    return metadata

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution"""

    logger.info("="*60)
    logger.info("SCRIPT 2: FETCH AND OPTIMIZE IMAGES")
    logger.info("="*60)
    logger.info("")

    # Load sites from Phase 1
    sites_file = PATHS['raw'] / 'sites.json'

    if not sites_file.exists():
        logger.error(f"Sites file not found: {sites_file}")
        logger.error("Run Script 1 first (1_fetch_wikidata.py)")
        return

    sites = load_json(sites_file)
    logger.info(f"Loaded {len(sites)} sites")
    logger.info("")

    # Process each site
    results = []
    errors = []

    for site in tqdm(sites, desc="Processing sites"):
        try:
            metadata = process_site_images(site)
            results.append(metadata)

            # Rate limiting (be nice to Wikimedia APIs - they require delays)
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Failed to process {site['name']}: {e}")
            errors.append({
                'site': site['name'],
                'error': str(e)
            })
            # Extra delay on error to avoid rate limiting
            time.sleep(2)

    # Save summary
    summary = {
        'total_sites': len(sites),
        'successful': len(results),
        'failed': len(errors),
        'total_images': sum(r['total_images'] for r in results),
        'average_images_per_site': sum(r['total_images'] for r in results) / len(results) if results else 0,
    }

    summary_path = PATHS['logs'] / 'image_processing_summary.json'
    save_json(summary, summary_path)

    if errors:
        errors_path = PATHS['logs'] / 'image_errors.json'
        save_json(errors, errors_path)

    # Print summary
    logger.info("")
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"Total sites: {summary['total_sites']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Total images: {summary['total_images']}")
    logger.info(f"Average per site: {summary['average_images_per_site']:.1f}")
    logger.info("")
    logger.info(f"Summary: {summary_path}")
    if errors:
        logger.info(f"Errors: {errors_path}")
    logger.info("")
    logger.info("✅ Script 2 complete!")

if __name__ == '__main__':
    main()
