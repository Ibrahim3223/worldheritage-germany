"""
Test Content Generator
Creates placeholder content for testing without using OpenAI API
"""

import json
from pathlib import Path
from datetime import datetime

import logging

try:
    from .config import PATHS, PROJECT
    from .utils import load_json, save_json
except ImportError:
    from config import PATHS, PROJECT
    from utils import load_json, save_json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def generate_placeholder_content(site: dict) -> dict:
    """Generate placeholder content for a site"""

    name = site.get('name', 'Heritage Site')
    region = site.get('region', 'Germany')
    heritage_type = site.get('heritage_type', 'heritage site')
    description = site.get('description', '')

    # Create placeholder sections
    content = {
        'introduction': f"{name} is a remarkable {heritage_type} located in {region}, Germany. {description} This site represents an important piece of German cultural and historical heritage.",

        'history': f"The history of {name} dates back several centuries, playing a significant role in the region's development. Over the years, it has witnessed numerous historical events and transformations that have shaped its current form.",

        'architecture': f"The architectural features of {name} showcase exceptional craftsmanship and design. The structure combines traditional German architectural elements with unique characteristics that make it stand out as a notable {heritage_type}.",

        'visiting': f"Visitors to {name} can explore various aspects of this magnificent site. The location offers a rich cultural experience, allowing guests to immerse themselves in German heritage and history.",

        'practical_info': f"{name} is accessible to tourists throughout the year. Visitors should plan their trip in advance to make the most of their experience at this historical location in {region}.",

        'nearby_attractions': f"The area surrounding {name} offers additional points of interest for travelers. {region} is known for its cultural richness and provides various attractions for visitors to explore."
    }

    return {
        'site_id': site.get('wikidata_id'),
        'site_name': name,
        'content': content,
        'word_count': sum(len(text.split()) for text in content.values()),
        'generated_at': datetime.now().isoformat(),
        'generator': 'test_placeholder',
        'quality_score': 50  # Placeholder quality
    }

def main():
    """Generate placeholder content for all test sites"""

    logger.info("="*60)
    logger.info("TEST CONTENT GENERATOR (No GPT)")
    logger.info("="*60)
    logger.info("")

    # Load sites
    sites_file = PATHS['raw'] / 'sites.json'
    sites = load_json(sites_file)
    logger.info(f"Loaded {len(sites)} sites")
    logger.info("")

    # Generate content for each site
    generated = 0

    for site in sites:
        site_name = site.get('name', 'Unknown')
        wikidata_id = site.get('wikidata_id')

        logger.info(f"Generating placeholder content for: {site_name}")

        content_data = generate_placeholder_content(site)
        content_data['wikidata_id'] = wikidata_id
        content_data['site_slug'] = site_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
        content_data['validation'] = {
            'approved': True,
            'quality_score': 75,
            'flesch_score': 60,
            'ai_detection_score': 10
        }

        # Save individual file for each site
        output_file = PATHS['content'] / f"{wikidata_id}.json"
        save_json(content_data, output_file)
        generated += 1

        logger.info(f"  Word count: {content_data['word_count']}")
        logger.info(f"  Saved: {output_file.name}")

    logger.info("")
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"Sites processed: {generated}")
    logger.info(f"Files created: {generated}")
    logger.info(f"Output directory: {PATHS['content']}")
    logger.info("")
    logger.info("[OK] Test content generated!")

if __name__ == '__main__':
    main()
