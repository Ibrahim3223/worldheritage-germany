"""
Test Script: Generate content for a single site with GPT
To test the new comprehensive prompt
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()
base_dir = Path(__file__).parent.parent

# OpenAI setup
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load test sites
sites_file = base_dir / 'data/raw/sites_test.json'
with open(sites_file, 'r', encoding='utf-8') as f:
    sites = json.load(f)

# Pick Aachen Cathedral (has good data)
site = next(s for s in sites if 'Aachen' in s['name'])

print("Testing GPT-4o-mini with new comprehensive prompt...")
print("=" * 60)
print(f"Site: {site['name']}")
print(f"Data completeness: {site.get('completeness_score', 0)}%")
print("=" * 60)

# Import the prompt builder using importlib
import sys
import importlib.util
sys.path.insert(0, str(base_dir / 'scripts'))

# Load the 3_generate_content module
spec = importlib.util.spec_from_file_location("generate_content", base_dir / 'scripts' / '3_generate_content.py')
generate_content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_content)

# Get the functions
format_site_data_for_prompt = generate_content.format_site_data_for_prompt
build_content_prompt = generate_content.build_content_prompt

# Content strategy - adjusted for more comprehensive content
strategy = {
    'depth': 'comprehensive and detailed',
    'word_count_min': 1800,
    'word_count_max': 2200,
    'sections': ['introduction', 'history', 'features', 'visiting', 'nearby', 'tips', 'faq']
}

# Build prompt
prompt = build_content_prompt(site, strategy)

print("\nPrompt length:", len(prompt), "characters")
print("\nCalling GPT-4o-mini...")
print("-" * 60)

# Call GPT with higher max_tokens for 1800-2200 word articles
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert travel writer for WorldHeritage.guide. You write engaging, factual, SEO-optimized heritage site guides that are 1800-2200 words long. You NEVER invent facts - only use provided data. IMPORTANT: Write detailed, comprehensive articles that hit the target word count."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=8000  # Increased to allow full 1800-2200 words
)

content_text = response.choices[0].message.content
word_count = len(content_text.split())

print("Response received!")
print("=" * 60)
print(f"Word count: {word_count} words")
print(f"Character count: {len(content_text)} characters")
print("=" * 60)
print("\nFirst 500 characters:")
print(content_text[:500])
print("\n...")
print("\nLast 500 characters:")
print(content_text[-500:])
print("=" * 60)

# Save full content
output_file = base_dir / 'test_gpt_output.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Site: {site['name']}\n")
    f.write(f"Word Count: {word_count}\n")
    f.write("=" * 60 + "\n\n")
    f.write(content_text)

print(f"\nFull output saved to: {output_file}")
print("\nQuality check:")
print(f"  - Target: 1500-2000 words")
print(f"  - Actual: {word_count} words")
print(f"  - Status: {'PASS' if 1500 <= word_count <= 2500 else 'FAIL'}")
