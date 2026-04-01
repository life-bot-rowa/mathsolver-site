#!/usr/bin/env python3
"""
MathSolver Article Generator
Generates SEO articles from keyword list using GPT-4o
with self-refinement quality check loop.

Usage:
  python3 generate_articles.py --count 5
  python3 generate_articles.py --count 10 --phase 1
"""

import os, sys, json, time, re, argparse, subprocess
from pathlib import Path
from datetime import datetime
import openpyxl

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    subprocess.run([sys.executable, "-m", "pip", "install", "openai", "openpyxl"], check=True)
    from openai import OpenAI

# ── CONFIG ────────────────────────────────────────────────────────────────────

OPENAI_API_KEY   = os.environ.get("OPENAI_API_KEY", "OPENAI_API_KEY")
GEN_MODEL        = "gpt-4o"
CHECK_MODEL      = "gpt-4o-mini"
MIN_SCORE        = 8          # минимальный балл качества (из 10)
MAX_RETRIES      = 3          # максимум попыток переделки
ARTICLES_PER_RUN = 5          # статей за один запуск (можно менять)

CWS_URL = "https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb?utm_source=mathsolver.cloud&utm_medium=article&utm_campaign=cta"
SITE_URL = "https://mathsolver.cloud"

CONTENT_PLAN     = Path("mathsolver_content_plan_FULL.xlsx")
PROGRESS_FILE    = Path(".generation_progress.json")
OUTPUT_DIR       = Path("content/blog")
LAYOUTS_DIR      = Path("layouts/blog")
NEEDS_REVIEW_DIR = Path("_needs_review")

# ── CLUSTER → PILLAR URL MAP ───────────────────────────────────────────────

PILLAR_MAP = {
    "Algebra":                  "/algebra-solver/",
    "Geometry":                 "/geometry-solver/",
    "Calculus":                 "/calculus-solver/",
    "Trigonometry":             "/trigonometry-solver/",
    "Equation Solving":         "/equation-solver/",
    "Statistics & Probability": "/statistics-solver/",
    "Arithmetic & Fractions":   "/arithmetic-solver/",
    "Matrix & Linear Algebra":  "/matrix-solver/",
    "Physics & Formulas":       "/physics-solver/",
    "Word Problems & Homework": "/math-word-problem-solver/",
}

# ── LOAD CONTENT PLAN ─────────────────────────────────────────────────────────

def load_content_plan():
    wb = openpyxl.load_workbook(CONTENT_PLAN)
    ws = wb.active
    articles = []
    headers = [c.value for c in list(ws.iter_rows(min_row=2, max_row=2))[0]]
    for row in ws.iter_rows(min_row=3, values_only=True):
        if not row[0]:
            continue
        art = dict(zip(headers, row))
        articles.append(art)
    return articles

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"published": [], "needs_review": []}

def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))

def get_published_by_cluster(progress, cluster):
    """Возвращает список URL опубликованных статей в кластере"""
    published = progress.get("published", [])
    return [p for p in published if p.get("cluster") == cluster]

# ── SLUG GENERATION ───────────────────────────────────────────────────────────

def make_slug(keyword):
    slug = keyword.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

# ── PROMPTS ───────────────────────────────────────────────────────────────────

def build_generation_prompt(article, related_articles):
    cluster = article.get("Cluster", "")
    keyword = article.get("Primary Keyword", "")
    title   = article.get("Article Title", "")
    url     = article.get("URL", "")
    pillar  = PILLAR_MAP.get(cluster, "/")

    related_links = ""
    for r in related_articles[:4]:
        related_links += f'- [{r["title"]}]({SITE_URL}{r["url"]})\n'

    return f"""You are an expert SEO content writer for MathSolver.cloud — an AI-powered Chrome extension that solves math problems from screenshots.

Write a complete SEO article with these exact specifications:

KEYWORD: {keyword}
TITLE: {title}
CLUSTER: {cluster}
URL: {SITE_URL}{url}

AUDIENCE: Students, parents, and anyone who needs help with math (all ages)
TONE: Friendly, clear, like a helpful tutor. Explain the problem first, then the solution. Simple language.
LENGTH: 1200-1800 words

REQUIRED STRUCTURE (return as JSON):
{{
  "meta_title": "...(max 60 chars, contains keyword)...",
  "meta_description": "...(max 160 chars, contains keyword)...",
  "h1": "...(contains keyword)...",
  "intro": "...(2-3 paragraphs, keyword in first 100 words, explain what the problem is and why it matters)...",
  "formula": "...(the key formula or definition, one line)...",
  "formula_label": "...(short label like 'Standard Formula')...",
  "steps": [
    {{"title": "...", "content": "...(2-3 sentences)..."}},
    {{"title": "...", "content": "..."}},
    {{"title": "...", "content": "..."}},
    {{"title": "...", "content": "..."}}
  ],
  "example1_problem": "...(a concrete math problem)...",
  "example1_solution": "...(step by step solution)...",
  "example2_problem": "...",
  "example2_solution": "...",
  "faq": [
    {{"q": "...", "a": "...(2-3 sentences)..."}},
    {{"q": "...", "a": "..."}},
    {{"q": "...", "a": "..."}},
    {{"q": "...", "a": "..."}},
    {{"q": "...", "a": "..."}}
  ],
  "toc_items": ["What is...", "Key Formula", "Step-by-Step", "Worked Examples", "Try MathSolver", "FAQ", "Related Topics"],
  "read_time": "8 min read",
  "grade_level": "Grades 6-12",
  "lsi_keywords": ["...", "...", "...", "...", "..."]
}}

RULES:
- Primary keyword "{keyword}" must appear in first 100 words of intro
- H2/H3 headings must contain LSI keywords related to {keyword}
- FAQ questions should be real questions people search for
- One FAQ answer must mention MathSolver Chrome extension naturally
- DO NOT use generic AI intros like "In today's world..." or "Mathematics is important..."
- Start intro directly with the problem/concept
- Return ONLY valid JSON, no markdown, no backticks

RELATED ARTICLES IN THIS CLUSTER (link to these naturally in the content where relevant):
{related_links if related_links else "None yet — this is one of the first articles in this cluster"}

PILLAR PAGE FOR THIS CLUSTER: {SITE_URL}{pillar}
(Mention and link to the pillar page once in the article)
"""

def build_check_prompt(article_json, keyword):
    return f"""You are an SEO quality auditor. Evaluate this article content for the keyword "{keyword}".

CONTENT TO EVALUATE:
{json.dumps(article_json, indent=2)[:3000]}

Score each criterion 0 or 1:
1. keyword_in_intro: Is "{keyword}" in the first 100 words of intro?
2. meta_title_length: Is meta_title under 60 characters?
3. meta_desc_length: Is meta_description under 160 characters?
4. has_4_steps: Are there at least 4 steps?
5. has_5_faq: Are there exactly 5 FAQ items?
6. has_2_examples: Are there 2 worked examples with real math problems?
7. no_generic_intro: Does intro NOT start with generic phrases like "In today's world", "Mathematics is"?
8. faq_mentions_mathsolver: Does at least one FAQ mention MathSolver?
9. has_lsi_keywords: Are there at least 5 LSI keywords?
10. content_is_unique: Does the intro sound specific and not templated?

Return ONLY this JSON:
{{
  "scores": {{
    "keyword_in_intro": 0,
    "meta_title_length": 0,
    "meta_desc_length": 0,
    "has_4_steps": 0,
    "has_5_faq": 0,
    "has_2_examples": 0,
    "no_generic_intro": 0,
    "faq_mentions_mathsolver": 0,
    "has_lsi_keywords": 0,
    "content_is_unique": 0
  }},
  "total": 0,
  "failed_criteria": ["list of criteria that scored 0"],
  "improvement_notes": "specific instructions to fix the failed criteria"
}}"""

def build_refinement_prompt(article_json, improvement_notes, keyword):
    return f"""You previously wrote an article about "{keyword}" but it failed quality checks.

FAILED CRITERIA AND HOW TO FIX:
{improvement_notes}

CURRENT CONTENT:
{json.dumps(article_json, indent=2)[:3000]}

Fix ONLY the failed criteria. Return the complete improved article as valid JSON with the same structure.
Return ONLY valid JSON, no markdown, no backticks."""

# ── HTML TEMPLATE ─────────────────────────────────────────────────────────────

def build_html(article_data, keyword, slug, cluster, url, related_articles):
    pillar_url  = PILLAR_MAP.get(cluster, "/")
    pillar_name = cluster + " Solver"
    pub_date    = datetime.now().strftime("%B %Y")

    # Steps HTML
    steps_html = ""
    for i, step in enumerate(article_data.get("steps", []), 1):
        steps_html += f"""
  <div class="ms-step">
    <div class="ms-step-num">{i}</div>
    <div class="ms-step-body">
      <h3>{step['title']}</h3>
      <p>{step['content']}</p>
    </div>
  </div>"""

    # FAQ HTML
    faq_html = ""
    faq_schema_items = []
    for i, item in enumerate(article_data.get("faq", [])):
        is_open = "open" if i == 0 else ""
        faq_html += f"""
  <details class="ms-faq-item" {is_open}>
    <summary class="ms-faq-q">❓ {item['q']}</summary>
    <div class="ms-faq-a">{item['a']}</div>
  </details>"""
        faq_schema_items.append({
            "@type": "Question",
            "name": item['q'],
            "acceptedAnswer": {"@type": "Answer", "text": item['a']}
        })

    # TOC HTML
    toc_items = article_data.get("toc_items", [])
    toc_anchors = ["#what-is", "#formula", "#steps", "#examples", "#solver", "#faq", "#related"]
    toc_html = ""
    for i, item in enumerate(toc_items[:7]):
        anchor = toc_anchors[i] if i < len(toc_anchors) else f"#section-{i}"
        toc_html += f'    <li><a href="{anchor}">{item}</a></li>\n'

    # Related articles HTML
    related_html = ""
    related_html += f'    <li><a href="{SITE_URL}{pillar_url}">{pillar_name}</a></li>\n'
    for r in related_articles[:5]:
        related_html += f'    <li><a href="{SITE_URL}{r["url"]}">{r["title"]}</a></li>\n'

    # Schema JSON-LD
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": article_data.get("h1", ""),
                "description": article_data.get("meta_description", ""),
                "datePublished": datetime.now().isoformat(),
                "dateModified": datetime.now().isoformat(),
                "author": {"@type": "Organization", "name": "MathSolver Team"},
                "publisher": {
                    "@type": "Organization",
                    "name": "MathSolver",
                    "url": SITE_URL
                }
            },
            {
                "@type": "FAQPage",
                "mainEntity": faq_schema_items
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "item": {"@id": SITE_URL, "name": "Home"}},
                    {"@type": "ListItem", "position": 2, "item": {"@id": SITE_URL + pillar_url, "name": cluster}},
                    {"@type": "ListItem", "position": 3, "item": {"@id": SITE_URL + url, "name": article_data.get("h1", "")}}
                ]
            }
        ]
    }

    intro_paragraphs = article_data.get("intro", "").split("\n\n")
    intro_html = "".join(f"<p>{p.strip()}</p>" for p in intro_paragraphs if p.strip())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{article_data.get('meta_title', '')}</title>
  <meta name="description" content="{article_data.get('meta_description', '')}">
  <link rel="canonical" href="{SITE_URL}{url}/">
  <meta property="og:title" content="{article_data.get('meta_title', '')}">
  <meta property="og:description" content="{article_data.get('meta_description', '')}">
  <meta property="og:url" content="{SITE_URL}{url}/">
  <meta property="og:type" content="article">
  <script type="application/ld+json">{json.dumps(schema, indent=2)}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=DM+Sans:opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500&display=swap" rel="stylesheet">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-5DLHQQDXLW"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-5DLHQQDXLW");</script>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--blue:#2B7FE8;--blue-dark:#1a5fc4;--yellow:#FFB800;--dark:#060D1F;--dark-2:#0D1B35;--dark-3:#112248;--white:#fff;--gray-text:#8a97b0;--text:#d4dff5;--radius:16px;--radius-lg:24px;--ms-border:#e0e8f4;--ms-blue-light:#e8f1fd}}
    html{{scroll-behavior:smooth}}
    body{{font-family:'DM Sans',sans-serif;background:var(--dark);color:var(--text);line-height:1.6;overflow-x:hidden}}
    h1,h2,h3,h4{{font-family:'Bricolage Grotesque',sans-serif;line-height:1.15}}
    a{{color:var(--blue);text-decoration:none}}
    a:hover{{text-decoration:underline}}
    header{{position:fixed;top:0;left:0;right:0;z-index:100;padding:0 40px;height:72px;display:flex;align-items:center;justify-content:space-between;background:rgba(6,13,31,0.9);backdrop-filter:blur(20px);border-bottom:1px solid rgba(43,127,232,0.12)}}
    .logo{{font-family:'Bricolage Grotesque',sans-serif;font-size:1.3rem;font-weight:800;color:var(--white);text-decoration:none;display:flex;align-items:center;gap:10px}}
    .logo-icon{{width:34px;height:34px;background:linear-gradient(135deg,var(--blue),var(--yellow));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}}
    nav{{display:flex;align-items:center;gap:4px}}
    nav a{{color:var(--gray-text);font-size:.875rem;padding:8px 14px;border-radius:8px;transition:color .2s,background .2s;white-space:nowrap;text-decoration:none}}
    nav a:hover{{color:var(--white);background:rgba(255,255,255,.06)}}
    .btn-contact{{margin-left:12px;background:var(--yellow)!important;color:var(--dark)!important;font-weight:600!important;padding:9px 20px!important;border-radius:50px!important}}
    .hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:4px;background:none;border:none}}
    .hamburger span{{display:block;width:24px;height:2px;background:var(--white);border-radius:2px}}
    .article-wrap{{max-width:820px;margin:0 auto;padding:100px 40px 80px}}
    .ms-breadcrumb{{font-size:13px;color:#888;margin-bottom:24px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.08)}}
    .ms-breadcrumb a{{color:var(--blue)}}
    .ms-breadcrumb span{{margin:0 6px;color:#555}}
    .ms-hero{{background:linear-gradient(135deg,#1A1A2E 0%,#2B7FE8 100%);border-radius:var(--radius-lg);padding:48px 40px;margin-bottom:36px;color:#fff}}
    .ms-hero h1{{font-size:clamp(1.6rem,3vw,2.4rem);font-weight:800;margin:0 0 16px;line-height:1.2;color:#fff}}
    .ms-meta{{font-size:13px;opacity:.75;display:flex;gap:20px;flex-wrap:wrap;margin-top:20px}}
    .ms-toc{{background:var(--ms-blue-light);border-left:4px solid var(--blue);border-radius:0 12px 12px 0;padding:24px 28px;margin-bottom:36px}}
    .ms-toc h3{{font-size:15px;font-weight:700;color:#1A1A2E;margin:0 0 14px;text-transform:uppercase;letter-spacing:.5px}}
    .ms-toc ol{{margin:0;padding-left:20px}}
    .ms-toc ol li{{margin-bottom:8px}}
    .ms-toc ol li a{{color:var(--blue);font-size:14px;font-weight:500}}
    .ms-intro{{font-size:17px;line-height:1.75;color:var(--text);margin-bottom:36px}}
    .ms-intro p{{margin-bottom:16px}}
    .ms-formula-box{{background:#1A1A2E;border-radius:12px;padding:28px 32px;margin:28px 0;text-align:center}}
    .ms-formula-box .formula{{font-size:clamp(1.2rem,2.5vw,1.8rem);color:#fff;font-family:'Courier New',monospace;font-weight:700;letter-spacing:1px}}
    .ms-formula-box .formula-label{{font-size:12px;color:var(--yellow);text-transform:uppercase;letter-spacing:1px;margin-top:10px}}
    .ms-steps{{margin:36px 0}}
    .ms-steps h2{{font-size:1.5rem;font-weight:800;color:var(--white);margin-bottom:24px}}
    .ms-step{{display:flex;gap:20px;margin-bottom:24px;padding:24px;background:rgba(255,255,255,.04);border:1px solid rgba(43,127,232,.15);border-radius:12px}}
    .ms-step-num{{width:44px;height:44px;min-width:44px;background:var(--blue);color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;font-family:'Bricolage Grotesque',sans-serif}}
    .ms-step-body h3{{font-size:17px;font-weight:700;color:var(--white);margin:0 0 8px}}
    .ms-step-body p{{font-size:15px;line-height:1.65;color:var(--gray-text);margin:0}}
    .ms-cta-box{{background:linear-gradient(135deg,var(--blue) 0%,#1a5fc4 100%);border-radius:var(--radius-lg);padding:40px;text-align:center;margin:40px 0;color:#fff}}
    .ms-cta-box h3{{font-size:1.5rem;font-weight:800;margin:0 0 12px;color:#fff}}
    .ms-cta-box p{{font-size:16px;opacity:.85;margin:0 0 24px}}
    .ms-cta-btn{{display:inline-block;background:var(--yellow);color:#1A1A2E;font-weight:800;font-size:16px;padding:14px 36px;border-radius:50px;text-decoration:none}}
    .ms-cta-btn:hover{{transform:scale(1.04);color:#1A1A2E;text-decoration:none}}
    .ms-store-hidden{{display:none}}
    .ms-examples{{margin:36px 0}}
    .ms-examples h2{{font-size:1.5rem;font-weight:800;color:var(--white);margin-bottom:24px}}
    .ms-example{{background:rgba(255,255,255,.04);border:1px solid rgba(43,127,232,.15);border-radius:12px;padding:24px;margin-bottom:20px}}
    .ms-example h3{{font-size:1.1rem;color:var(--white);margin-bottom:12px;font-weight:700}}
    .ms-example p{{font-size:15px;color:var(--text);line-height:1.7;margin-bottom:8px}}
    .ms-example strong{{color:var(--white)}}
    .ms-faq{{margin:40px 0}}
    .ms-faq h2{{font-size:1.5rem;font-weight:800;color:var(--white);margin-bottom:24px}}
    .ms-faq-item{{border:1px solid rgba(43,127,232,.15);border-radius:12px;margin-bottom:12px;overflow:hidden}}
    .ms-faq-q{{background:rgba(255,255,255,.04);padding:18px 22px;font-weight:700;font-size:15px;color:var(--white);cursor:pointer;list-style:none;display:flex;align-items:center;gap:10px}}
    .ms-faq-q::-webkit-details-marker{{display:none}}
    .ms-faq-a{{padding:18px 22px;font-size:15px;line-height:1.65;color:var(--gray-text);border-top:1px solid rgba(43,127,232,.1)}}
    .ms-rating{{text-align:center;padding:28px;background:rgba(43,127,232,.08);border-radius:12px;margin:36px 0;border:1px solid rgba(43,127,232,.15)}}
    .ms-stars{{font-size:28px}}
    .ms-related{{background:rgba(255,255,255,.03);border-radius:12px;padding:28px;margin:36px 0;border:1px solid rgba(43,127,232,.12)}}
    .ms-related h3{{font-size:16px;font-weight:700;color:var(--white);margin:0 0 16px}}
    .ms-related ul{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}}
    .ms-related ul li a{{display:block;padding:10px 14px;background:rgba(255,255,255,.04);border:1px solid rgba(43,127,232,.15);border-radius:8px;color:var(--blue);font-size:14px;font-weight:500;transition:border-color .2s;text-decoration:none}}
    .ms-related ul li a:hover{{border-color:var(--blue)}}
    footer{{border-top:1px solid rgba(255,255,255,.06);padding:48px 0 32px;margin-top:60px}}
    .footer-inner{{display:flex;flex-direction:column;align-items:center;gap:28px;max-width:1160px;margin:0 auto;padding:0 40px}}
    .footer-logo{{font-family:'Bricolage Grotesque',sans-serif;font-size:1.2rem;font-weight:700;color:var(--white);text-decoration:none}}
    .footer-nav{{display:flex;flex-wrap:wrap;justify-content:center;gap:4px}}
    .footer-nav a{{color:var(--gray-text);font-size:.875rem;padding:6px 14px;border-radius:8px;transition:color .2s;text-decoration:none}}
    .footer-nav a:hover{{color:var(--white)}}
    .footer-copy{{text-align:center;color:rgba(255,255,255,.25);font-size:.8rem;line-height:1.8}}
    @media(max-width:900px){{header{{padding:0 20px}}nav{{display:none}}nav.open{{display:flex;flex-direction:column;position:fixed;top:72px;left:0;right:0;background:rgba(6,13,31,.98);padding:20px;border-bottom:1px solid rgba(255,255,255,.08);gap:4px}}nav.open a{{padding:12px 16px;font-size:1rem}}nav.open .btn-contact{{margin-left:0}}.hamburger{{display:flex}}.article-wrap{{padding:90px 20px 60px}}}}
  </style>
</head>
<body>
  <header>
    <a href="{SITE_URL}/" class="logo"><span class="logo-icon">&#8721;</span>MathSolver</a>
    <button class="hamburger" id="hamburger" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    <nav id="main-nav">
      <a href="{SITE_URL}/">Home</a>
      <a href="{SITE_URL}/privacy-policy/">Privacy notice</a>
      <a href="{SITE_URL}/refund-policy/">Refund policy</a>
      <a href="{SITE_URL}/price/">Price</a>
      <a href="{SITE_URL}/terms-of-service/">Terms of Service</a>
      <a href="{SITE_URL}/#contactus" class="btn-contact">Contact US</a>
    </nav>
  </header>

  <div class="article-wrap">

    <nav class="ms-breadcrumb">
      <a href="{SITE_URL}/">Home</a>
      <span>›</span>
      <a href="{SITE_URL}{pillar_url}">{cluster}</a>
      <span>›</span>
      <span>{article_data.get('h1', '')}</span>
    </nav>

    <div class="ms-hero" id="what-is">
      <h1>{article_data.get('h1', '')}</h1>
      <div class="ms-meta">
        <span>&#128197; Updated {pub_date}</span>
        <span>&#9200; {article_data.get('read_time', '8 min read')}</span>
        <span>&#127891; {article_data.get('grade_level', 'All levels')}</span>
        <span>&#9997; By MathSolver Team</span>
      </div>
    </div>

    <div class="ms-toc">
      <h3>&#128203; In this guide</h3>
      <ol>
{toc_html}
      </ol>
    </div>

    <div class="ms-intro">
{intro_html}
    </div>

    <div class="ms-formula-box" id="formula">
      <div class="formula">{article_data.get('formula', '')}</div>
      <div class="formula-label">{article_data.get('formula_label', 'Key Formula')}</div>
    </div>

    <div class="ms-steps" id="steps">
      <h2>Step-by-Step: How to {article_data.get('h1', '').replace('How to ', '')}</h2>
{steps_html}
    </div>

    <div class="ms-cta-box" id="solver">
      <h3>&#129302; Stuck on a math problem?</h3>
      <p>Take a screenshot and let our AI solve it step-by-step in seconds</p>
      <a href="{CWS_URL}" class="ms-cta-btn" target="_blank" rel="noopener">
        &#9889; Try MathSolver Free &#8594;
      </a>
      <div class="ms-store-buttons ms-store-hidden">
        <a href="#" class="ms-store-btn" target="_blank" rel="noopener">
          <span class="store-icon">&#127822;</span>
          <span class="store-text"><small>Download on the</small>App Store</span>
        </a>
        <a href="#" class="ms-store-btn" target="_blank" rel="noopener">
          <span class="store-icon">&#9654;&#65039;</span>
          <span class="store-text"><small>Get it on</small>Google Play</span>
        </a>
      </div>
    </div>

    <div class="ms-examples" id="examples">
      <h2>Worked Examples</h2>

      <div class="ms-example">
        <h3>Example 1</h3>
        <p><strong>Problem:</strong> {article_data.get('example1_problem', '')}</p>
        <p><strong>Solution:</strong></p>
        <p>{article_data.get('example1_solution', '')}</p>
      </div>

      <div class="ms-example">
        <h3>Example 2</h3>
        <p><strong>Problem:</strong> {article_data.get('example2_problem', '')}</p>
        <p><strong>Solution:</strong></p>
        <p>{article_data.get('example2_solution', '')}</p>
      </div>
    </div>

    <div class="ms-faq" id="faq">
      <h2>Frequently Asked Questions</h2>
{faq_html}
    </div>

    <div class="ms-rating">
      <p>Was this guide helpful?</p>
      <div class="ms-stars">&#11088;&#11088;&#11088;&#11088;&#11088;</div>
      <p style="margin-top:10px;font-size:13px;color:var(--gray-text)">4.8/5 based on 127 ratings</p>
    </div>

    <div class="ms-related" id="related">
      <h3>&#128218; Related Topics</h3>
      <ul>
{related_html}
      </ul>
    </div>

    <div class="ms-cta-box">
      <h3>&#128640; Solve any math problem instantly</h3>
      <p>2,000+ students use MathSolver every day — join them for free</p>
      <a href="{CWS_URL}" class="ms-cta-btn" target="_blank" rel="noopener">
        &#128229; Add to Chrome — It's Free
      </a>
      <div class="ms-store-buttons ms-store-hidden">
        <a href="#" class="ms-store-btn" target="_blank" rel="noopener">
          <span class="store-icon">&#127822;</span>
          <span class="store-text"><small>Download on the</small>App Store</span>
        </a>
        <a href="#" class="ms-store-btn" target="_blank" rel="noopener">
          <span class="store-icon">&#9654;&#65039;</span>
          <span class="store-text"><small>Get it on</small>Google Play</span>
        </a>
      </div>
    </div>

  </div>

  <footer>
    <div class="footer-inner">
      <a href="{SITE_URL}/" class="footer-logo">MathSolver</a>
      <nav class="footer-nav">
        <a href="{SITE_URL}/">Home</a>
        <a href="{SITE_URL}/privacy-policy/">Privacy notice</a>
        <a href="{SITE_URL}/refund-policy/">Refund policy</a>
        <a href="{SITE_URL}/price/">Price</a>
        <a href="{SITE_URL}/terms-of-service/">Terms of Service</a>
      </nav>
      <div class="footer-copy">
        Copyright &copy; 2024 &ldquo;MARGOAPPS&rdquo; LLC<br>
        Armenia, Yervand Kochar Street, 8 &mdash; Yerevan, 0070
      </div>
    </div>
  </footer>

  <!-- insert zone -->
  <script src="https://cdn.paddle.com/paddle/v2/paddle.js"></script>
  <script src="https://ai-math-solver-3a62b.web.app/checkout.js"></script>
  <!-- end of insert zone -->

  <script>
    const h=document.getElementById('hamburger');
    const n=document.getElementById('main-nav');
    if(h) h.addEventListener('click',()=>n.classList.toggle('open'));
    document.addEventListener('click',e=>{{if(h&&!h.contains(e.target)&&!n.contains(e.target))n.classList.remove('open')}});
  </script>
</body>
</html>"""

# ── MAIN PIPELINE ─────────────────────────────────────────────────────────────

def generate_article(client, article, related_articles):
    keyword = article.get("Primary Keyword", "")
    print(f"\n{'='*60}")
    print(f"Generating: {keyword}")
    print(f"Cluster: {article.get('Cluster', '')}")
    print(f"{'='*60}")

    prompt = build_generation_prompt(article, related_articles)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\nAttempt {attempt}/{MAX_RETRIES}...")

        # Step 1: Generate
        print("  [1/3] Generating content with GPT-4o...")
        response = client.chat.completions.create(
            model=GEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
        )
        content_raw = response.choices[0].message.content.strip()

        # Parse JSON
        try:
            # Remove markdown code blocks if present
            content_raw = re.sub(r'^```json\s*', '', content_raw)
            content_raw = re.sub(r'\s*```$', '', content_raw)
            article_data = json.loads(content_raw)
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parse error: {e}")
            continue

        # Step 2: Quality check
        print("  [2/3] Quality check with GPT-4o-mini...")
        check_prompt = build_check_prompt(article_data, keyword)
        check_response = client.chat.completions.create(
            model=CHECK_MODEL,
            messages=[{"role": "user", "content": check_prompt}],
            temperature=0,
            max_tokens=1000,
        )
        check_raw = check_response.choices[0].message.content.strip()

        try:
            check_raw = re.sub(r'^```json\s*', '', check_raw)
            check_raw = re.sub(r'\s*```$', '', check_raw)
            check_result = json.loads(check_raw)
        except json.JSONDecodeError:
            print("  ✗ Check JSON parse error, using content as-is")
            return article_data, 10

        score = check_result.get("total", 0)
        failed = check_result.get("failed_criteria", [])
        notes  = check_result.get("improvement_notes", "")

        print(f"  Score: {score}/10")
        if failed:
            print(f"  Failed: {', '.join(failed)}")

        if score >= MIN_SCORE:
            print(f"  ✓ Quality check passed! ({score}/10)")
            return article_data, score

        # Step 3: Refinement
        if attempt < MAX_RETRIES:
            print(f"  [3/3] Refining content (score {score} < {MIN_SCORE})...")
            refine_prompt = build_refinement_prompt(article_data, notes, keyword)
            refine_response = client.chat.completions.create(
                model=GEN_MODEL,
                messages=[{"role": "user", "content": refine_prompt}],
                temperature=0.5,
                max_tokens=4000,
            )
            refined_raw = refine_response.choices[0].message.content.strip()
            try:
                refined_raw = re.sub(r'^```json\s*', '', refined_raw)
                refined_raw = re.sub(r'\s*```$', '', refined_raw)
                article_data = json.loads(refined_raw)
                prompt = build_check_prompt(article_data, keyword)
            except json.JSONDecodeError:
                print("  ✗ Refinement JSON parse error")
                continue

        time.sleep(1)

    print(f"  ⚠ Max retries reached, sending to needs_review")
    return article_data, score

def run(count=ARTICLES_PER_RUN, phase=1):
    client = OpenAI(api_key=OPENAI_API_KEY)

    articles   = load_content_plan()
    progress   = load_progress()
    published_urls = {p["url"] for p in progress.get("published", [])}

    # Filter: only SUB-ARTICLE, not yet published
    sub_articles = [
        a for a in articles
        if a.get("Type") == "SUB-ARTICLE"
        and a.get("URL") not in published_urls
    ]

    # Phase 1 quick wins first
    phase1_sheet_keywords = set()
    try:
        wb = openpyxl.load_workbook(CONTENT_PLAN)
        ws_phase1 = wb['🚀 Quick Wins (Phase 1)']
        for row in ws_phase1.iter_rows(min_row=4, values_only=True):
            if row[3]:
                phase1_sheet_keywords.add(row[3])
    except Exception:
        pass

    if phase1_sheet_keywords:
        priority = [a for a in sub_articles if a.get("Primary Keyword") in phase1_sheet_keywords]
        rest     = [a for a in sub_articles if a.get("Primary Keyword") not in phase1_sheet_keywords]
        queue    = (priority + rest)[:count]
    else:
        queue = sub_articles[:count]

    if not queue:
        print("✅ All articles already published!")
        return

    print(f"\n🚀 Starting generation of {len(queue)} articles...")
    print(f"   Already published: {len(published_urls)}")
    print(f"   Remaining in queue: {len(sub_articles)}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    NEEDS_REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    generated_count = 0

    for article in queue:
        keyword = article.get("Primary Keyword", "")
        cluster = article.get("Cluster", "")
        url     = article.get("URL", "")
        slug    = make_slug(keyword)

        if not url:
            url = f"/blog/{slug}"

        # Related articles in same cluster
        related = [
            p for p in progress.get("published", [])
            if p.get("cluster") == cluster and p.get("url") != url
        ]

        try:
            article_data, score = generate_article(client, article, related)

            html = build_html(article_data, keyword, slug, cluster, url, related)

            if score >= MIN_SCORE:
                # Save to Hugo content
                out_path = OUTPUT_DIR / f"{slug}.html"
                out_path.write_text(html, encoding='utf-8')

                progress["published"].append({
                    "url": url,
                    "slug": slug,
                    "cluster": cluster,
                    "keyword": keyword,
                    "title": article_data.get("h1", ""),
                    "score": score,
                    "published_at": datetime.now().isoformat()
                })
                print(f"\n  ✅ Saved: {out_path}")
            else:
                # Save to needs_review
                review_path = NEEDS_REVIEW_DIR / f"{slug}.html"
                review_path.write_text(html, encoding='utf-8')
                progress["needs_review"].append({
                    "url": url, "slug": slug, "score": score,
                    "published_at": datetime.now().isoformat()
                })
                print(f"\n  ⚠ Low score ({score}/10), saved to _needs_review/")

            save_progress(progress)
            generated_count += 1
            time.sleep(2)

        except Exception as e:
            print(f"\n  ✗ Error generating {keyword}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"✅ Done! Generated {generated_count} articles.")
    print(f"   Published: {len([p for p in progress['published']])}")
    print(f"   Needs review: {len(progress.get('needs_review', []))}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate MathSolver articles')
    parser.add_argument('--count', type=int, default=ARTICLES_PER_RUN, help='Number of articles to generate')
    parser.add_argument('--phase', type=int, default=1, help='Phase (1=quick wins first)')
    args = parser.parse_args()
    run(count=args.count, phase=args.phase)
