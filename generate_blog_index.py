"""Generate /blog/ index page listing all published articles."""

import re
from pathlib import Path

SITE_URL = "https://mathsolver.cloud"
STATIC = Path("static")
BLOG_DIR = STATIC / "blog"


def extract_meta(html):
    """Extract title and description from article HTML."""
    title_m = re.search(r"<title>(.*?)</title>", html)
    desc_m = re.search(r'<meta name="description" content="(.*?)"', html)
    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    return {
        "title": h1_m.group(1).strip() if h1_m else (title_m.group(1) if title_m else ""),
        "description": desc_m.group(1) if desc_m else "",
    }


def main():
    articles = []
    if BLOG_DIR.exists():
        for p in sorted(BLOG_DIR.iterdir()):
            if p.is_dir() and (p / "index.html").exists():
                html = (p / "index.html").read_text()
                meta = extract_meta(html)
                articles.append({
                    "slug": p.name,
                    "title": meta["title"],
                    "description": meta["description"],
                })

    cards = ""
    for a in articles:
        cards += f"""
      <a href="/blog/{a['slug']}/" class="blog-card">
        <h3>{a['title']}</h3>
        <p>{a['description']}</p>
        <span class="read-more">Read guide &rarr;</span>
      </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Math Guides &amp; Tutorials — MathSolver Blog</title>
  <meta name="description" content="Free step-by-step math guides, homework help, and tutorials. Browse all topics: algebra, calculus, geometry, statistics, and more.">
  <link rel="canonical" href="{SITE_URL}/blog/">
  <meta property="og:title" content="Math Guides & Tutorials — MathSolver Blog">
  <meta property="og:description" content="Free step-by-step math guides, homework help, and tutorials. Browse all topics: algebra, calculus, geometry, statistics, and more.">
  <meta property="og:url" content="{SITE_URL}/blog/">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{SITE_URL}/favicon.png">
  <meta property="og:site_name" content="MathSolver">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Math Guides & Tutorials — MathSolver Blog">
  <meta name="twitter:description" content="Free step-by-step math guides, homework help, and tutorials. Browse all topics: algebra, calculus, geometry, statistics, and more.">
  <meta name="twitter:image" content="{SITE_URL}/favicon.png">
  <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--blue:#2B7FE8;--yellow:#FFB800;--dark:#060D1F;--dark-2:#0D1B35;--white:#ffffff;--text:#d4dff5;--gray:#8a97b0;--border:rgba(43,127,232,0.15)}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--dark);color:var(--text);line-height:1.6}}
    header{{position:sticky;top:0;z-index:100;padding:0 40px;height:72px;display:flex;align-items:center;justify-content:space-between;background:rgba(6,13,31,0.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
    .logo{{font-size:1.3rem;font-weight:800;color:var(--white);text-decoration:none;display:flex;align-items:center;gap:10px}}
    .logo-icon{{width:34px;height:34px;background:linear-gradient(135deg,var(--blue),var(--yellow));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}}
    nav a{{color:var(--gray);text-decoration:none;font-size:0.875rem;padding:8px 14px;border-radius:8px;transition:color 0.2s}}
    nav a:hover,nav a.active{{color:var(--white);background:rgba(255,255,255,0.06)}}
    .btn-contact{{margin-left:12px;background:var(--yellow)!important;color:var(--dark)!important;font-weight:600!important;padding:9px 20px!important;border-radius:50px!important}}
    .page-hero{{padding:120px 40px 60px;text-align:center}}
    .page-hero h1{{font-size:clamp(2rem,4vw,3rem);font-weight:800;color:var(--white);margin-bottom:16px}}
    .page-hero p{{font-size:1.1rem;color:var(--gray);max-width:600px;margin:0 auto}}
    .blog-grid{{max-width:900px;margin:0 auto;padding:0 40px 80px;display:grid;gap:20px}}
    .blog-card{{display:block;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:16px;padding:28px;text-decoration:none;transition:transform 0.2s,border-color 0.2s}}
    .blog-card:hover{{transform:translateY(-2px);border-color:var(--blue)}}
    .blog-card h3{{font-size:1.15rem;font-weight:700;color:var(--white);margin-bottom:8px}}
    .blog-card p{{font-size:0.9rem;color:var(--gray);margin-bottom:12px;line-height:1.5}}
    .read-more{{font-size:0.85rem;color:var(--blue);font-weight:600}}
    footer{{text-align:center;padding:40px;border-top:1px solid var(--border);color:var(--gray);font-size:0.85rem}}
    footer a{{color:var(--gray);text-decoration:none;margin:0 12px}}
    footer a:hover{{color:var(--white)}}
    .hamburger{{display:none}}
    @media(max-width:768px){{
      header{{padding:0 20px}}
      .page-hero,.blog-grid{{padding-left:20px;padding-right:20px}}
    }}
  </style>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-5DLHQQDXLW"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-5DLHQQDXLW");</script>
</head>
<body>
  <header>
    <a href="/" class="logo"><span class="logo-icon">&Sigma;</span>MathSolver</a>
    <nav>
      <a href="/">Home</a>
      <a href="/blog/" class="active">Blog</a>
      <a href="/price/">Price</a>
      <a href="/#contactus" class="btn-contact">Contact US</a>
    </nav>
  </header>

  <div class="page-hero">
    <h1>Math Guides &amp; Tutorials</h1>
    <p>Free step-by-step solutions, homework help, and expert tips for every math topic.</p>
  </div>

  <div class="blog-grid">
    {cards}
  </div>

  <footer>
    <a href="/">Home</a>
    <a href="/privacy-policy/">Privacy</a>
    <a href="/terms-of-service/">Terms</a>
    <a href="/price/">Price</a>
    <div style="margin-top:16px">Copyright &copy; 2024 &ldquo;MARGOAPPS&rdquo; LLC</div>
  </footer>
</body>
</html>"""

    out = BLOG_DIR / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Blog index generated: {len(articles)} articles")


if __name__ == "__main__":
    main()
