"""
WorldHeritage.guide - Germany Configuration
PRODUCTION SETTINGS - DO NOT MODIFY WITHOUT REVIEW
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

# ============================================
# PROJECT METADATA
# ============================================

PROJECT = {
    'name': 'WorldHeritage.guide - Germany',
    'country': 'Germany',
    'country_code': 'DE',
    'wikidata_id': 'Q183',
    'subdomain': 'de.worldheritage.guide',
    'primary_language': 'en',
    'local_language': 'de',
}

# ============================================
# PATHS
# ============================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'  # Outside data folder (Hugo parses data/)

PATHS = {
    'raw': DATA_DIR / 'raw',
    'processed': DATA_DIR / 'processed',
    'content': DATA_DIR / 'content',
    'images': BASE_DIR / 'static' / 'images-sites',  # In static for Hugo
    'logs': LOGS_DIR,
    'hugo_content': BASE_DIR / 'content',
    'hugo_static': BASE_DIR / 'static',
}

# Create directories
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

# ============================================
# WIKIDATA - HERITAGE TYPES
# ============================================

HERITAGE_TYPES = {
    # UNESCO & Monuments
    'Q9259': 'UNESCO World Heritage Site',
    'Q4989906': 'Monument',
    'Q570116': 'National Monument',
    'Q41176': 'Historic Building',

    # Palaces & Castles
    'Q16560': 'Palace',
    'Q23413': 'Castle',
    'Q57831': 'Fortress',
    'Q1785071': 'Citadel',

    # Religious
    'Q32815': 'Mosque',
    'Q16970': 'Church',
    'Q2977': 'Cathedral',
    'Q328': 'Basilica',
    'Q811979': 'Buddhist Temple',
    'Q842402': 'Hindu Temple',
    'Q34627': 'Synagogue',
    'Q44613': 'Monastery',
    'Q160742': 'Abbey',

    # Archaeological
    'Q839954': 'Archaeological Site',
    'Q1549591': 'Ancient City',
    'Q109607': 'Ruins',

    # Cultural
    'Q33506': 'Museum',
    'Q207694': 'Art Museum',
    'Q1344': 'Opera House',
    'Q24354': 'Theater',

    # Nature
    'Q46169': 'National Park',
    'Q179049': 'Nature Reserve',
    'Q34038': 'Waterfall',
    'Q23397': 'Lake',
    'Q177380': 'Hot Spring',
    'Q83471': 'Geyser',

    # Coastal
    'Q40080': 'Beach',
    'Q39594': 'Bay',
    'Q107425': 'Cliff',
    'Q23442': 'Island',

    # Mountains & Geological
    'Q207326': 'Mountain Peak',
    'Q35509': 'Cave',
    'Q133056': 'Gorge',
    'Q185528': 'Karst',

    # Civil Engineering
    'Q12280': 'Bridge',
    'Q18870689': 'Aqueduct',
    'Q39715': 'Lighthouse',
    'Q38720': 'Windmill',
    'Q185187': 'Watermill',

    # Gardens & Parks
    'Q1107656': 'Garden',
    'Q22698': 'Park',
    'Q167346': 'Botanical Garden',

    # Urban Heritage
    'Q7545011': 'Historic District',
    'Q174782': 'Town Square',
    'Q43483': 'Fountain',
}

# ============================================
# DATA QUALITY THRESHOLDS
# ============================================

DATA_QUALITY = {
    'completeness_minimum': 45,
    'image_quality_minimum': 50,

    'required_fields': [
        'wikidata_id',
        'name',
        'coordinates',
        'country',
        'heritage_type',
    ],

    'scoring': {
        'critical_fields': {
            'name': 10,
            'coordinates': 10,
            'country': 5,
            'heritage_type': 5,
            'description': 10,
        },
        'important_fields': {
            'year_built': 5,
            'images': 5,
            'opening_hours': 5,
            'entry_fee': 3,
            'annual_visitors': 3,
            'architect': 3,
            'unesco': 3,
            'official_website': 3,
        },
        'nice_to_have': {
            'elevation': 2,
            'area_sqm': 2,
            'height_m': 2,
            'period': 3,
            'style': 3,
            'phone': 2,
            'email': 2,
            'accessibility': 3,
            'parking': 2,
            'best_time': 3,
            'peak_season': 3,
            'material': 3,
        }
    }
}

# ============================================
# IMAGE CONFIGURATION
# ============================================

IMAGE_CONFIG = {
    'strategy': 'download_and_optimize',

    'per_site': {
        'minimum': 1,
        'target': 3,
        'maximum': 3,
    },

    'requirements': {
        'min_width': 1024,
        'min_height': 768,
        'aspect_ratio_min': 1.2,
        'aspect_ratio_max': 2.0,
        'min_file_size': 100_000,
        'max_file_size': 5_000_000,
        'formats': ['jpg', 'jpeg', 'png', 'webp'],
    },

    'optimization': {
        'format': 'webp',
        'quality': 85,
        'max_width': 1920,
        'srcset_widths': [320, 640, 1024, 1920],
    },

    'fallback': {
        'use_satellite': True,
        'provider': 'mapbox',
        'zoom': 16,
    }
}

# ============================================
# CONTENT GENERATION
# ============================================

OPENAI_CONFIG = {
    'model': 'gpt-4o-mini',
    'api_key': os.environ.get('OPENAI_API_KEY'),
    'temperature': 0.7,
    'max_tokens': 8000,  # Increased to allow 1800-2200 word articles
    'top_p': 0.9,
    'presence_penalty': 0.1,
    'frequency_penalty': 0.1,
}

CONTENT_CONFIG = {
    'word_count': {
        'minimum': 1200,
        'target': 1800,
        'maximum': 2500,
    },

    'sections': [
        'introduction',
        'history',
        'features',
        'visiting',
        'nearby',
        'tips',
        'faq',
    ],

    'quality': {
        'data_accuracy': 100,
        'ai_detection_max': 5,
        'readability_min': 60,
        'internal_links_min': 15,
    }
}

# ============================================
# WIKISPARQL
# ============================================

SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'
SPARQL_TIMEOUT = 180  # 3 minutes for complex queries

# ============================================
# API KEYS
# ============================================

API_KEYS = {
    'openai': os.environ.get('OPENAI_API_KEY'),
    'mapbox': os.environ.get('MAPBOX_TOKEN'),
}

# ============================================
# LOGGING
# ============================================

LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / 'worldheritage.log',
}

# ============================================
# SEO
# ============================================

SEO_CONFIG = {
    'title_template': '{site_name}: Complete Guide 2026 | {category}, {region}',
    'description_template': '{site_name} in {region}, {country}. {key_info}. Opening hours, tickets, best time to visit, and insider tips.',
    'title_length': (50, 60),
    'description_length': (150, 160),
}
