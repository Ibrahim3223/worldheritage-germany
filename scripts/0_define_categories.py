#!/usr/bin/env python3
"""
COMPREHENSIVE Wikidata Category Definitions
Complete system for fetching 12-17k high-quality sites
Optimized for 100+ countries with quality filters
"""

# ============================================================================
# QUALITY THRESHOLDS
# ============================================================================
QUALITY_FILTERS = {
    "min_sitelinks": 3,          # Minimum Wikipedia language versions
    "require_coordinates": True,  # Must have location
    "require_image": False,       # Image preferred but not required
    "min_claims": 5,             # Minimum Wikidata statements
}

# PAGE LIMITS per category (for balancing content)
CATEGORY_LIMITS = {
    # Natural sites (1,500-2,000 target)
    "waterfall": 50,
    "lake": 200,
    "cave": 50,
    "mountain": 150,
    "gorge": 30,
    "geopark": 20,
    "national_park": 20,
    "nature_reserve": 400,      # From 1000+ to 400
    "biosphere_reserve": 20,
    "nature_park": 100,
    "botanical_garden": 80,
    "zoo": 80,
    "beach": 50,
    "island": 50,
    "valley": 40,

    # Museums & Galleries (3,000-4,000 target)
    "museum": 2500,              # From 6800+ to 2500 (quality filter)
    "art_museum": 400,
    "science_museum": 150,
    "history_museum": 200,
    "technology_museum": 100,
    "local_museum": 300,

    # Religious Buildings (1,500 target)
    "cathedral": 50,
    "basilica": 30,
    "monastery": 250,
    "abbey": 200,
    "synagogue": 150,
    "mosque": 100,
    "chapel": 300,
    "pilgrimage_church": 100,

    # Castles & Palaces (2,000 target)
    "castle": 800,               # From 1000+ to 800
    "palace": 300,
    "fortress": 200,
    "city_wall": 100,
    "castle_ruin": 400,
    "manor_house": 200,

    # Monuments & Memorials (800 target)
    "monument": 300,
    "memorial": 200,
    "statue": 150,
    "fountain": 100,
    "triumphal_arch": 50,

    # Infrastructure (1,000 target)
    "bridge": 250,
    "tower": 200,
    "city_gate": 100,
    "railway_station": 150,
    "lighthouse": 50,
    "windmill": 100,
    "aqueduct": 30,
    "dam": 40,

    # Civic & Government (1,000 target)
    "town_hall": 500,
    "city_hall": 100,
    "courthouse": 50,
    "university": 150,
    "school_building": 100,
    "market_square": 100,

    # Parks & Gardens (500 target)
    "park": 200,
    "garden": 150,
    "sculpture_garden": 50,
    "rose_garden": 30,
    "english_garden": 30,

    # Cultural Venues (800 target)
    "theater": 200,
    "opera_house": 80,
    "concert_hall": 100,
    "cinema": 50,
    "cultural_center": 150,
    "library": 220,

    # Industrial Heritage (400 target)
    "industrial_building": 150,
    "mine": 100,
    "factory": 80,
    "brewery": 70,

    # Cemetery & Burial (200 target)
    "cemetery": 150,
    "mausoleum": 30,
    "tomb": 20,

    # Archaeological Sites (200 target)
    "archaeological_site": 150,
    "roman_villa": 30,
    "prehistoric_site": 20,

    # UNESCO Heritage (100 target) - New categories for UNESCO sites
    "architectural_ensemble": 50,
    "cultural_landscape": 30,
    "old_town": 30,
    "roman_limes": 20,

    # Markets & Commercial (150 target)
    "market_hall": 80,
    "shopping_arcade": 50,
    "covered_market": 20,
}

# Total target: ~15,000 sites

# ============================================================================
# COMPREHENSIVE CATEGORY DEFINITIONS
# ============================================================================

CATEGORIES = {
    # ========== NATURAL FEATURES ==========

    # Water Features
    "waterfall": {
        "wikidata_classes": ["Q34038"],  # waterfall
        "category_tags": ["natural site", "waterfall"],
        "description": "Waterfalls and cascades",
        "priority": "high",
    },
    "lake": {
        "wikidata_classes": ["Q23397"],  # lake
        "category_tags": ["natural site", "lake"],
        "description": "Natural and artificial lakes",
        "priority": "high",
    },
    "river": {
        "wikidata_classes": ["Q4022"],  # river
        "category_tags": ["natural site", "river"],
        "description": "Major rivers",
        "priority": "medium",
    },

    # Geological Features
    "cave": {
        "wikidata_classes": ["Q35509"],  # cave
        "category_tags": ["natural site", "cave"],
        "description": "Natural caves and grottos",
        "priority": "high",
    },
    "mountain": {
        "wikidata_classes": ["Q8502"],  # mountain
        "category_tags": ["natural site", "mountain"],
        "description": "Mountains and peaks",
        "priority": "high",
    },
    "gorge": {
        "wikidata_classes": ["Q133056"],  # gorge
        "category_tags": ["natural site", "gorge"],
        "description": "Gorges and canyons",
        "priority": "medium",
    },
    "valley": {
        "wikidata_classes": ["Q39816"],  # valley
        "category_tags": ["natural site", "valley"],
        "description": "Notable valleys",
        "priority": "medium",
    },

    # Coastal Features
    "beach": {
        "wikidata_classes": ["Q40080"],  # beach
        "category_tags": ["natural site", "beach"],
        "description": "Beaches and coastlines",
        "priority": "high",
    },
    "island": {
        "wikidata_classes": ["Q23442"],  # island
        "category_tags": ["natural site", "island"],
        "description": "Islands",
        "priority": "medium",
    },

    # Protected Areas
    "geopark": {
        "wikidata_classes": ["Q1301686"],  # geopark
        "category_tags": ["natural site", "geopark", "unesco"],
        "description": "UNESCO Global Geoparks",
        "priority": "very_high",
    },
    "national_park": {
        "wikidata_classes": ["Q46169"],  # national park
        "category_tags": ["natural site", "national park"],
        "description": "National parks",
        "priority": "very_high",
    },
    "nature_reserve": {
        "wikidata_classes": ["Q759421"],  # nature reserve
        "category_tags": ["natural site", "nature reserve"],
        "description": "Nature reserves",
        "priority": "high",
    },
    "biosphere_reserve": {
        "wikidata_classes": ["Q158454"],  # biosphere reserve
        "category_tags": ["natural site", "unesco biosphere"],
        "description": "UNESCO Biosphere Reserves",
        "priority": "very_high",
    },
    "nature_park": {
        "wikidata_classes": ["Q3503299"],  # nature park
        "category_tags": ["natural site", "nature park"],
        "description": "Nature parks",
        "priority": "high",
    },

    # Gardens & Zoos
    "botanical_garden": {
        "wikidata_classes": ["Q167346"],  # botanical garden
        "category_tags": ["botanical garden", "garden"],
        "description": "Botanical gardens",
        "priority": "high",
    },
    "zoo": {
        "wikidata_classes": ["Q43501"],  # zoo
        "category_tags": ["zoo", "attraction"],
        "description": "Zoological gardens",
        "priority": "high",
    },

    # ========== MUSEUMS & GALLERIES ==========

    "museum": {
        "wikidata_classes": ["Q33506"],  # museum
        "category_tags": ["museum", "cultural site"],
        "description": "Museums",
        "priority": "very_high",
    },
    "art_museum": {
        "wikidata_classes": ["Q207694"],  # art museum
        "category_tags": ["museum", "art museum"],
        "description": "Art museums and galleries",
        "priority": "very_high",
    },
    "science_museum": {
        "wikidata_classes": ["Q588140"],  # science museum
        "category_tags": ["museum", "science museum"],
        "description": "Science and technology museums",
        "priority": "high",
    },
    "history_museum": {
        "wikidata_classes": ["Q1497375"],  # history museum
        "category_tags": ["museum", "history museum"],
        "description": "History museums",
        "priority": "high",
    },
    "technology_museum": {
        "wikidata_classes": ["Q2864485"],  # technology museum
        "category_tags": ["museum", "technology museum"],
        "description": "Technology museums",
        "priority": "high",
    },
    "local_museum": {
        "wikidata_classes": ["Q7075565"],  # local museum
        "category_tags": ["museum", "local museum"],
        "description": "Local and regional museums",
        "priority": "medium",
    },

    # ========== RELIGIOUS BUILDINGS ==========

    "cathedral": {
        "wikidata_classes": ["Q2977"],  # cathedral
        "category_tags": ["cathedral", "religious site"],
        "description": "Cathedrals",
        "priority": "very_high",
    },
    "basilica": {
        "wikidata_classes": ["Q144384"],  # basilica
        "category_tags": ["basilica", "religious site"],
        "description": "Basilicas",
        "priority": "high",
    },
    "monastery": {
        "wikidata_classes": ["Q44613"],  # monastery
        "category_tags": ["monastery", "religious site"],
        "description": "Monasteries",
        "priority": "high",
    },
    "abbey": {
        "wikidata_classes": ["Q157031"],  # abbey
        "category_tags": ["abbey", "religious site"],
        "description": "Abbeys",
        "priority": "high",
    },
    "synagogue": {
        "wikidata_classes": ["Q34627"],  # synagogue
        "category_tags": ["synagogue", "religious site"],
        "description": "Synagogues",
        "priority": "high",
    },
    "mosque": {
        "wikidata_classes": ["Q32815"],  # mosque
        "category_tags": ["mosque", "religious site"],
        "description": "Mosques",
        "priority": "high",
    },
    "chapel": {
        "wikidata_classes": ["Q108325"],  # chapel
        "category_tags": ["chapel", "religious site"],
        "description": "Chapels",
        "priority": "medium",
    },
    "pilgrimage_church": {
        "wikidata_classes": ["Q56242215"],  # pilgrimage church
        "category_tags": ["pilgrimage church", "religious site"],
        "description": "Pilgrimage churches",
        "priority": "high",
    },

    # ========== CASTLES & FORTIFICATIONS ==========

    "castle": {
        "wikidata_classes": ["Q23413"],  # castle
        "category_tags": ["castle", "fortification"],
        "description": "Castles",
        "priority": "very_high",
    },
    "palace": {
        "wikidata_classes": ["Q16560"],  # palace
        "category_tags": ["palace", "royal residence"],
        "description": "Palaces",
        "priority": "very_high",
    },
    "fortress": {
        "wikidata_classes": ["Q57821"],  # fortress
        "category_tags": ["fortification", "military site"],
        "description": "Fortresses",
        "priority": "high",
    },
    "city_wall": {
        "wikidata_classes": ["Q1763828"],  # city wall
        "category_tags": ["fortification", "city wall"],
        "description": "City walls and fortifications",
        "priority": "medium",
    },
    "castle_ruin": {
        "wikidata_classes": ["Q1127623"],  # castle ruin
        "category_tags": ["castle", "ruin"],
        "description": "Castle ruins",
        "priority": "high",
    },
    "manor_house": {
        "wikidata_classes": ["Q879050"],  # manor house
        "category_tags": ["manor house", "historic building"],
        "description": "Manor houses",
        "priority": "medium",
    },

    # ========== MONUMENTS & MEMORIALS ==========

    "monument": {
        "wikidata_classes": ["Q4989906"],  # monument
        "category_tags": ["monument", "memorial"],
        "description": "Monuments",
        "priority": "high",
    },
    "memorial": {
        "wikidata_classes": ["Q5003624"],  # memorial
        "category_tags": ["memorial", "monument"],
        "description": "War memorials and commemorative sites",
        "priority": "high",
    },
    "statue": {
        "wikidata_classes": ["Q179700"],  # statue
        "category_tags": ["statue", "monument"],
        "description": "Notable statues",
        "priority": "medium",
    },
    "fountain": {
        "wikidata_classes": ["Q483453"],  # fountain
        "category_tags": ["fountain", "monument"],
        "description": "Historic fountains",
        "priority": "medium",
    },
    "triumphal_arch": {
        "wikidata_classes": ["Q33506"],  # triumphal arch
        "category_tags": ["monument", "arch"],
        "description": "Triumphal arches and gates",
        "priority": "high",
    },

    # ========== INFRASTRUCTURE ==========

    "bridge": {
        "wikidata_classes": ["Q12280"],  # bridge
        "category_tags": ["bridge", "infrastructure"],
        "description": "Historic and notable bridges",
        "priority": "high",
    },
    "tower": {
        "wikidata_classes": ["Q12518"],  # tower
        "category_tags": ["tower", "monument"],
        "description": "Towers and observation points",
        "priority": "high",
    },
    "city_gate": {
        "wikidata_classes": ["Q82117"],  # city gate
        "category_tags": ["gate", "fortification"],
        "description": "Historic city gates",
        "priority": "high",
    },
    "railway_station": {
        "wikidata_classes": ["Q55488"],  # railway station
        "category_tags": ["railway station", "infrastructure"],
        "description": "Historic railway stations",
        "priority": "medium",
    },
    "lighthouse": {
        "wikidata_classes": ["Q39715"],  # lighthouse
        "category_tags": ["lighthouse", "infrastructure"],
        "description": "Lighthouses",
        "priority": "medium",
    },
    "windmill": {
        "wikidata_classes": ["Q38720"],  # windmill
        "category_tags": ["windmill", "industrial heritage"],
        "description": "Historic windmills",
        "priority": "medium",
    },
    "aqueduct": {
        "wikidata_classes": ["Q474"],  # aqueduct
        "category_tags": ["aqueduct", "infrastructure"],
        "description": "Aqueducts",
        "priority": "low",
    },
    "dam": {
        "wikidata_classes": ["Q12323"],  # dam
        "category_tags": ["dam", "infrastructure"],
        "description": "Dams and reservoirs",
        "priority": "low",
    },

    # ========== CIVIC & GOVERNMENT ==========

    "town_hall": {
        "wikidata_classes": ["Q25550691"],  # town hall
        "category_tags": ["town hall", "civic building"],
        "description": "Town halls",
        "priority": "high",
    },
    "city_hall": {
        "wikidata_classes": ["Q15548007"],  # city hall
        "category_tags": ["city hall", "civic building"],
        "description": "City halls",
        "priority": "high",
    },
    "courthouse": {
        "wikidata_classes": ["Q1137809"],  # courthouse
        "category_tags": ["courthouse", "government building"],
        "description": "Courthouses",
        "priority": "low",
    },
    "university": {
        "wikidata_classes": ["Q3918"],  # university
        "category_tags": ["university", "education"],
        "description": "Historic university buildings",
        "priority": "medium",
    },
    "school_building": {
        "wikidata_classes": ["Q1244442"],  # school building
        "category_tags": ["school", "education"],
        "description": "Historic school buildings",
        "priority": "low",
    },
    "market_square": {
        "wikidata_classes": ["Q174782"],  # market square
        "category_tags": ["square", "public space"],
        "description": "Market squares",
        "priority": "medium",
    },

    # ========== PARKS & GARDENS ==========

    "park": {
        "wikidata_classes": ["Q22698"],  # park
        "category_tags": ["park", "green space"],
        "description": "Public parks",
        "priority": "medium",
    },
    "garden": {
        "wikidata_classes": ["Q1107656"],  # garden
        "category_tags": ["garden", "green space"],
        "description": "Historic gardens",
        "priority": "medium",
    },
    "sculpture_garden": {
        "wikidata_classes": ["Q2327519"],  # sculpture garden
        "category_tags": ["sculpture garden", "garden"],
        "description": "Sculpture gardens",
        "priority": "low",
    },
    "rose_garden": {
        "wikidata_classes": ["Q1326494"],  # rose garden
        "category_tags": ["rose garden", "garden"],
        "description": "Rose gardens",
        "priority": "low",
    },
    "english_garden": {
        "wikidata_classes": ["Q2675015"],  # English garden
        "category_tags": ["english garden", "garden"],
        "description": "English landscape gardens",
        "priority": "low",
    },

    # ========== CULTURAL VENUES ==========

    "theater": {
        "wikidata_classes": ["Q24354"],  # theater
        "category_tags": ["theater", "cultural site"],
        "description": "Theaters",
        "priority": "high",
    },
    "opera_house": {
        "wikidata_classes": ["Q13022095"],  # opera house
        "category_tags": ["opera house", "theater"],
        "description": "Opera houses",
        "priority": "high",
    },
    "concert_hall": {
        "wikidata_classes": ["Q277760"],  # concert hall
        "category_tags": ["concert hall", "cultural site"],
        "description": "Concert halls",
        "priority": "medium",
    },
    "cinema": {
        "wikidata_classes": ["Q41253"],  # cinema
        "category_tags": ["cinema", "cultural site"],
        "description": "Historic cinemas",
        "priority": "low",
    },
    "cultural_center": {
        "wikidata_classes": ["Q3152824"],  # cultural center
        "category_tags": ["cultural center", "cultural site"],
        "description": "Cultural centers",
        "priority": "medium",
    },
    "library": {
        "wikidata_classes": ["Q7075"],  # library
        "category_tags": ["library", "cultural site"],
        "description": "Libraries",
        "priority": "medium",
    },

    # ========== INDUSTRIAL HERITAGE ==========

    "industrial_building": {
        "wikidata_classes": ["Q1662626"],  # industrial heritage
        "category_tags": ["industrial heritage", "historical site"],
        "description": "Industrial heritage sites",
        "priority": "medium",
    },
    "mine": {
        "wikidata_classes": ["Q820477"],  # mine
        "category_tags": ["mine", "industrial heritage"],
        "description": "Historic mines",
        "priority": "medium",
    },
    "factory": {
        "wikidata_classes": ["Q83405"],  # factory
        "category_tags": ["factory", "industrial heritage"],
        "description": "Historic factories",
        "priority": "low",
    },
    "brewery": {
        "wikidata_classes": ["Q131734"],  # brewery
        "category_tags": ["brewery", "industrial heritage"],
        "description": "Historic breweries",
        "priority": "low",
    },

    # ========== CEMETERY & BURIAL ==========

    "cemetery": {
        "wikidata_classes": ["Q39614"],  # cemetery
        "category_tags": ["cemetery", "memorial"],
        "description": "Historic cemeteries",
        "priority": "low",
    },
    "mausoleum": {
        "wikidata_classes": ["Q162875"],  # mausoleum
        "category_tags": ["mausoleum", "memorial"],
        "description": "Mausoleums",
        "priority": "low",
    },
    "tomb": {
        "wikidata_classes": ["Q381885"],  # tomb
        "category_tags": ["tomb", "memorial"],
        "description": "Historic tombs",
        "priority": "low",
    },

    # ========== ARCHAEOLOGICAL SITES ==========

    "archaeological_site": {
        "wikidata_classes": ["Q839954"],  # archaeological site
        "category_tags": ["archaeological site", "historical site"],
        "description": "Archaeological sites",
        "priority": "high",
    },
    "roman_villa": {
        "wikidata_classes": ["Q744099"],  # Roman villa
        "category_tags": ["roman villa", "archaeological site"],
        "description": "Roman villas and settlements",
        "priority": "medium",
    },
    "prehistoric_site": {
        "wikidata_classes": ["Q4205952"],  # prehistoric site
        "category_tags": ["prehistoric site", "archaeological site"],
        "description": "Prehistoric sites",
        "priority": "medium",
    },

    # ========== UNESCO HERITAGE CATEGORIES ==========

    "architectural_ensemble": {
        "wikidata_classes": ["Q1497375"],  # architectural ensemble
        "category_tags": ["architectural ensemble", "unesco", "heritage site"],
        "description": "Architectural ensembles",
        "priority": "very_high",
    },
    "cultural_landscape": {
        "wikidata_classes": ["Q1129474"],  # cultural landscape
        "category_tags": ["cultural landscape", "unesco", "heritage site"],
        "description": "Cultural landscapes",
        "priority": "very_high",
    },
    "old_town": {
        "wikidata_classes": ["Q676050"],  # old town
        "category_tags": ["old town", "historic district", "heritage site"],
        "description": "Historic old towns",
        "priority": "very_high",
    },
    "roman_limes": {
        "wikidata_classes": ["Q146924"],  # Roman limes
        "category_tags": ["roman limes", "fortification", "archaeological site", "unesco"],
        "description": "Roman frontier fortifications",
        "priority": "very_high",
    },

    # ========== MARKETS & COMMERCIAL ==========

    "market_hall": {
        "wikidata_classes": ["Q1758804"],  # market hall
        "category_tags": ["market hall", "commercial building"],
        "description": "Market halls",
        "priority": "low",
    },
    "shopping_arcade": {
        "wikidata_classes": ["Q3488013"],  # shopping arcade
        "category_tags": ["shopping arcade", "commercial building"],
        "description": "Historic shopping arcades",
        "priority": "low",
    },
    "covered_market": {
        "wikidata_classes": ["Q330284"],  # covered market
        "category_tags": ["covered market", "commercial building"],
        "description": "Covered markets",
        "priority": "low",
    },
}

# Country Wikidata IDs
COUNTRIES = {
    "Germany": "Q183",
    "France": "Q142",
    "Italy": "Q38",
    "Spain": "Q29",
    "UK": "Q145",
    "USA": "Q30",
    "Netherlands": "Q55",
    "Belgium": "Q31",
    "Switzerland": "Q39",
    "Austria": "Q40",
    # Add more as needed
}

def get_category_limit(category_key):
    """Get limit for a category"""
    return CATEGORY_LIMITS.get(category_key, 100)

def get_category_info(category_key):
    """Get category information"""
    return CATEGORIES.get(category_key)

def get_all_categories():
    """Get all available categories"""
    return list(CATEGORIES.keys())

def get_categories_by_priority(priority="high"):
    """Get categories by priority level"""
    return [k for k, v in CATEGORIES.items() if v.get("priority") == priority]

def calculate_total_potential():
    """Calculate total site potential"""
    return sum(CATEGORY_LIMITS.values())

if __name__ == "__main__":
    print("COMPREHENSIVE CATEGORY SYSTEM")
    print("=" * 70)
    print(f"\nTotal categories: {len(CATEGORIES)}")
    print(f"Total page target: {calculate_total_potential():,}")
    print(f"\nQuality filters:")
    for key, value in QUALITY_FILTERS.items():
        print(f"  - {key}: {value}")

    print(f"\nCategories by priority:")
    for priority in ["very_high", "high", "medium", "low"]:
        cats = get_categories_by_priority(priority)
        if cats:
            print(f"\n  {priority.upper()}: {len(cats)} categories")
            for cat in cats[:5]:
                limit = get_category_limit(cat)
                print(f"    - {cat}: {limit} sites")
            if len(cats) > 5:
                print(f"    ... and {len(cats) - 5} more")
