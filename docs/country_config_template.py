"""
Country Configuration Template
Copy this to scripts/country_config.py for each country deployment
"""

# ==============================================================================
# COUNTRY-SPECIFIC CONFIGURATION
# ==============================================================================

COUNTRY_CONFIG = {
    # Basic Information
    'name': 'Germany',              # Full country name
    'code': 'de',                   # ISO 3166-1 alpha-2 code
    'wikidata_qid': 'Q183',         # Wikidata entity ID
    'language': 'en',               # Content language

    # Administrative Divisions (States/Regions/Provinces)
    'regions': [
        'Baden-Württemberg',
        'Bavaria',
        'Berlin',
        'Brandenburg',
        'Bremen',
        'Hamburg',
        'Hesse',
        'Lower Saxony',
        'Mecklenburg-Vorpommern',
        'North Rhine-Westphalia',
        'Rhineland-Palatinate',
        'Saarland',
        'Saxony',
        'Saxony-Anhalt',
        'Schleswig-Holstein',
        'Thuringia'
    ],

    # Heritage Statistics (approximate)
    'unesco_count': 52,             # Number of UNESCO World Heritage Sites
    'estimated_sites': 12000,       # Estimated total heritage sites

    # Wikidata Query Parameters
    'wikidata': {
        # Categories to include in Wikidata query
        'categories': [
            'Q839954',   # Archaeological site
            'Q23413',    # Castle
            'Q16560',    # Palace
            'Q160742',   # Abbey
            'Q16970',    # Church building
            'Q9159',     # Cathedral
            'Q33506',    # Museum
            'Q811979',   # Architectural structure
            'Q839954',   # Archaeological site
            'Q44782',    # Port
            'Q12280',    # Bridge
            'Q44494',    # Mill
            'Q43229',    # Organization (for foundations, institutions)
            'Q860861',   # Sculpture
            'Q4989906',  # Monument
            'Q35145263', # Lighthouse
            'Q28045079', # Historic site
        ],

        # Special designations
        'designations': [
            'Q9259',     # UNESCO World Heritage Site
            'Q61572',    # National monument
            'Q15077985', # Cultural heritage
        ],

        # Natural features
        'natural': [
            'Q8502',     # Mountain
            'Q23397',    # Lake
            'Q355304',   # Waterfall
            'Q35509',    # Cave
            'Q23442',    # Island
            'Q10971235', # Natural monument
        ],
    },

    # Content Generation
    'content': {
        'tone': 'informative and engaging',
        'target_audience': 'international travelers',
        'word_count_min': 500,
        'word_count_max': 1500,

        # LLM Prompts
        'system_prompt': '''You are a professional travel writer creating comprehensive guides
for heritage sites. Write in clear, engaging English that appeals to international travelers.
Focus on history, architecture, cultural significance, and visitor experience.''',

        'site_prompt_template': '''Write a comprehensive travel guide for {site_name},
a {heritage_type} in {region}, {country}. Include:

1. Overview (2-3 paragraphs)
2. History and Significance (3-4 paragraphs)
3. Architecture and Features (2-3 paragraphs)
4. Visiting Information (practical tips)
5. Nearby Attractions (3-5 suggestions)
6. Insider Tips (photography, best times, avoiding crowds)
7. Practical Information (accessibility, facilities)

Write in an engaging, informative style. Focus on what makes this site unique and worth visiting.
Length: 800-1200 words.''',
    },

    # URL and Deployment
    'deployment': {
        'base_url': 'https://de.worldheritage.guide/',
        'cloudflare_project': 'worldheritage-germany',
        'r2_bucket': 'worldheritage-germany-images',
        'github_repo': 'worldheritage-germany',
    },

    # SEO
    'seo': {
        'title_template': 'WorldHeritage.guide - Germany | Comprehensive Heritage Travel Guide',
        'description_template': "Discover Germany's rich cultural and natural heritage. Comprehensive guides to UNESCO sites, monuments, castles, museums, and hidden gems.",
        'keywords': ['Germany', 'heritage', 'UNESCO', 'travel', 'monuments', 'castles', 'museums'],
    },
}

# ==============================================================================
# PRESET CONFIGURATIONS FOR OTHER COUNTRIES
# ==============================================================================

COUNTRY_PRESETS = {
    'france': {
        'name': 'France',
        'code': 'fr',
        'wikidata_qid': 'Q142',
        'language': 'en',
        'regions': [
            'Île-de-France', 'Provence-Alpes-Côte d\'Azur', 'Nouvelle-Aquitaine',
            'Occitanie', 'Auvergne-Rhône-Alpes', 'Grand Est', 'Hauts-de-France',
            'Normandie', 'Brittany', 'Pays de la Loire', 'Centre-Val de Loire',
            'Bourgogne-Franche-Comté', 'Corsica'
        ],
        'unesco_count': 49,
        'estimated_sites': 15000,
        'deployment': {
            'base_url': 'https://fr.worldheritage.guide/',
            'cloudflare_project': 'worldheritage-france',
            'r2_bucket': 'worldheritage-france-images',
            'github_repo': 'worldheritage-france',
        },
    },

    'italy': {
        'name': 'Italy',
        'code': 'it',
        'wikidata_qid': 'Q38',
        'language': 'en',
        'regions': [
            'Lazio', 'Lombardy', 'Tuscany', 'Campania', 'Sicily', 'Veneto',
            'Piedmont', 'Emilia-Romagna', 'Apulia', 'Liguria', 'Calabria',
            'Sardinia', 'Marche', 'Abruzzo', 'Friuli-Venezia Giulia',
            'Umbria', 'Trentino-Alto Adige', 'Basilicata', 'Molise', 'Valle d\'Aosta'
        ],
        'unesco_count': 58,
        'estimated_sites': 20000,
        'deployment': {
            'base_url': 'https://it.worldheritage.guide/',
            'cloudflare_project': 'worldheritage-italy',
            'r2_bucket': 'worldheritage-italy-images',
            'github_repo': 'worldheritage-italy',
        },
    },

    'spain': {
        'name': 'Spain',
        'code': 'es',
        'wikidata_qid': 'Q29',
        'language': 'en',
        'regions': [
            'Andalusia', 'Catalonia', 'Madrid', 'Valencia', 'Galicia',
            'Castile and León', 'Basque Country', 'Castilla-La Mancha',
            'Canary Islands', 'Murcia', 'Aragon', 'Extremadura',
            'Balearic Islands', 'Asturias', 'Navarre', 'Cantabria', 'La Rioja'
        ],
        'unesco_count': 50,
        'estimated_sites': 18000,
        'deployment': {
            'base_url': 'https://es.worldheritage.guide/',
            'cloudflare_project': 'worldheritage-spain',
            'r2_bucket': 'worldheritage-spain-images',
            'github_repo': 'worldheritage-spain',
        },
    },

    'uk': {
        'name': 'United Kingdom',
        'code': 'gb',
        'wikidata_qid': 'Q145',
        'language': 'en',
        'regions': [
            'England', 'Scotland', 'Wales', 'Northern Ireland',
            'London', 'South East', 'South West', 'East of England',
            'West Midlands', 'East Midlands', 'Yorkshire', 'North West',
            'North East', 'Scottish Highlands', 'Scottish Lowlands'
        ],
        'unesco_count': 33,
        'estimated_sites': 25000,
        'deployment': {
            'base_url': 'https://uk.worldheritage.guide/',
            'cloudflare_project': 'worldheritage-uk',
            'r2_bucket': 'worldheritage-uk-images',
            'github_repo': 'worldheritage-uk',
        },
    },
}

# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================

def load_country_config(country_code=None):
    """
    Load country configuration

    Args:
        country_code: ISO country code (e.g., 'de', 'fr', 'it')
                     If None, returns COUNTRY_CONFIG

    Returns:
        dict: Country configuration
    """
    if country_code is None:
        return COUNTRY_CONFIG

    if country_code.lower() in COUNTRY_PRESETS:
        return COUNTRY_PRESETS[country_code.lower()]

    raise ValueError(f"Country code '{country_code}' not found in presets")

# Example usage in scripts:
if __name__ == "__main__":
    # Load current country (Germany)
    config = load_country_config()
    print(f"Current country: {config['name']}")
    print(f"Wikidata QID: {config['wikidata_qid']}")
    print(f"Regions: {len(config['regions'])}")

    # Load preset for another country
    france_config = load_country_config('fr')
    print(f"\nFrance preset:")
    print(f"UNESCO sites: {france_config['unesco_count']}")
    print(f"Base URL: {france_config['deployment']['base_url']}")
