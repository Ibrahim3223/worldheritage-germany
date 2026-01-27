# Multi-Country Deployment Guide

This guide explains how to deploy WorldHeritage.guide for a new country based on the Germany template.

---

## 📋 Prerequisites

- Access to Cloudflare Pages
- Access to Cloudflare R2 (for images)
- Wikidata knowledge (for fetching heritage sites)
- OpenAI API key (for content generation)

---

## 🚀 Quick Start (30 minutes)

### 1. Clone Germany Repository

```bash
git clone https://github.com/yourusername/worldheritage-germany.git worldheritage-france
cd worldheritage-france
```

### 2. Update Country Configuration

Edit `config.toml`:

```toml
baseURL = "https://fr.worldheritage.guide/"  # Change country code
title = "WorldHeritage.guide - France | Comprehensive Heritage Travel Guide"

[params]
  country = "France"           # Full country name
  countryCode = "fr"           # ISO country code
  wikidataQID = "Q142"         # France's Wikidata QID

  description = "Discover France's rich cultural and natural heritage..."
  imageBaseURL = "https://pub-YOUR_R2_BUCKET.r2.dev"
```

### 3. Update Scripts Configuration

Create `scripts/country_config.py`:

```python
COUNTRY_CONFIG = {
    'name': 'France',
    'code': 'fr',
    'wikidata_qid': 'Q142',
    'language': 'en',
    'regions': [
        'Île-de-France',
        'Provence-Alpes-Côte d\'Azur',
        'Nouvelle-Aquitaine',
        'Occitanie',
        'Auvergne-Rhône-Alpes',
        'Grand Est',
        'Hauts-de-France',
        'Normandie',
        'Brittany',
        'Pays de la Loire',
        'Centre-Val de Loire',
        'Bourgogne-Franche-Comté',
        'Corsica'
    ],
    'unesco_count': 49,  # As of 2024
}
```

### 4. Clean Old Content

```bash
# Remove Germany content
rm -rf content/sites/*
rm -rf data/*

# Keep directory structure
mkdir -p content/sites
mkdir -p data/content_backup
```

### 5. Fetch New Country Data

```bash
# 1. Fetch Wikidata
python scripts/1_fetch_wikidata.py --country-qid Q142

# 2. Process and categorize
python scripts/2_process_wikidata.py

# 3. Generate content
python scripts/3_generate_content.py

# 4. Add images
python scripts/add_images_to_sites.py
```

### 6. Update Repository

```bash
git add .
git commit -m "feat: Initialize France deployment"
git remote set-url origin https://github.com/yourusername/worldheritage-france.git
git push -u origin main
```

### 7. Deploy to Cloudflare Pages

1. Go to Cloudflare Pages dashboard
2. Create new project: `worldheritage-france`
3. Connect to GitHub repository
4. Build settings:
   - Framework: Hugo
   - Build command: `hugo --minify`
   - Build output: `public`
   - Environment variables:
     ```
     HUGO_VERSION = 0.152.2
     NODE_VERSION = 18
     ```

5. Custom domain:
   - Add `fr.worldheritage.guide`
   - Configure DNS CNAME

---

## 📊 Country-Specific Data

### Supported Countries

| Country | Code | QID | UNESCO Sites | Status |
|---------|------|-----|--------------|--------|
| Germany | de | Q183 | 52 | ✅ Live |
| France | fr | Q142 | 49 | ⏳ Template Ready |
| Italy | it | Q38 | 58 | ⏳ Template Ready |
| Spain | es | Q29 | 50 | ⏳ Template Ready |
| UK | gb | Q145 | 33 | ⏳ Template Ready |

### Finding Country Information

#### Wikidata QID

Go to: https://www.wikidata.org/wiki/COUNTRY_NAME

Example: https://www.wikidata.org/wiki/Q142 (France)

#### ISO Country Code

See: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

#### UNESCO Site Count

See: https://whc.unesco.org/en/statesparties/

---

## 🔧 Advanced Configuration

### Custom Regions

Each country has different administrative divisions. Update in `scripts/country_config.py`:

**Germany (States):**
```python
regions = ['Bavaria', 'Berlin', 'Hamburg', ...]
```

**France (Regions):**
```python
regions = ['Île-de-France', 'Provence', ...]
```

**Italy (Regions):**
```python
regions = ['Lombardy', 'Tuscany', 'Lazio', ...]
```

### Wikidata Query Customization

Edit `scripts/1_fetch_wikidata.py`:

```python
# Query for heritage sites
query = f"""
SELECT DISTINCT ?item ?itemLabel ?itemDescription
       ?categoryLabel ?location ?coords
       ?image ?wikidataId
WHERE {{
  ?item wdt:P17 wd:{COUNTRY_QID} .  # Country

  # Include:
  # - UNESCO sites (P1435:Q9259)
  # - Monuments
  # - Museums
  # - Castles/Palaces
  # - Churches/Cathedrals
  # - Natural sites

  OPTIONAL {{ ?item wdt:P18 ?image }}
  OPTIONAL {{ ?item wdt:P625 ?coords }}

  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
}}
LIMIT 15000
"""
```

### Content Generation Prompts

Edit `scripts/3_generate_content.py` to customize for each country:

```python
# Germany-specific
prompt = f"Write about {site_name}, a {heritage_type} in Germany..."

# France-specific
prompt = f"Write about {site_name}, a {heritage_type} in France..."
```

### Layout Customization

Update `layouts/` files to use country parameter:

**Before:**
```html
<h1>Discover Germany's Heritage</h1>
```

**After:**
```html
<h1>Discover {{ .Site.Params.country }}'s Heritage</h1>
```

---

## 🖼️ Image Management

### Cloudflare R2 Setup

1. **Create R2 Bucket:**
   ```
   Name: worldheritage-france-images
   Public URL: https://pub-XXXXX.r2.dev
   ```

2. **Update config.toml:**
   ```toml
   imageBaseURL = "https://pub-XXXXX.r2.dev"
   ```

3. **Upload Images:**
   ```bash
   # Images are fetched from Wikimedia Commons
   # No upload needed - use direct URLs
   ```

### Image Strategy

- **Primary:** Wikimedia Commons URLs (no storage needed)
- **Backup:** R2 for custom images
- **Optimization:** Responsive srcsets generated automatically

---

## 🌐 Domain & DNS

### Subdomain Structure

```
de.worldheritage.guide  → Germany
fr.worldheritage.guide  → France
it.worldheritage.guide  → Italy
es.worldheritage.guide  → Spain
```

### Cloudflare DNS Setup

```
Type: CNAME
Name: fr
Target: worldheritage-france.pages.dev
Proxied: Yes (orange cloud)
```

---

## 📝 Content Pipeline

### Full Pipeline (Germany Example)

```bash
# Total time: ~8 hours for 10,000+ sites

# 1. Fetch from Wikidata (~5 min)
python scripts/1_fetch_wikidata.py --country-qid Q183

# 2. Process & categorize (~10 min)
python scripts/2_process_wikidata.py

# 3. Generate content with LLM (~6 hours)
python scripts/3_generate_content.py

# 4. Add images (~30 min)
python scripts/add_images_to_sites.py

# 5. Build Hugo site (~2 min)
hugo --minify

# 6. Deploy
git push origin main  # Auto-deploys to Cloudflare
```

### Cost Estimate (per country)

| Item | Cost |
|------|------|
| OpenAI API (content) | ~$150-200 |
| Cloudflare Pages | Free (up to 500 builds/month) |
| Cloudflare R2 | Free (up to 10GB) |
| Domain | $10/year (if new domain) |
| **Total** | ~$160-210 one-time |

---

## 🔍 Quality Assurance

### Pre-Launch Checklist

- [ ] Wikidata fetch successful (10,000+ sites)
- [ ] All regions represented
- [ ] UNESCO sites included
- [ ] Images added (>70%)
- [ ] Content generated (100%)
- [ ] Build succeeds without errors
- [ ] Lighthouse score >90
- [ ] Mobile responsive
- [ ] SEO meta tags correct
- [ ] Sitemap generated
- [ ] robots.txt configured

### Audit Scripts

```bash
# Data quality
python scripts/audit_simple.py

# Root cleanup
python scripts/audit_cleanup.py

# Config check
python scripts/audit_config.py
```

---

## 🐛 Common Issues

### Issue: Wikidata returns too few sites

**Solution:** Adjust query to include more categories

```sparql
# Add more P31 (instance of) values
?item wdt:P31 ?type .
VALUES ?type {
  wd:Q839954   # Archaeological site
  wd:Q570116   # Tourist attraction
  wd:Q23413    # Castle
  # Add more...
}
```

### Issue: Content generation too slow

**Solution:** Use parallel processing

```python
# Use ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(generate_content, sites)
```

### Issue: Build exceeds Cloudflare 20k file limit

**Solution:** Reduce output formats

```toml
[outputs]
  home = ["HTML"]       # Remove RSS
  section = ["HTML"]    # Remove JSON if not needed
  page = ["HTML"]
  taxonomy = ["HTML"]
```

---

## 📊 Analytics & Monitoring

### Google Analytics

Add to `config.toml`:

```toml
[params]
  googleAnalytics = "G-XXXXXXXXXX"
```

### Cloudflare Analytics

Built-in - check Cloudflare Pages dashboard

### Performance Monitoring

Use Lighthouse CI:

```bash
npm install -g @lhci/cli
lhci autorun --collect.url=https://fr.worldheritage.guide
```

---

## 🔄 Maintenance

### Monthly Tasks

- [ ] Check for new UNESCO sites
- [ ] Update site count in config
- [ ] Re-run image import for sites without images
- [ ] Review analytics for popular pages
- [ ] Update content for top 10 sites

### Quarterly Tasks

- [ ] Full Wikidata refresh
- [ ] Content quality audit
- [ ] SEO optimization review
- [ ] Performance audit
- [ ] Broken link check

---

## 📚 Resources

### Documentation

- Hugo: https://gohugo.io/documentation/
- Cloudflare Pages: https://developers.cloudflare.com/pages/
- Wikidata: https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial
- OpenAI API: https://platform.openai.com/docs

### Templates

- Config: `docs/config.template.toml`
- Country Config: `scripts/country_config_template.py`
- Deployment: This guide

### Support

- GitHub Issues: https://github.com/yourusername/worldheritage-germany/issues
- Email: support@worldheritage.guide

---

## ✅ Success Metrics

### Target Metrics (per country)

| Metric | Target | Germany (Actual) |
|--------|--------|------------------|
| Total Sites | 10,000+ | 10,173 ✅ |
| UNESCO Sites | Country total | 52 ✅ |
| Content Quality | 99%+ | 99.99% ✅ |
| Images Coverage | 70%+ | 79% ✅ |
| Build Time | <3 min | ~2 min ✅ |
| Lighthouse Score | >90 | 95+ ✅ |
| Page Load | <2s | ~1.2s ✅ |

---

## 🎯 Next Steps

1. Choose your country
2. Follow Quick Start guide
3. Run quality audits
4. Deploy to Cloudflare Pages
5. Monitor and iterate

**Happy deploying! 🚀**
