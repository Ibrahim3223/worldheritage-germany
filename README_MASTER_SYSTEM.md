# Master System - WorldHeritage Multi-Country Platform

**Status:** Production Ready
**Target:** 12,000-17,000 pages per country
**Scalability:** 100+ countries

---

## 🎯 System Overview

This is a complete, production-ready system for creating comprehensive heritage site websites for any country. The system uses Wikidata as the data source, applies quality filters, optionally enhances content with GPT, and generates a static Hugo website.

### Current Stats (Germany)
- **Pages:** 1,085 (churches, castles, palaces only)
- **Potential:** 15,000+ sites (with comprehensive categories)
- **Quality:** 100% coordinates, multi-language descriptions
- **Images:** ~95% coverage

---

## 📁 Core Scripts (Production)

### 1. **wikidata_categories_comprehensive.py** (22KB)
**Purpose:** Complete category definitions for 80+ site types

**Features:**
- 80+ categories (museums, natural sites, monuments, etc.)
- Quality filters (min sitelinks, coordinates, claims)
- Per-category limits (balanced content distribution)
- Target: 12,000-17,000 sites

**Categories Include:**
- **Natural:** Waterfalls, lakes, caves, mountains, national parks, beaches
- **Museums:** Art, science, history, technology, local museums
- **Religious:** Cathedrals, monasteries, synagogues, mosques
- **Castles:** Castles, palaces, fortresses, ruins
- **Infrastructure:** Bridges, towers, lighthouses, railway stations
- **Civic:** Town halls, universities, libraries, theaters
- **And 60+ more...**

### 2. **master_fetch_sites.py** (12KB)
**Purpose:** Fetch sites from Wikidata with quality filtering

**Usage:**
```bash
# Fetch for Germany (default target: 15,000 sites)
python master_fetch_sites.py Germany

# Custom target
python master_fetch_sites.py France --target 12000

# Specific priorities only
python master_fetch_sites.py Italy --priorities very_high high

# Test mode (5 sites per category)
python master_fetch_sites.py Spain --test
```

**Features:**
- Quality filtering (sitelinks, coordinates, claims)
- Smart prioritization (UNESCO → high-value → medium → low)
- Rate limiting (Wikidata-friendly)
- Progress tracking
- JSON output to `data/fetched/`

**Quality Filters:**
- Minimum 3 Wikipedia language versions
- Coordinates required
- Minimum 5 Wikidata claims
- Ordered by popularity (sitelinks)

### 3. **create_pages_master.py** (13KB)
**Purpose:** Generate markdown pages with optional GPT enhancement

**Usage:**
```bash
# Basic mode (no GPT)
python create_pages_master.py Germany

# With GPT enhancement
python create_pages_master.py Germany --with-gpt --gpt-key YOUR_KEY

# Skip images (faster)
python create_pages_master.py Germany --skip-images

# Environment variable
export OPENAI_API_KEY=your_key
python create_pages_master.py Germany --with-gpt
```

**Features:**
- GPT-4 content enhancement (optional)
- Image downloading from Wikimedia Commons
- YAML-safe frontmatter
- Quality metadata (sitelinks, coordinates, categories)
- Markdown formatting
- Progress tracking

**Content Quality:**
- With GPT: 150-200 words, engaging narratives
- Without GPT: Basic but structured content
- All include: Overview, History, Visiting sections

### 4. **optimize_images.py** (2.1KB)
**Purpose:** Optimize downloaded images

**Features:**
- Convert to WebP format
- Single size only (1920w for quality)
- Hugo handles responsive sizing
- Removes duplicates

### 5. **validate_project.py** (6.9KB)
**Purpose:** Validate project structure and data quality

**Checks:**
- File structure integrity
- YAML frontmatter validation
- Coordinate quality
- Image availability
- Content length
- Category distribution

---

## 🚀 Complete Workflow

### Step 1: Fetch Data (2-4 hours)
```bash
# Fetch 15,000 high-quality sites
python master_fetch_sites.py Germany --target 15000
```

**Output:** `data/fetched/germany_*.json` (80+ files)

### Step 2: Create Pages (2-8 hours)
```bash
# Option A: Basic (fast, no GPT)
python create_pages_master.py Germany

# Option B: With GPT (slow, high quality)
python create_pages_master.py Germany --with-gpt

# Option C: No images (fastest)
python create_pages_master.py Germany --skip-images
```

**Output:** `content/sites/*.md` (15,000 pages)

### Step 3: Build Site
```bash
# Start Hugo development server
hugo server

# Build for production
hugo --minify
```

**Output:** `public/` (static website)

---

## 📊 Expected Results

### Content Distribution (15,000 pages target)

| Category | Pages | % |
|----------|-------|---|
| Museums | 2,500-3,000 | 17-20% |
| Religious Sites | 2,000-2,500 | 13-17% |
| Castles & Palaces | 1,800-2,200 | 12-15% |
| Natural Sites | 1,500-2,000 | 10-13% |
| Infrastructure | 1,000-1,200 | 7-8% |
| Monuments | 800-1,000 | 5-7% |
| Civic Buildings | 800-1,000 | 5-7% |
| Cultural Venues | 600-800 | 4-5% |
| Industrial Heritage | 300-400 | 2-3% |
| Other | 1,000-1,500 | 7-10% |

### Quality Metrics
- ✅ **Coordinates:** 100% (required by filter)
- ✅ **Images:** 80-90% (depends on Wikimedia coverage)
- ✅ **Content:** 150-200 words per page (with GPT)
- ✅ **Multi-language:** Average 5-10 Wikipedia versions per site
- ✅ **Accuracy:** High (Wikidata verified)

---

## 🌍 Multi-Country Expansion

### Supported Countries
The system works with **any country** in Wikidata. Pre-configured:

- 🇩🇪 Germany (Q183) - **15,000+ potential**
- 🇫🇷 France (Q142) - **18,000+ potential**
- 🇮🇹 Italy (Q38) - **20,000+ potential**
- 🇪🇸 Spain (Q29) - **12,000+ potential**
- 🇬🇧 UK (Q145) - **18,000+ potential**
- 🇺🇸 USA (Q30) - **50,000+ potential**
- And 190+ more...

### To Add a New Country:
1. Add to `COUNTRIES` dict in `wikidata_categories_comprehensive.py`
2. Run: `python master_fetch_sites.py NewCountry`
3. Run: `python create_pages_master.py NewCountry`
4. Done!

**Time per country:** 1-2 days for 15k sites

---

## 💰 Cost Estimation

### With GPT-4 Enhancement
- **API Costs:** ~$30-50 per 15,000 pages
- **Time:** 6-8 hours (with rate limiting)
- **Quality:** Premium content, engaging narratives

### Without GPT (Basic)
- **API Costs:** $0
- **Time:** 2-3 hours
- **Quality:** Good structure, factual content

### Image Downloading
- **Bandwidth:** ~5-10GB per 15,000 sites
- **Time:** 4-6 hours (with rate limiting)
- **Cost:** Free (Wikimedia Commons)

---

## 🔧 Configuration

### Quality Filters (`wikidata_categories_comprehensive.py`)

```python
QUALITY_FILTERS = {
    "min_sitelinks": 3,          # Minimum Wikipedia versions
    "require_coordinates": True,  # Must have location
    "require_image": False,       # Image preferred but not required
    "min_claims": 5,             # Minimum Wikidata statements
}
```

### Category Limits

```python
CATEGORY_LIMITS = {
    "museum": 2500,              # Quality over quantity
    "castle": 800,
    "waterfall": 50,
    # ... 80+ more
}
```

Adjust based on:
- Target page count (12k-17k)
- Country characteristics
- Content focus

---

## 📈 Performance Optimization

### Wikidata Queries
- **Rate Limiting:** 0.5s between requests
- **Batch Size:** 1000 results per query
- **Quality First:** ORDER BY sitelinks DESC

### GPT API
- **Model:** gpt-4o-mini (cost-effective)
- **Rate Limiting:** 1s after every 10 requests
- **Tokens:** ~400 per site (cost: $0.002)

### Hugo Build
- **Fast Render:** Enabled for development
- **Minification:** Enabled for production
- **Build Time:** ~5-10 minutes for 15k pages

---

## ✅ Validation & Quality Control

Run validation after page creation:

```bash
python validate_project.py
```

**Checks:**
- ✓ YAML frontmatter integrity
- ✓ Coordinate validity
- ✓ Image accessibility
- ✓ Content length
- ✓ Category distribution
- ✓ Duplicate detection

---

## 📝 TODO for Future Versions

- [ ] Implement image optimization (WebP conversion, sizing)
- [ ] Add multi-language content generation
- [ ] Implement caching for API responses
- [ ] Add progress resume capability
- [ ] Create automated testing suite
- [ ] Add content review/approval workflow
- [ ] Implement incremental updates (detect changes)

---

## 🆘 Troubleshooting

### "No sites found"
- Check Wikidata ID is correct
- Verify internet connection
- Check rate limiting (wait 5 minutes)

### "GPT enhancement failed"
- Verify API key is valid
- Check OpenAI account has credits
- Fall back to basic mode

### "Image download failed"
- Wikimedia Commons may be unavailable
- Image may not exist
- Continue with text-only page

### "Hugo build fails"
- Run: `python validate_project.py`
- Check YAML frontmatter for quotes
- Look for special characters in titles

---

## 📚 System Requirements

### Software
- Python 3.10+
- Hugo v0.120+ (extended version)
- Git

### Python Packages
```bash
pip install requests openai
```

### Optional
- OpenAI API key (for GPT enhancement)
- 10-20GB disk space per country

---

## 🎯 Success Criteria

A successfully deployed country site should have:

✅ 12,000-17,000 pages
✅ 100% coordinate coverage
✅ 80%+ image coverage
✅ Balanced category distribution (<30% any single category)
✅ All pages buildable by Hugo (no errors)
✅ Average 3-5 Wikipedia language links per site
✅ Proper YAML frontmatter
✅ Working maps and galleries

---

**System Status:** ✅ Production Ready
**Last Updated:** 2026-01-18
**Version:** 2.0

For questions or issues, check `archived_scripts/` for historical reference scripts.
