# WorldHeritage.guide - Germany

Premium heritage travel guide platform - Germany edition.

## Project Status
🚧 **Phase 1**: Foundation + Wikidata Fetch

## Structure
- `scripts/`: Python automation scripts
- `data/`: Data storage (gitignored)
- `content/`: Hugo content (generated)
- `layouts/`: Hugo templates (coming in Phase 5)
- `static/`: Static assets (coming in Phase 5)

## Setup

### 1. Install Dependencies
```bash
cd scripts
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Scripts
```bash
# Phase 1: Fetch Wikidata
python scripts/1_fetch_wikidata.py
```

## Phase Progress
- [x] Phase 1: Foundation + Wikidata
- [ ] Phase 2: Image Pipeline
- [ ] Phase 3: Content Generation
- [ ] Phase 4: Quality Control
- [ ] Phase 5: Hugo Templates
- [ ] Phase 6: Deploy

## License
Private - All Rights Reserved
