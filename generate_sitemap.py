"""Generate sitemap.xml including all static pages, pillar pages, and blog articles."""

from pathlib import Path
from datetime import datetime

SITE_URL = "https://mathsolver.cloud"
STATIC_DIR = Path("static")
PUBLIC_DIR = Path("public")

# Pages to exclude from sitemap
EXCLUDE = {"welcome", "mathsolver_solution_images", "favicon.ico", "favicon.png"}


def get_pages():
    """Collect all pages for the sitemap."""
    pages = []
    today = datetime.now().strftime("%Y-%m-%d")

    # Homepage
    pages.append({"url": f"{SITE_URL}/", "priority": "1.0", "changefreq": "daily"})

    # Pillar pages (static/*/index.html)
    for p in sorted(STATIC_DIR.iterdir()):
        if p.is_dir() and p.name not in EXCLUDE and (p / "index.html").exists():
            if p.name == "blog":
                continue  # blog articles handled separately
            pages.append({
                "url": f"{SITE_URL}/{p.name}/",
                "priority": "0.8",
                "changefreq": "weekly",
            })

    # Blog articles (static/blog/*/index.html)
    blog_dir = STATIC_DIR / "blog"
    if blog_dir.exists():
        for p in sorted(blog_dir.iterdir()):
            if p.is_dir() and (p / "index.html").exists():
                pages.append({
                    "url": f"{SITE_URL}/blog/{p.name}/",
                    "priority": "0.6",
                    "changefreq": "monthly",
                })

    # Static content pages (exclude noindex pages)
    for name in ["price", "access"]:
        pages.append({
            "url": f"{SITE_URL}/{name}/",
            "priority": "0.3",
            "changefreq": "monthly",
        })
    # privacy-policy, refund-policy, terms-of-service have noindex — not in sitemap

    return pages, today


def build_sitemap(pages, lastmod):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{p['url']}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{p['changefreq']}</changefreq>")
        lines.append(f"    <priority>{p['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    pages, today = get_pages()
    sitemap = build_sitemap(pages, today)

    # Write to both static and public so it's available everywhere
    (STATIC_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    PUBLIC_DIR.mkdir(exist_ok=True)
    (PUBLIC_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print(f"Sitemap generated: {len(pages)} URLs")


if __name__ == "__main__":
    main()
