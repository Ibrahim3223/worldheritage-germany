"""
Script 3: Generate Content with GPT-5 Mini
Creates premium travel articles with zero hallucination
"""

import os
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
from tqdm import tqdm

# Handle imports for both package and direct execution
try:
    from .config import (
        PROJECT, PATHS, OPENAI_CONFIG, CONTENT_CONFIG
    )
    from .utils import (
        load_json, save_json, generate_slug, logger
    )
except ImportError:
    from config import (
        PROJECT, PATHS, OPENAI_CONFIG, CONTENT_CONFIG
    )
    from utils import (
        load_json, save_json, generate_slug, logger
    )

# Initialize OpenAI client (lazy - will fail gracefully if no key)
def get_openai_client():
    """Get OpenAI client, raising helpful error if not configured"""
    api_key = OPENAI_CONFIG.get('api_key')
    if not api_key:
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in your .env file")
    return OpenAI(api_key=api_key)

# ============================================
# CONTENT STRATEGY
# ============================================

def get_content_strategy(completeness_score: int) -> Dict:
    """
    Determine content strategy based on data completeness

    Args:
        completeness_score: Site completeness score (0-100)

    Returns:
        Strategy dictionary with word count targets and depth
    """

    if completeness_score >= 70:
        return {
            'word_count_min': 1800,
            'word_count_max': 2200,
            'depth': 'comprehensive and detailed',
            'sections': ['introduction', 'history', 'features',
                        'visiting', 'nearby', 'tips', 'faq'],
        }
    elif completeness_score >= 50:
        return {
            'word_count_min': 1500,
            'word_count_max': 1800,
            'depth': 'informative and engaging',
            'sections': ['introduction', 'history', 'visiting',
                        'nearby', 'tips', 'faq'],
        }
    else:  # 45-49
        return {
            'word_count_min': 1200,
            'word_count_max': 1500,
            'depth': 'focused and factual',
            'sections': ['introduction', 'history', 'visiting', 'faq'],
        }

# ============================================
# PROMPT ENGINEERING
# ============================================

def format_site_data_for_prompt(site: Dict) -> str:
    """Format site data clearly for the GPT prompt"""

    sections = []

    # Basic Info
    sections.append("=== BASIC INFORMATION ===")
    sections.append(f"Name: {site.get('name', 'Unknown')}")
    sections.append(f"Type: {site.get('heritage_type', 'heritage site')}")
    sections.append(f"Region: {site.get('region', 'Germany')}")
    sections.append(f"Country: {site.get('country', 'Germany')}")
    if site.get('description'):
        sections.append(f"Description: {site['description']}")

    # Location
    if site.get('coordinates'):
        sections.append(f"\n=== LOCATION ===")
        sections.append(f"Coordinates: {site['coordinates'][0]}, {site['coordinates'][1]}")

    # Historical Data
    history_data = []
    if site.get('inception'):
        history_data.append(f"Founded/Built: {site['inception']}")
    if site.get('year_built'):
        history_data.append(f"Year Built: {site['year_built']}")
    if site.get('century'):
        history_data.append(f"Century: {site['century']}")
    if site.get('architect'):
        history_data.append(f"Architect: {site['architect']}")
    if site.get('commissioned_by'):
        history_data.append(f"Commissioned by: {site['commissioned_by']}")

    if history_data:
        sections.append(f"\n=== HISTORICAL DATA ===")
        sections.extend(history_data)

    # Physical Attributes
    physical_data = []
    if site.get('height_m'):
        physical_data.append(f"Height: {site['height_m']} meters")
    if site.get('area_sqm'):
        physical_data.append(f"Area: {site['area_sqm']} sq meters")
    if site.get('elevation'):
        physical_data.append(f"Elevation: {site['elevation']} meters")
    if site.get('material'):
        physical_data.append(f"Material: {site['material']}")
    if site.get('style'):
        physical_data.append(f"Architectural Style: {site['style']}")

    if physical_data:
        sections.append(f"\n=== PHYSICAL ATTRIBUTES ===")
        sections.extend(physical_data)

    # UNESCO Status
    if site.get('unesco'):
        sections.append(f"\n=== UNESCO STATUS ===")
        sections.append("UNESCO World Heritage Site: Yes")
        if site.get('unesco_criteria'):
            sections.append(f"UNESCO Criteria: {site['unesco_criteria']}")

    # Visit Information
    visit_data = []
    if site.get('opening_hours'):
        visit_data.append(f"Opening Hours: {site['opening_hours']}")
    if site.get('entry_fee'):
        visit_data.append(f"Entry Fee: {site['entry_fee']}")
    if site.get('official_website'):
        visit_data.append(f"Website: {site['official_website']}")
    if site.get('phone'):
        visit_data.append(f"Phone: {site['phone']}")
    if site.get('annual_visitors'):
        visit_data.append(f"Annual Visitors: {site['annual_visitors']}")

    if visit_data:
        sections.append(f"\n=== VISITOR INFORMATION ===")
        sections.extend(visit_data)

    # Additional Info
    additional = []
    if site.get('religion'):
        additional.append(f"Religion: {site['religion']}")
    if site.get('period'):
        additional.append(f"Period: {site['period']}")
    if site.get('protection_status'):
        additional.append(f"Protection Status: {site['protection_status']}")

    if additional:
        sections.append(f"\n=== ADDITIONAL INFO ===")
        sections.extend(additional)

    return "\n".join(sections)


def build_content_prompt(site: Dict, strategy: Dict) -> str:
    """
    Build comprehensive data-driven prompt for GPT
    Optimized for 1500-2000 word detailed travel guides
    """

    site_name = site['name']
    heritage_type = site.get('heritage_type', 'heritage site')
    region = site.get('region', 'Germany')

    # Format site data clearly
    formatted_data = format_site_data_for_prompt(site)

    prompt = f"""You are writing for WorldHeritage.guide, a premium heritage travel platform.

================================================================================
MISSION: Write a {strategy['depth']} guide to {site_name}
================================================================================

TARGET: {strategy['word_count_min']}-{strategy['word_count_max']} words
STYLE: National Geographic meets Lonely Planet - authoritative yet engaging

================================================================================
CRITICAL RULE #1: DATA INTEGRITY (MOST IMPORTANT)
================================================================================

You MUST follow these rules with ZERO exceptions:

1. ONLY use facts from the SITE DATA section below
2. If information is missing, write around it gracefully - readers won't notice
3. NEVER invent or guess:
   - Specific dates, years, or centuries
   - Prices or admission fees
   - Opening hours or schedules
   - Heights, areas, or dimensions
   - Names of architects, builders, or historical figures
   - Visitor statistics or numbers
   - Any specific facts not in the data

4. For missing practical info, use these EXACT phrases:
   - Hours: "Check the official website for current opening hours"
   - Prices: "Visit the official website for current admission prices"
   - Contact: "Contact the site directly for the latest information"

5. For historical/architectural sections with missing data:
   - Use general language: "historically significant", "over the centuries"
   - Focus on what CAN be said from the data
   - Skip sections entirely if no relevant data exists

6. GEOGRAPHIC ACCURACY:
   - NEVER mention specific geographic features (valleys, rivers, mountains) not in the data
   - NEVER mention specific nearby cities, towns, or regions not in the data
   - Use only GENERAL directional language: "the surrounding landscape", "the vista below", "the nearby area"
   - Do NOT invent specific place names, valleys, or regions
   - Exception: Only mention the EXACT region from the site data (e.g., "Schwangau" if that's the region field)

7. DOUBLE-CHECK BEFORE WRITING:
   - Before mentioning ANY specific fact, verify it exists in the SITE DATA section above
   - When in doubt, use general language instead of specific claims
   - It's better to be vague than wrong

================================================================================
CRITICAL RULE #2: FORBIDDEN PHRASES (AI CLICHÉS)
================================================================================

NEVER use these phrases - they mark content as AI-generated:

- "nestled in/among"
- "boasts" (as in "the castle boasts")
- "rich tapestry"
- "testament to"
- "stands as a beacon"
- "jewel of" / "crown jewel"
- "journey through time"
- "step back in time"
- "hidden gem" (unless provably obscure)
- "breathtaking views" (be specific instead)
- "a feast for the senses"
- "where history comes alive"
- "steeped in history"
- "treasure trove"
- "picture-perfect"
- "postcard-worthy"

INSTEAD: Use specific, concrete, vivid language.
BAD: "The castle boasts breathtaking views"
GOOD: "From the north tower, the Rhine Valley stretches 40 kilometers to the horizon"

================================================================================
CRITICAL RULE #3: WRITING EXCELLENCE
================================================================================

1. SENTENCE VARIETY:
   - Mix short punchy sentences with longer flowing ones
   - Start some sentences with: And, But, So, Yet, Or
   - Use questions occasionally: "What draws visitors here?"

2. VOICE & TENSE:
   - Active voice 90%+ of the time
   - Present tense for descriptions
   - Past tense only for historical events
   - Second person welcome: "you'll discover", "your visit"

3. SPECIFICITY:
   - Concrete details over vague adjectives
   - Sensory details: what you see, hear, feel
   - Directional language: "to the east", "at the entrance"

================================================================================
SITE DATA - YOUR ONLY SOURCE OF FACTS
================================================================================

{formatted_data}

================================================================================
ARTICLE STRUCTURE
================================================================================

Write these sections with CLEAR MARKDOWN HEADERS (## for H2):

## Overview (200-300 words)
   - Hook: Start with a surprising fact, vivid scene, or historical moment
   - Geographic context: Where is it? What's the landscape like?
   - Significance: Why does this place matter?
   - Promise: What will the reader discover?

## History and Significance (400-600 words) - ONLY IF HISTORICAL DATA EXISTS
   - Use ONLY dates/facts from the data
   - If no dates: use general phrases ("over centuries", "through the ages")
   - Key figures: ONLY mention if in the data
   - Major events and transformations
   - UNESCO significance (if applicable)

   >>> IF NO HISTORICAL DATA: Skip this section

## Architecture and Features (300-500 words) - ONLY IF PHYSICAL DATA EXISTS
   - Physical description using PROVIDED measurements
   - Architectural style (if in data)
   - Notable features visitors should look for
   - Materials and construction (if in data)

   >>> IF NO ARCHITECTURAL DATA: Skip this section

## Visiting Information (400-500 words) - REQUIRED
   - Getting there: General transport options for the region
   - Hours/Fees: Use data if available, otherwise "check official website"
   - What to expect: The visitor experience
   - Time needed: Estimate based on site type (1-2 hours for church, half-day for castle, etc.)
   - Best times: Morning for fewer crowds, spring/fall for weather
   - Accessibility: Mention if relevant

## Nearby Attractions (200-300 words)
   - 3-5 nearby places worth visiting
   - Brief description of each
   - Can mention general regional attractions

## Insider Tips (150-200 words) - REQUIRED
   - Best photography spots and times
   - Lesser-known details to look for
   - How to avoid crowds
   - Local tips

## Practical Information (200-250 words)
   - Consolidate all visitor details
   - What to bring
   - Seasonal considerations

## Frequently Asked Questions (300-400 words) - REQUIRED
   Write 8-10 common questions visitors would ask, with detailed answers.
   Use this EXACT format for SEO and accordion compatibility:

   ### [Question here]?
   [Detailed answer 2-3 sentences]

   Example questions:
   - How long should I spend visiting?
   - Is photography allowed inside?
   - Are there guided tours available?
   - What's the best time of day to visit?
   - Is the site wheelchair accessible?
   - Can I buy tickets online?
   - Are there facilities like restrooms and cafes?
   - What should I wear when visiting?

   IMPORTANT: Use ### (H3) for each question, not bold. Answer directly below with no prefix.

================================================================================
OUTPUT FORMAT
================================================================================

IMPORTANT: Use markdown headers (##) for each section except the introduction.
Write flowing prose within each section.
Use bold (**text**) for FAQ questions.
The article should be well-structured and easy to scan.

================================================================================
BEGIN WRITING
================================================================================

Remember the priority: DATA ACCURACY > ENGAGING WRITING > WORD COUNT

Start with a compelling opening line that draws the reader in.
"""

    return prompt

# ============================================
# CONTENT GENERATION
# ============================================

def generate_article(site: Dict, client: OpenAI) -> Dict:
    """
    Generate article content using GPT-5 Mini

    Args:
        site: Site data dictionary
        client: OpenAI client instance

    Returns:
        Generated content dictionary
    """

    site_name = site['name']
    logger.info(f"Generating content for: {site_name}")

    # Get strategy
    completeness = site.get('completeness_score', 50)
    strategy = get_content_strategy(completeness)

    # Build prompt
    prompt = build_content_prompt(site, strategy)

    try:
        # Call GPT-5 Mini
        response = client.chat.completions.create(
            model=OPENAI_CONFIG['model'],
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel writer. You write engaging, factual, SEO-optimized heritage site guides. You NEVER invent facts - only use provided data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=OPENAI_CONFIG['temperature'],
            max_tokens=OPENAI_CONFIG['max_tokens'],
            top_p=OPENAI_CONFIG['top_p'],
            presence_penalty=OPENAI_CONFIG['presence_penalty'],
            frequency_penalty=OPENAI_CONFIG['frequency_penalty'],
        )

        content = response.choices[0].message.content

        # Calculate word count
        word_count = len(content.split())

        # Build result
        result = {
            'site_name': site_name,
            'site_slug': generate_slug(site_name),
            'wikidata_id': site['wikidata_id'],
            'completeness_score': completeness,
            'strategy': strategy,
            'content': content,
            'word_count': word_count,
            'model': OPENAI_CONFIG['model'],
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tokens_used': response.usage.total_tokens,
        }

        logger.info(f"Generated {word_count} words for {site_name}")

        return result

    except Exception as e:
        logger.error(f"Content generation failed for {site_name}: {e}")
        raise

# ============================================
# VALIDATION
# ============================================

def validate_content(content_data: Dict, site: Dict) -> Dict:
    """
    Validate generated content for quality and accuracy

    Args:
        content_data: Generated content dictionary
        site: Original site data

    Returns:
        Validation results dictionary
    """

    content = content_data['content']
    strategy = content_data['strategy']

    issues = []
    warnings = []

    # 1. Word count check
    word_count = content_data['word_count']
    if word_count < strategy['word_count_min']:
        issues.append(f"Word count too low: {word_count} < {strategy['word_count_min']}")
    elif word_count > strategy['word_count_max']:
        warnings.append(f"Word count high: {word_count} > {strategy['word_count_max']}")

    # 2. AI cliche detection
    cliches = [
        'nestled in', 'boasts', 'rich tapestry', 'testament to',
        'stands as a beacon', 'jewel of', 'crown jewel',
        'journey through time', 'step back in time'
    ]

    content_lower = content.lower()
    found_cliches = [c for c in cliches if c in content_lower]
    if found_cliches:
        warnings.append(f"AI cliches detected: {', '.join(found_cliches)}")

    # 3. Check for invented dates (basic check)
    # If site has no year_built but content mentions specific construction dates
    if not site.get('year_built') and not site.get('inception'):
        year_pattern = r'(built|constructed|completed|founded|established) in (\d{4})'
        matches = re.findall(year_pattern, content_lower)
        if matches:
            warnings.append(f"Specific dates mentioned but not in source data: {matches}")

    # 4. Content structure check
    required_elements = ['visit', 'hour', 'fee']  # Basic elements that should be mentioned
    missing = [elem for elem in required_elements if elem not in content_lower]
    if missing:
        warnings.append(f"Missing common visit info elements: {missing}")

    # Quality score (0-100)
    score = 100
    score -= len(issues) * 20  # Major issues
    score -= len(warnings) * 5  # Minor warnings
    score = max(0, score)

    return {
        'valid': len(issues) == 0,
        'quality_score': score,
        'issues': issues,
        'warnings': warnings,
    }

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution"""

    logger.info("="*60)
    logger.info("SCRIPT 3: GENERATE CONTENT WITH GPT-5 MINI")
    logger.info("="*60)
    logger.info("")

    # Check API key and get client
    try:
        client = get_openai_client()
        logger.info("OpenAI client initialized")
    except ValueError as e:
        logger.error(str(e))
        return

    # Load sites from Phase 1
    sites_file = PATHS['raw'] / 'sites.json'

    if not sites_file.exists():
        logger.error(f"Sites file not found: {sites_file}")
        logger.error("Run Script 1 first (1_fetch_wikidata.py)")
        return

    sites = load_json(sites_file)
    logger.info(f"Loaded {len(sites)} sites")
    logger.info(f"Model: {OPENAI_CONFIG['model']}")
    logger.info("")

    # Process each site
    results = []
    errors = []
    total_tokens = 0
    total_cost_estimate = 0

    for site in tqdm(sites, desc="Generating content"):
        try:
            # Generate content
            content_data = generate_article(site, client)

            # Validate
            validation = validate_content(content_data, site)
            content_data['validation'] = validation

            # Save individual content file
            slug = content_data['site_slug']
            content_file = PATHS['content'] / f"{slug}.json"
            save_json(content_data, content_file)

            # Track statistics
            results.append(content_data)
            total_tokens += content_data['tokens_used']

            # Cost estimate (GPT-5 Mini pricing - update if needed)
            # Approximate: $0.15 per 1M input tokens, $0.60 per 1M output tokens
            # Rough estimate: ~$0.001 per article
            total_cost_estimate += 0.001

            # Rate limiting (1 request per second to be safe)
            time.sleep(1)

        except Exception as e:
            logger.error(f"Failed to process {site['name']}: {e}")
            errors.append({
                'site': site['name'],
                'error': str(e)
            })

    # Calculate statistics
    if results:
        word_counts = [r['word_count'] for r in results]
        quality_scores = [r['validation']['quality_score'] for r in results]

        summary = {
            'total_sites': len(sites),
            'successful': len(results),
            'failed': len(errors),
            'total_words': sum(word_counts),
            'average_words': sum(word_counts) / len(word_counts),
            'total_tokens': total_tokens,
            'estimated_cost_usd': round(total_cost_estimate, 2),
            'average_quality_score': sum(quality_scores) / len(quality_scores),
        }
    else:
        summary = {
            'total_sites': len(sites),
            'successful': 0,
            'failed': len(errors),
            'total_words': 0,
            'average_words': 0,
            'total_tokens': 0,
            'estimated_cost_usd': 0,
            'average_quality_score': 0,
        }

    # Save summary
    summary_path = PATHS['logs'] / 'content_generation_summary.json'
    save_json(summary, summary_path)

    if errors:
        errors_path = PATHS['logs'] / 'content_errors.json'
        save_json(errors, errors_path)

    # Print summary
    logger.info("")
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"Total sites: {summary['total_sites']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Total words: {summary['total_words']:,}")
    logger.info(f"Average words/article: {summary['average_words']:.0f}")
    logger.info(f"Total tokens: {summary['total_tokens']:,}")
    logger.info(f"Estimated cost: ${summary['estimated_cost_usd']}")
    logger.info(f"Average quality: {summary['average_quality_score']:.1f}/100")
    logger.info("")
    logger.info(f"Summary: {summary_path}")
    if errors:
        logger.info(f"Errors: {errors_path}")
    logger.info("")
    logger.info("Script 3 complete!")
    logger.info("")
    logger.info("Next: Run Script 4 for quality validation")

if __name__ == '__main__':
    main()
