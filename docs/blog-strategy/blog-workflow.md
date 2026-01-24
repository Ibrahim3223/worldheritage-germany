# Blog Content Creation Workflow

This document defines the step-by-step process for creating, reviewing, and publishing blog posts.

---

## Overview

**Purpose:** Ensure consistent quality, SEO optimization, and efficient production

**Team Roles:**
- **Content Creator:** Researches and writes posts (or AI-assisted)
- **Editor:** Reviews for quality, accuracy, SEO
- **Publisher:** Final checks and publication

**Timeline:** 3-5 days per post (research to publish)

---

## Phase 1: Planning & Research (Day 1)

### Step 1.1: Select Topic

**From:**
- Content calendar (planned topics)
- Keyword research (new opportunities)
- User requests/questions
- Trending topics in niche
- Content gaps identified

**Document:**
```
Topic: [Working title]
Content Type: [Ultimate Guide, Listicle, How-To, etc.]
Target Keyword: [Primary keyword]
Target Length: [Word count]
Author: [Assigned author]
Target Publish Date: [Date]
```

### Step 1.2: Keyword Research

**Tools:** Ahrefs, SEMrush, Google Keyword Planner

**Find:**
- Primary keyword (highest volume, rankable)
- Secondary keywords (3-5)
- Long-tail variations
- Related questions (People Also Ask)
- Search intent (informational, navigational, transactional)

**Document in Spreadsheet:**
| Keyword | Volume | Difficulty | Intent | Use |
|---------|--------|------------|--------|-----|
| german castles | 12,100 | 65 | Info | Primary |
| castles in germany | 8,100 | 60 | Info | Secondary |
| beautiful castles germany | 1,600 | 45 | Info | Secondary |

### Step 1.3: Competitor Analysis

**Research top 10 results for target keyword:**

**Analyze:**
- What do they cover? (topic breadth)
- How long are they? (word count)
- What's missing? (content gaps)
- What format? (list, guide, comparison)
- How many images? (visual richness)
- Internal links? (site structure)

**Our Advantage:**
- What can we do better?
- What unique value can we add?
- What insider knowledge do we have?

**Document:**
```
Top 3 Competitors:
1. [URL] - [Strengths] - [Weaknesses] - [Our advantage]
2. [URL] - [Strengths] - [Weaknesses] - [Our advantage]
3. [URL] - [Strengths] - [Weaknesses] - [Our advantage]

Our Unique Angle: [How we'll differentiate]
```

### Step 1.4: Content Outline

**Choose appropriate template** from `content-type-templates.md`

**Create detailed outline:**

```markdown
# [Working Title]

Target: [word count] words
Author: [name]
Category: [category]
Tags: [tag1, tag2, tag3]

## I. Introduction (300 words)
- Hook: [specific hook]
- What: [what post covers]
- Why: [why reader should care]
- Promise: [what they'll learn]

## II. [Section 1 Title] (400 words)
- Point A
- Point B
- Internal link: [site/post to link]
- Image needed: [description]

[Continue for all sections...]

## Checklist:
- [ ] 10+ internal links identified
- [ ] Image requirements noted
- [ ] FAQ questions listed (8-10)
- [ ] CTAs planned
```

**Review outline with stakeholder before writing**

---

## Phase 2: Content Creation (Days 2-3)

### Step 2.1: First Draft

**Writing Best Practices:**

**Structure:**
- Use outline as framework
- Write in assigned author's voice
- Front-load important information
- Use short paragraphs (2-4 sentences)
- Vary sentence length for readability

**SEO Integration:**
- Include primary keyword in first 100 words
- Use keyword variations in headers
- Write naturally (don't force keywords)
- Add internal links as you write
- Note where images needed

**Style:**
- Active voice preferred
- Present tense for immediacy
- Specific over generic
- Show, don't just tell
- Use examples and anecdotes

**Formatting:**
- H2 headers every 300-400 words
- H3 subheaders for subsections
- Bold key phrases sparingly
- Lists for scannable content
- Blockquotes for expert quotes

**Tools:**
- Grammarly (grammar/style checking)
- Hemingway App (readability)
- Google Docs (collaboration)
- Word counter

### Step 2.2: Add Internal Links

**While writing, add links for:**

**Heritage Sites (5-15 links):**
```markdown
[Cologne Cathedral](/sites/cologne-cathedral/) is Germany's most visited landmark...

For a fairy-tale experience, visit [Neuschwanstein Castle](/sites/neuschwanstein-castle/)...
```

**Related Blog Posts (2-5 links):**
```markdown
For photography tips, see our [castle photography guide](/blog/castle-photography/)...

Learn more in our [Gothic architecture guide](/blog/gothic-architecture/)...
```

**Category/Tag Pages (1-2 links):**
```markdown
Explore all [UNESCO sites in Germany](/tags/unesco/)...

Browse [castles by region](/regions/)...
```

**Best Practices:**
- Link naturally within sentences
- Use descriptive anchor text
- Distribute throughout post
- Don't link same page twice (unless far apart)
- Verify all links work

### Step 2.3: Write FAQ Section

**Source questions from:**
- Google's "People Also Ask"
- Related searches
- Competitor FAQs
- Common questions you've received
- Logical questions reader would have

**Format:**
```markdown
## Frequently Asked Questions

### Question in natural language?

Answer in 2-4 sentences with specific information. Include relevant
keyword naturally. Link to deeper resource if applicable.

### Second question?

[Answer]
```

**Aim for 6-10 FAQs**

### Step 2.4: Draft Conclusion

**Elements:**
- Summarize key points (2-3 sentences)
- Motivate action/inspire
- Provide next steps
- Include call to action

**Example:**
```markdown
## Conclusion

Germany's 50 most beautiful castles showcase the country's rich architectural
heritage, from medieval fortresses to romantic palaces. Whether you're drawn
to Ludwig II's fairy-tale creations or prefer ancient strongholds, each castle
tells a unique story of German history and culture.

Start planning your castle tour by [exploring our regional guides](/regions/)
or use our [trip planner](/trip-planner/) to create your perfect itinerary.
Which castle will you visit first?
```

---

## Phase 3: Enhancement (Day 3)

### Step 3.1: Source Images

**Requirements:**
- Minimum 1 image per major section
- Featured image (1920x1080px minimum)
- High quality, properly licensed

**Sources:**
- Wikimedia Commons (free, properly licensed)
- Own photos (if available)
- Unsplash/Pexels (free stock)
- Purchased stock (if budget allows)

**Naming Convention:**
```
[keyword]-[description]-[number].jpg

Examples:
cologne-cathedral-exterior-01.jpg
neuschwanstein-castle-winter-02.jpg
gothic-architecture-flying-buttress.jpg
```

**Optimization:**
1. Resize to maximum 1920px width
2. Convert to WebP format
3. Compress to under 200KB
4. Add descriptive alt text
5. Upload to `/static/images/blog/[post-slug]/`

### Step 3.2: Add Alt Text

**Format:** Descriptive sentence including keyword naturally

**Examples:**
```markdown
![Cologne Cathedral's twin Gothic spires dominating the Cologne skyline](/images/blog/castles/cologne-cathedral-exterior.webp)

![Neuschwanstein Castle perched on hilltop above Bavarian Alps in winter](/images/blog/castles/neuschwanstein-winter.webp)
```

**Requirements:**
- Descriptive (what's in image?)
- Natural keyword inclusion
- 10-15 words ideal
- Never empty

### Step 3.3: Create Visual Elements

**When appropriate, create:**

**Comparison Tables:**
```markdown
| Castle | Built | Style | Region | Visitors/Year |
|--------|-------|-------|--------|---------------|
| Neuschwanstein | 1869 | Romantic | Bavaria | 1.5M |
| Hohenzollern | 1850 | Neo-Gothic | Baden-W. | 350K |
```

**Infographics (future):**
- Timelines
- Maps with locations
- Step-by-step visuals
- Comparison charts

**Callout Boxes:**
```markdown
**Pro Tip:** Visit Neuschwanstein in winter for fewer crowds and a magical
snow-covered setting. The Marienbrücke viewpoint is accessible year-round.
```

---

## Phase 4: SEO Review (Day 4)

### Step 4.1: Title & Meta Check

**Title Optimization:**
- [ ] 50-60 characters
- [ ] Includes primary keyword
- [ ] Compelling/click-worthy
- [ ] Matches search intent

**Meta Description:**
- [ ] 150-160 characters
- [ ] Includes keyword naturally
- [ ] Has clear benefit/value
- [ ] Ends with CTA
- [ ] Compelling preview

**URL Slug:**
- [ ] 3-5 words
- [ ] Includes keyword
- [ ] Lowercase with hyphens
- [ ] No stop words

### Step 4.2: Content SEO Check

**Keyword Placement:**
- [ ] Primary keyword in first 100 words
- [ ] Keyword in at least one H2
- [ ] Keyword naturally throughout (1-2% density)
- [ ] Keyword in conclusion
- [ ] Secondary keywords in H2s

**Headers:**
- [ ] One H1 (title)
- [ ] 8-15 H2s with keyword variations
- [ ] H3s under H2s where needed
- [ ] Headers are descriptive
- [ ] Some headers are questions

**Content Quality:**
- [ ] Meets minimum word count for type
- [ ] Answers search intent completely
- [ ] Better than top 3 competitors
- [ ] No fluff or filler
- [ ] Specific and actionable

### Step 4.3: Link Check

**Internal Links:**
- [ ] Minimum 10 total internal links
- [ ] 5+ links to heritage sites
- [ ] 2-3 links to blog posts
- [ ] Varied anchor text
- [ ] Contextual (not forced)
- [ ] All links work (test each)

**External Links (if any):**
- [ ] Reputable sources only
- [ ] Opens in new tab
- [ ] No affiliate links without disclosure

### Step 4.4: Image SEO Check

**All Images:**
- [ ] Descriptive file names
- [ ] Alt text on every image
- [ ] Proper size (not oversized)
- [ ] WebP format
- [ ] Under 200KB each
- [ ] Lazy loading enabled

**Featured Image:**
- [ ] Compelling and relevant
- [ ] 1920x1080px minimum
- [ ] Properly optimized
- [ ] Has alt text

---

## Phase 5: Quality Review (Day 4)

### Step 5.1: Factual Accuracy

**Verify:**
- [ ] All dates correct
- [ ] All statistics sourced
- [ ] Historical facts accurate
- [ ] Visiting information current
- [ ] Prices/hours up to date
- [ ] Geographic information correct

**Sources:**
- Official site websites
- UNESCO documentation
- Academic sources
- Government tourism sites
- Recent travel guides

### Step 5.2: Grammar & Style

**Use Tools:**
- Grammarly (grammar, spelling, tone)
- Hemingway App (readability, grade level)
- ProWritingAid (style, repetition)

**Manual Check:**
- [ ] No typos or spelling errors
- [ ] Consistent voice (matches author)
- [ ] Proper punctuation
- [ ] No awkward phrasing
- [ ] Active voice predominates
- [ ] Varied sentence structure

**Readability:**
- Target: 8th-10th grade reading level
- Short paragraphs (2-4 sentences)
- Varied sentence length
- Subheaders for scanning

### Step 5.3: Author Voice Check

**Verify voice matches assigned author:**

**Dr. Sophia Weber:**
- Academic but accessible
- Conservation focus
- Expert terminology (explained)
- "From a heritage perspective..."

**Max Fischer:**
- Friendly and conversational
- Personal anecdotes
- Practical focus
- "I've visited 12 times and..."

**Anna Hoffmann:**
- Technical but not dry
- Visual focus
- Specific camera advice
- "The light at golden hour..."

**Prof. Martin Schmidt:**
- Scholarly and detailed
- Historical narratives
- Dates and context
- "In the 13th century..."

---

## Phase 6: Pre-Publish (Day 5)

### Step 6.1: Format for Hugo

**Front Matter:**
```yaml
---
title: "[Optimized Title]"
description: "[Meta description]"
date: 2026-01-12
author: [author-slug]
blog_category: "[Category]"
tags: ["[Tag1]", "[Tag2]", "[Tag3]", "[Tag4]", "[Tag5]"]
featured_image: "/images/blog/[post-slug]/featured.webp"
excerpt: "[2-3 sentence excerpt for cards]"
featured: false  # or true if featured post
toc: true  # enable table of contents
---
```

**File Organization:**
```
content/blog/[post-slug].md
static/images/blog/[post-slug]/
├── featured.webp
├── image-01.webp
├── image-02.webp
└── [etc.]
```

### Step 6.2: Preview & Test

**Local Testing:**
1. Run Hugo locally: `hugo server -D`
2. Navigate to post: `http://localhost:1313/blog/[post-slug]/`
3. Test all internal links (click each)
4. Check image loading
5. Verify mobile responsiveness
6. Test table of contents
7. Check layout on different screen sizes

**Test Checklist:**
- [ ] Post displays correctly
- [ ] Featured image shows
- [ ] All images load
- [ ] All internal links work
- [ ] TOC generates properly
- [ ] Mobile looks good
- [ ] No layout breaks
- [ ] Author info displays
- [ ] Related posts show (if applicable)

### Step 6.3: Final SEO Check

**Run Through:**
- Google Mobile-Friendly Test
- PageSpeed Insights
- SEO checker (Yoast, Rank Math equivalent)

**Verify:**
- [ ] Lighthouse SEO score 90+
- [ ] Mobile-friendly
- [ ] Page speed under 3 seconds
- [ ] No console errors
- [ ] Schema markup valid

---

## Phase 7: Publication (Day 5)

### Step 7.1: Publish

**In Hugo:**
1. Set correct publish date (future for scheduled)
2. Remove draft status if present
3. Commit to repository
4. Deploy to production

**Git Workflow:**
```bash
git add content/blog/[post-slug].md
git add static/images/blog/[post-slug]/
git commit -m "Add blog post: [Title]"
git push origin main
```

### Step 7.2: Immediate Post-Publication

**Within 1 hour:**
- [ ] Verify post live at correct URL
- [ ] Test all links on live site
- [ ] Submit URL to Google Search Console
- [ ] Share on social media (if strategy exists)
- [ ] Add to email newsletter (if applicable)
- [ ] Update content calendar (mark published)

**Update Related Content:**
- [ ] Add links from older relevant posts to new post
- [ ] Update any lists that should include this post
- [ ] Link from relevant heritage site pages (if applicable)

---

## Phase 8: Post-Publication (Ongoing)

### Day 7: Initial Metrics Check

**Monitor:**
- Indexing status (Google Search Console)
- Initial traffic (Google Analytics)
- Any errors or issues
- User feedback/comments

### Week 2-4: Performance Tracking

**Track:**
- Organic traffic
- Keyword rankings
- Internal link clicks
- Time on page
- Bounce rate
- Social shares

### Month 1-3: Optimization

**Based on data:**
- Improve low-performing elements
- Add more content if thin
- Improve images if engagement low
- Update title/description if CTR low
- Build more backlinks

### Annual Review

**Every 12 months:**
- Update statistics and dates
- Refresh any outdated information
- Add new sections if topic evolved
- Improve images if better available
- Update lastmod date in front matter
- Resubmit to search engines

---

## Quick Reference Checklist

### Before Writing
- [ ] Keyword research complete
- [ ] Competitors analyzed
- [ ] Detailed outline created
- [ ] Content type selected
- [ ] Author voice determined

### During Writing
- [ ] Following outline
- [ ] Using author's voice
- [ ] Adding internal links
- [ ] Noting image needs
- [ ] Meeting word count

### Before Publishing
- [ ] Title optimized (50-60 chars)
- [ ] Meta description optimized (150-160 chars)
- [ ] URL slug optimized
- [ ] 10+ internal links
- [ ] All images optimized with alt text
- [ ] FAQ section included
- [ ] Factually accurate
- [ ] Grammar checked
- [ ] Mobile tested
- [ ] All links work

### After Publishing
- [ ] Live URL verified
- [ ] Submitted to Search Console
- [ ] Social media shared
- [ ] Content calendar updated
- [ ] Related posts updated

---

## Tools & Resources

**Writing:**
- Google Docs (drafting, collaboration)
- Grammarly (grammar, style)
- Hemingway App (readability)
- Word counter

**SEO:**
- Ahrefs/SEMrush (keyword research)
- Google Search Console (indexing, performance)
- Google PageSpeed Insights (speed)
- Lighthouse (SEO audit)

**Images:**
- Squoosh (compression)
- Photopea (editing, free Photoshop alternative)
- TinyPNG (compression)
- CloudConvert (WebP conversion)

**Testing:**
- Hugo local server
- BrowserStack (cross-browser testing)
- Google Mobile-Friendly Test

---

**Last Updated:** January 2026
**Owner:** Content Team
**Review Frequency:** Quarterly
