# WorldHeritage.guide - Germany

> Premium heritage travel guide platform powered by AI-generated content and Wikidata.

[![Hugo](https://img.shields.io/badge/Hugo-0.152.2-blue.svg)](https://gohugo.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.x-38B2AC.svg)](https://tailwindcss.com/)
[![Cloudflare](https://img.shields.io/badge/Deploy-Cloudflare%20Pages-F38020.svg)](https://pages.cloudflare.com/)

## 🌟 Features

- **5,800+ Heritage Sites**: Comprehensive coverage of German cultural and natural heritage
- **AI-Generated Content**: High-quality articles powered by GPT-4o-mini
- **Wikidata Integration**: Structured data from 60+ heritage categories
- **Cloudflare R2 CDN**: Optimized image delivery from R2 object storage
- **Fast & SEO-Optimized**: Hugo static site with perfect Lighthouse scores

## 🚀 Quick Start

### Prerequisites

- **Hugo Extended** 0.152.2+ ([Download](https://gohugo.io/installation/))
- **Node.js** 16+ & npm
- **Python** 3.9+

### Installation

```bash
# Clone the repository
git clone https://github.com/Ibrahim3223/worldheritage-germany.git
cd worldheritage-germany

# Install dependencies
npm install
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys (OpenAI, Mapbox, Cloudflare R2)
```

### Development

```bash
# Start Hugo development server
npm run dev

# Visit http://localhost:1313
```

### Content Generation Pipeline

Generate content for new sites:

```bash
# 1. Fetch heritage sites from Wikidata
npm run fetch:wikidata

# 2. Download images from Wikimedia Commons
npm run fetch:images

# 3. Generate AI content (GPT-4o-mini)
npm run generate:content

# 4. Upload images to Cloudflare R2
npm run upload:images

# Or run the entire pipeline:
npm run pipeline:full
```

## 📁 Project Structure

```
worldheritage-germany/
├── content/           # Hugo content (5,856 site pages)
│   ├── sites/        # Heritage site pages
│   └── blog/         # Blog posts
├── data/             # Wikidata JSON files
├── layouts/          # Hugo templates
├── static/           # Static assets
├── scripts/          # Content generation pipeline
│   ├── 0_define_categories.py
│   ├── 1_fetch_wikidata.py
│   ├── 2_fetch_images.py
│   ├── 2b_optimize_images.py
│   ├── 3_generate_content.py
│   ├── 4_upload_to_r2.py
│   ├── config.py
│   └── utils/
├── docs/             # Documentation
└── config.toml       # Hugo configuration
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Master System](docs/README_MASTER_SYSTEM.md)
- [Blog Strategy](docs/blog-strategy/)

## 🚢 Deployment

### Cloudflare Pages

The site is automatically deployed to Cloudflare Pages:

**Build Settings:**
- **Build command**: `hugo --minify`
- **Build output**: `public`
- **Environment variables**:
  - `HUGO_VERSION = 0.152.2`

**Custom Domain**: Configure your domain in Cloudflare Pages settings.

### Image CDN

Images are served from Cloudflare R2:
- **Bucket**: `worldheritage-germany-images`
- **Public URL**: `https://pub-2acbb9b7266b4170a5ab3498a8936037.r2.dev`
- **Storage**: ~1.3 GB (17,600+ optimized WebP images)

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# OpenAI API (for content generation)
OPENAI_API_KEY=your_key

# Mapbox (for satellite imagery)
MAPBOX_TOKEN=your_token

# Cloudflare R2 (for image hosting)
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=worldheritage-germany-images
```

### Hugo Config

Edit `config.toml` to customize:
- `baseURL`: Your production URL
- `params.imageBaseURL`: R2 CDN URL for images
- SEO metadata
- Analytics

## 📊 Content Stats

- **Total Sites**: 5,856
- **Categories**: 62 (UNESCO sites, castles, churches, museums, etc.)
- **Data Source**: Wikidata SPARQL queries
- **Content Quality**: AI-generated with strict quality control
- **Images**: 1-3 images per site, optimized WebP format

## 🛠️ Tech Stack

- **Static Site Generator**: [Hugo](https://gohugo.io/)
- **CSS Framework**: [Tailwind CSS](https://tailwindcss.com/)
- **JavaScript**: Alpine.js for interactivity
- **Hosting**: [Cloudflare Pages](https://pages.cloudflare.com/)
- **CDN**: [Cloudflare R2](https://www.cloudflare.com/products/r2/)
- **Content Generation**: OpenAI GPT-4o-mini
- **Data Source**: [Wikidata](https://www.wikidata.org/)

## 📝 License

Private - All Rights Reserved

## 🤝 Contributing

This is a private project. For questions or collaboration opportunities, please contact the repository owner.

---

**Built with ❤️ using Claude Code**
