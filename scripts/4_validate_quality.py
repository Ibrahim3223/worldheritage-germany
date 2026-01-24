"""
Script 4: Validate Content Quality
Checks quality, readability, and accuracy
"""

import re
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

# Handle imports for both package and direct execution
try:
    from .config import PATHS, CONTENT_CONFIG
    from .utils import load_json, save_json, logger
except ImportError:
    from config import PATHS, CONTENT_CONFIG
    from utils import load_json, save_json, logger

# ============================================
# READABILITY SCORING
# ============================================

def calculate_flesch_reading_ease(text: str) -> float:
    """
    Calculate Flesch Reading Ease score

    Args:
        text: Article text

    Returns:
        Flesch score (0-100, higher = easier to read)
    """

    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences)

    if num_sentences == 0:
        return 0

    # Count words
    words = text.split()
    num_words = len(words)

    if num_words == 0:
        return 0

    # Count syllables (simplified)
    def count_syllables(word):
        word = word.lower()
        vowels = 'aeiouy'
        syllables = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllables += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            syllables -= 1

        # Ensure at least 1 syllable
        return max(1, syllables)

    num_syllables = sum(count_syllables(word) for word in words)

    # Calculate Flesch score
    # Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    score = 206.835
    score -= 1.015 * (num_words / num_sentences)
    score -= 84.6 * (num_syllables / num_words)

    return max(0, min(100, score))

def interpret_flesch_score(score: float) -> str:
    """Interpret Flesch score"""
    if score >= 90:
        return "Very easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly easy (7th grade)"
    elif score >= 60:
        return "Standard (8th-9th grade)"
    elif score >= 50:
        return "Fairly difficult (10th-12th grade)"
    elif score >= 30:
        return "Difficult (College)"
    else:
        return "Very difficult (College graduate)"

# ============================================
# AI DETECTION
# ============================================

def detect_ai_patterns(text: str) -> Dict:
    """
    Detect common AI writing patterns

    Args:
        text: Article text

    Returns:
        Detection results dictionary
    """

    text_lower = text.lower()

    # AI cliches
    cliches = {
        'nestled in': 0,
        'boasts': 0,
        'rich tapestry': 0,
        'testament to': 0,
        'stands as a beacon': 0,
        'jewel of': 0,
        'crown jewel': 0,
        'journey through time': 0,
        'step back in time': 0,
        'hidden gem': 0,
        'breathtaking': 0,
    }

    for cliche in cliches.keys():
        cliches[cliche] = text_lower.count(cliche)

    total_cliches = sum(cliches.values())

    # Repetitive sentence starters
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    starters = {}
    for sentence in sentences:
        words = sentence.split()
        if words:
            starter = words[0].lower()
            starters[starter] = starters.get(starter, 0) + 1

    # Find most repeated starter
    if starters:
        most_repeated = max(starters.values())
        repetition_ratio = most_repeated / len(sentences) if sentences else 0
    else:
        repetition_ratio = 0

    # Passive voice detection (simple)
    passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are']
    passive_count = sum(text_lower.count(f' {word} ') for word in passive_indicators)
    passive_ratio = passive_count / len(text.split()) if text.split() else 0

    # AI score (0-100, lower = more human-like)
    ai_score = 0
    ai_score += min(30, total_cliches * 5)  # Cliches (max 30 points)
    ai_score += min(30, repetition_ratio * 100)  # Repetition (max 30 points)
    ai_score += min(40, passive_ratio * 200)  # Passive voice (max 40 points)

    return {
        'ai_score': min(100, ai_score),
        'total_cliches': total_cliches,
        'cliches_found': {k: v for k, v in cliches.items() if v > 0},
        'repetition_ratio': round(repetition_ratio, 2),
        'passive_ratio': round(passive_ratio, 3),
        'interpretation': 'AI-like' if ai_score > 40 else 'Human-like',
    }

# ============================================
# FACT CHECKING
# ============================================

def basic_fact_check(content: str, site_data: Dict) -> Dict:
    """
    Basic fact-checking against source data

    Args:
        content: Generated article text
        site_data: Original Wikidata

    Returns:
        Fact-check results
    """

    issues = []
    content_lower = content.lower()

    # Check if year_built mentioned but not in data
    year_pattern = r'(built|constructed|completed|established) in (\d{4})'
    year_matches = re.findall(year_pattern, content_lower)

    if year_matches and not site_data.get('year_built') and not site_data.get('inception'):
        issues.append(f"Specific construction year mentioned but not in source data: {year_matches}")

    # Check if architect mentioned but not in data
    if 'architect' in content_lower or 'designed by' in content_lower:
        if not site_data.get('architect'):
            # Only flag if specific name is mentioned
            pass

    # Check if specific visitor numbers mentioned
    visitor_pattern = r'(\d+(?:,\d+)*)\s*(?:million|thousand)?\s*(?:visitors|people|tourists)'
    visitor_matches = re.findall(visitor_pattern, content_lower)

    if visitor_matches and not site_data.get('annual_visitors'):
        issues.append(f"Specific visitor numbers mentioned but not in source data: {visitor_matches}")

    return {
        'issues_found': len(issues),
        'issues': issues,
        'passed': len(issues) == 0,
    }

# ============================================
# COMPREHENSIVE VALIDATION
# ============================================

def validate_article(content_data: Dict, site_data: Dict) -> Dict:
    """
    Comprehensive article validation

    Args:
        content_data: Generated content dictionary
        site_data: Original site data

    Returns:
        Complete validation results
    """

    content = content_data['content']
    word_count = content_data['word_count']
    strategy = content_data['strategy']

    # 1. Word count
    word_count_ok = (
        strategy['word_count_min'] <= word_count <= strategy['word_count_max'] * 1.1
    )

    # 2. Readability
    flesch_score = calculate_flesch_reading_ease(content)
    readability_ok = flesch_score >= CONTENT_CONFIG['quality']['readability_min']

    # 3. AI detection
    ai_results = detect_ai_patterns(content)
    ai_ok = ai_results['ai_score'] <= CONTENT_CONFIG['quality']['ai_detection_max']

    # 4. Fact checking
    fact_check = basic_fact_check(content, site_data)
    facts_ok = fact_check['passed']

    # 5. Content structure
    required_keywords = ['visit', 'hour', 'location']
    has_keywords = all(kw in content.lower() for kw in required_keywords)

    # Overall quality score (0-100)
    quality_score = 0

    # Word count (20 points)
    if word_count_ok:
        quality_score += 20
    elif word_count >= strategy['word_count_min']:
        quality_score += 15

    # Readability (25 points)
    if readability_ok:
        quality_score += 25
    elif flesch_score >= 50:
        quality_score += 15

    # AI detection (30 points)
    if ai_ok:
        quality_score += 30
    elif ai_results['ai_score'] <= 20:
        quality_score += 20

    # Fact accuracy (20 points)
    if facts_ok:
        quality_score += 20

    # Structure (5 points)
    if has_keywords:
        quality_score += 5

    # Approval decision
    approved = (
        word_count_ok and
        readability_ok and
        ai_ok and
        facts_ok and
        quality_score >= 70
    )

    return {
        'approved': approved,
        'quality_score': quality_score,
        'word_count': {
            'count': word_count,
            'target_min': strategy['word_count_min'],
            'target_max': strategy['word_count_max'],
            'ok': word_count_ok,
        },
        'readability': {
            'flesch_score': round(flesch_score, 1),
            'interpretation': interpret_flesch_score(flesch_score),
            'ok': readability_ok,
        },
        'ai_detection': ai_results,
        'ai_ok': ai_ok,
        'fact_check': fact_check,
        'facts_ok': facts_ok,
    }

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution"""

    logger.info("="*60)
    logger.info("SCRIPT 4: VALIDATE CONTENT QUALITY")
    logger.info("="*60)
    logger.info("")

    # Load sites data
    sites_file = PATHS['raw'] / 'sites.json'
    if not sites_file.exists():
        logger.error("Sites file not found. Run Script 1 first.")
        return

    sites = load_json(sites_file)
    sites_dict = {s['wikidata_id']: s for s in sites}

    # Load generated content
    content_files = list(PATHS['content'].glob('*.json'))

    if not content_files:
        logger.error("No content files found. Run Script 3 first.")
        return

    logger.info(f"Validating {len(content_files)} articles...")
    logger.info("")

    # Validate each article
    results = []
    approved_count = 0
    rejected_count = 0

    for content_file in tqdm(content_files, desc="Validating"):
        try:
            content_data = load_json(content_file)
            wikidata_id = content_data['wikidata_id']

            if wikidata_id not in sites_dict:
                logger.warning(f"Site data not found for {content_file.name}")
                continue

            site_data = sites_dict[wikidata_id]

            # Validate
            validation = validate_article(content_data, site_data)

            # Add to content data
            content_data['validation'] = validation

            # Save updated content
            save_json(content_data, content_file)

            # Track results
            results.append({
                'site': content_data['site_name'],
                'slug': content_data['site_slug'],
                'approved': validation['approved'],
                'quality_score': validation['quality_score'],
                'word_count': validation['word_count']['count'],
                'flesch_score': validation['readability']['flesch_score'],
                'ai_score': validation['ai_detection']['ai_score'],
            })

            if validation['approved']:
                approved_count += 1
            else:
                rejected_count += 1

        except Exception as e:
            logger.error(f"Validation failed for {content_file.name}: {e}")

    # Generate summary
    if results:
        quality_scores = [r['quality_score'] for r in results]
        flesch_scores = [r['flesch_score'] for r in results]
        ai_scores = [r['ai_score'] for r in results]

        summary = {
            'total_articles': len(results),
            'approved': approved_count,
            'rejected': rejected_count,
            'approval_rate': round(approved_count / len(results) * 100, 1) if results else 0,
            'average_quality_score': round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0,
            'average_flesch_score': round(sum(flesch_scores) / len(flesch_scores), 1) if flesch_scores else 0,
            'average_ai_score': round(sum(ai_scores) / len(ai_scores), 1) if ai_scores else 0,
        }
    else:
        summary = {
            'total_articles': 0,
            'approved': 0,
            'rejected': 0,
            'approval_rate': 0,
            'average_quality_score': 0,
            'average_flesch_score': 0,
            'average_ai_score': 0,
        }

    # Save detailed results
    results_file = PATHS['logs'] / 'validation_results.json'
    save_json(results, results_file)

    summary_file = PATHS['logs'] / 'validation_summary.json'
    save_json(summary, summary_file)

    # Print summary
    logger.info("")
    logger.info("="*60)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total articles: {summary['total_articles']}")
    logger.info(f"Approved: {approved_count} ({summary['approval_rate']}%)")
    logger.info(f"Rejected: {rejected_count}")
    logger.info("")
    logger.info(f"Average quality score: {summary['average_quality_score']}/100")
    logger.info(f"Average readability: {summary['average_flesch_score']} (Flesch)")
    logger.info(f"Average AI score: {summary['average_ai_score']}/100 (lower = better)")
    logger.info("")
    logger.info(f"Results: {results_file}")
    logger.info(f"Summary: {summary_file}")
    logger.info("")
    logger.info("Script 4 complete!")
    logger.info("")
    logger.info("Next: Run Script 5 to generate Hugo site")

if __name__ == '__main__':
    main()
