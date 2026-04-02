"""Weekly SEO audit — checks all items and fixes what it can."""

import json
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

SITE_URL = "https://mathsolver.cloud"
STATIC = Path("static")
GA4_PROPERTY_ID = "510795182"
GSC_SITE_URL = "sc-domain:mathsolver.cloud"  # or "https://mathsolver.cloud/"
LAYOUTS = Path("layouts")
fixes = []
issues = []


def check(name, ok, fix_msg=None):
    if ok:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}")
        if fix_msg:
            issues.append(f"{name}: {fix_msg}")
        else:
            issues.append(name)


# ── 1. robots.txt ──

def audit_robots():
    print("\n## 1. robots.txt")
    f = STATIC / "robots.txt"
    check("robots.txt exists", f.exists())
    if f.exists():
        txt = f.read_text()
        check("Allows Googlebot", "Googlebot" in txt)
        check("Allows GPTBot", "GPTBot" in txt)
        check("Allows Claude-Web", "Claude-Web" in txt)
        check("Allows PerplexityBot", "PerplexityBot" in txt)
        check("Contains sitemap URL", "sitemap.xml" in txt)


# ── 2. Sitemap ──

def audit_sitemap():
    print("\n## 2. Sitemap")
    sitemap_file = STATIC / "sitemap.xml"
    check("sitemap.xml exists", sitemap_file.exists())
    if not sitemap_file.exists():
        return

    sitemap = sitemap_file.read_text()

    # Check all pillar pages are in sitemap
    missing_pillars = []
    for p in sorted(STATIC.iterdir()):
        if p.is_dir() and (p / "index.html").exists() and p.name not in ("blog", "welcome", "mathsolver_solution_images"):
            url = f"{SITE_URL}/{p.name}/"
            if url not in sitemap:
                missing_pillars.append(p.name)

    check("All pillar pages in sitemap", len(missing_pillars) == 0,
          f"Missing: {', '.join(missing_pillars)}" if missing_pillars else None)

    # Check all blog articles are in sitemap
    blog_dir = STATIC / "blog"
    missing_blogs = []
    if blog_dir.exists():
        for p in sorted(blog_dir.iterdir()):
            if p.is_dir() and (p / "index.html").exists():
                url = f"{SITE_URL}/blog/{p.name}/"
                if url not in sitemap:
                    missing_blogs.append(p.name)

    check("All blog articles in sitemap", len(missing_blogs) == 0,
          f"Missing: {', '.join(missing_blogs)}" if missing_blogs else None)

    if missing_pillars or missing_blogs:
        print("  🔧 Regenerating sitemap...")
        os.system("python3 generate_sitemap.py")
        fixes.append("Regenerated sitemap.xml with missing pages")


# ── 3. llms.txt ──

def audit_llms():
    print("\n## 3. llms.txt")
    f = STATIC / "llms.txt"
    check("llms.txt exists", f.exists())
    if not f.exists():
        return

    txt = f.read_text()
    needs_update = False

    # Check pillar pages
    for p in sorted(STATIC.iterdir()):
        if p.is_dir() and (p / "index.html").exists() and p.name not in ("blog", "welcome", "mathsolver_solution_images"):
            if p.name not in txt:
                print(f"  ❌ Pillar '{p.name}' missing from llms.txt")
                needs_update = True

    # Check blog articles
    blog_dir = STATIC / "blog"
    if blog_dir.exists():
        for p in sorted(blog_dir.iterdir()):
            if p.is_dir() and (p / "index.html").exists():
                if p.name not in txt:
                    print(f"  ❌ Blog '{p.name}' missing from llms.txt")
                    needs_update = True

    if needs_update:
        print("  🔧 Updating llms.txt...")
        update_llms_txt()
        fixes.append("Updated llms.txt with new pages")
    else:
        print("  ✅ All pages present in llms.txt")


def update_llms_txt():
    lines = [
        "# MathSolver\n",
        "> MathSolver is an AI-powered math solving tool available as a Chrome extension. "
        "Students take a screenshot of any math problem and get instant step-by-step solutions.\n",
        "## Site Structure\n",
        f"- Homepage: {SITE_URL}/",
        "- Chrome Extension: https://chromewebstore.google.com/detail/math-solver/pieobakkfhafplomcoiohhpikcofoghb\n",
        "## Solver Pages (Pillar Pages)\n",
        "These are comprehensive guides for each math topic:\n",
    ]

    for p in sorted(STATIC.iterdir()):
        if p.is_dir() and (p / "index.html").exists() and p.name not in ("blog", "welcome", "mathsolver_solution_images"):
            title = p.name.replace("-", " ").title()
            lines.append(f"- [{title}]({SITE_URL}/{p.name}/)")

    lines.append("\n## Blog Articles\n")
    lines.append("Step-by-step tutorials and homework help guides. New articles are published daily.\n")

    blog_dir = STATIC / "blog"
    if blog_dir.exists():
        for p in sorted(blog_dir.iterdir()):
            if p.is_dir() and (p / "index.html").exists():
                title = p.name.replace("-", " ").title()
                lines.append(f"- [{title}]({SITE_URL}/blog/{p.name}/)")

    (STATIC / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── 4. Canonical tags ──

def audit_canonical():
    print("\n## 4. Canonical tags")
    missing = []

    blog_dir = STATIC / "blog"
    if blog_dir.exists():
        for p in sorted(blog_dir.iterdir()):
            if p.is_dir() and (p / "index.html").exists():
                html = (p / "index.html").read_text()
                if 'rel="canonical"' not in html:
                    missing.append(f"blog/{p.name}")

    check("All blog articles have canonical", len(missing) == 0,
          f"Missing: {', '.join(missing)}" if missing else None)


# ── 5. On-Page SEO (blog articles) ──

def audit_onpage():
    print("\n## 5. On-Page SEO")
    blog_dir = STATIC / "blog"
    if not blog_dir.exists():
        print("  ⚠ No blog articles yet")
        return

    for p in sorted(blog_dir.iterdir()):
        if not p.is_dir() or not (p / "index.html").exists():
            continue

        html = (p / "index.html").read_text()
        slug = p.name
        print(f"\n  --- {slug} ---")

        # Title tag
        title_match = re.search(r"<title>(.*?)</title>", html)
        if title_match:
            title = title_match.group(1)
            check(f"Title exists ({len(title)} chars)", True)
            check("Title under 60 chars", len(title) <= 65)
        else:
            check("Title tag exists", False)

        # Meta description
        desc_match = re.search(r'<meta name="description" content="(.*?)"', html)
        if desc_match:
            desc = desc_match.group(1)
            check(f"Meta description ({len(desc)} chars)", True)
            check("Description under 160 chars", len(desc) <= 165)
        else:
            check("Meta description exists", False)

        # H1
        h1_count = len(re.findall(r"<h1[^>]*>", html))
        check("Exactly one H1", h1_count == 1)

        # FAQ
        check("Has FAQ section", "ms-faq" in html)

        # Schema
        check("Has Article schema", '"@type":"Article"' in html or '"@type": "Article"' in html)
        check("Has FAQPage schema", '"@type":"FAQPage"' in html or '"@type": "FAQPage"' in html)
        check("Has BreadcrumbList schema", '"@type":"BreadcrumbList"' in html or '"@type": "BreadcrumbList"' in html)

        # Screenshots
        check("Has screenshots", "ms-screenshot-wrap" in html)

        # Internal links
        internal_links = len(re.findall(rf'href="{SITE_URL}[^"]*"', html))
        check(f"Internal links ({internal_links})", internal_links >= 2)

        # Images
        imgs = re.findall(r"<img[^>]+>", html)
        for img in imgs:
            if "favicon" in img:
                continue
            has_lazy = 'loading="lazy"' in img
            has_dims = "width=" in img and "height=" in img
            if not has_lazy or not has_dims:
                check(f"Image has lazy+dimensions", False)
                break
        else:
            if imgs:
                check("All images have lazy+dimensions", True)


# ── 6. 404 page ──

def audit_404():
    print("\n## 6. 404 Page")
    check("Custom 404.html exists", (LAYOUTS / "404.html").exists())


# ── 7. noindex on legal pages ──

def audit_noindex():
    print("\n## 7. noindex on legal pages")
    for name in ["privacy-policy", "refund-policy", "terms-of-service"]:
        f = LAYOUTS / name / "single.html"
        if f.exists():
            has_noindex = "noindex" in f.read_text()
            check(f"{name} has noindex", has_noindex)
        else:
            check(f"{name} layout exists", False)


# ── 8. Organization schema on homepage ──

def audit_homepage_schema():
    print("\n## 8. Homepage schema")
    f = LAYOUTS / "index.html"
    if f.exists():
        html = f.read_text()
        check("Organization schema present", '"@type":"Organization"' in html or '"@type": "Organization"' in html)
    else:
        check("Homepage layout exists", False)


# ── 9. Sync static/blog → public/blog ──

def audit_sync():
    print("\n## 9. static/blog ↔ public/blog sync")
    blog_dir = STATIC / "blog"
    public_blog = Path("public/blog")

    if not blog_dir.exists():
        print("  ⚠ No blog articles yet")
        return

    out_of_sync = []
    for p in sorted(blog_dir.iterdir()):
        if p.is_dir() and (p / "index.html").exists():
            pub = public_blog / p.name / "index.html"
            if not pub.exists():
                out_of_sync.append(p.name)
            elif pub.read_text() != (p / "index.html").read_text():
                out_of_sync.append(p.name)

    check("static/blog and public/blog in sync", len(out_of_sync) == 0,
          f"Out of sync: {', '.join(out_of_sync)}" if out_of_sync else None)

    if out_of_sync:
        print("  🔧 Syncing...")
        os.system("cp -r static/blog/* public/blog/ 2>/dev/null")
        fixes.append(f"Synced {len(out_of_sync)} articles to public/blog")

    # Check for stale flat .html files
    if public_blog.exists():
        stale = [f.name for f in public_blog.glob("*.html") if f.is_file() and f.name != "index.html"]
        if stale:
            print(f"  🔧 Removing {len(stale)} stale flat HTML files...")
            for f in public_blog.glob("*.html"):
                if f.is_file() and f.name != "index.html":
                    f.unlink()
            fixes.append(f"Removed stale flat HTML files: {', '.join(stale)}")
        check("No stale flat .html files in public/blog", len(stale) == 0)


# ── 10. Google Data ──

def get_google_creds():
    """Load Google service account credentials from env or file."""
    try:
        from google.oauth2 import service_account
        key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY", "")
        if key_json:
            info = json.loads(key_json)
            return service_account.Credentials.from_service_account_info(info)
        key_file = Path("google-service-account.json")
        if key_file.exists():
            return service_account.Credentials.from_service_account_file(str(key_file))
    except ImportError:
        pass
    return None


def google_indexed_pages():
    """Get number of indexed pages from Google Search Console."""
    creds = get_google_creds()
    if not creds:
        return None
    try:
        from googleapiclient.discovery import build
        scoped = creds.with_scopes(["https://www.googleapis.com/auth/webmasters.readonly"])
        service = build("searchconsole", "v1", credentials=scoped)

        # Try both URL formats
        for site_url in [GSC_SITE_URL, SITE_URL + "/"]:
            try:
                response = service.searchAnalytics().query(
                    siteUrl=site_url,
                    body={
                        "startDate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                        "endDate": datetime.now().strftime("%Y-%m-%d"),
                        "dimensions": ["page"],
                        "rowLimit": 1000,
                    }
                ).execute()
                rows = response.get("rows", [])
                return {
                    "indexed_pages": len(rows),
                    "total_clicks": sum(r.get("clicks", 0) for r in rows),
                    "total_impressions": sum(r.get("impressions", 0) for r in rows),
                    "top_pages": sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)[:5],
                }
            except Exception:
                continue
    except Exception as e:
        print(f"  ⚠ Search Console API error: {e}")
    return None


def google_analytics_traffic():
    """Get weekly traffic from Google Analytics 4."""
    creds = get_google_creds()
    if not creds:
        return None
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric, FilterExpression, Filter
        )

        scoped = creds.with_scopes(["https://www.googleapis.com/auth/analytics.readonly"])
        client = BetaAnalyticsDataClient(credentials=scoped)

        # Total traffic this week
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            date_ranges=[DateRange(
                start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                end_date="today",
            )],
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
            ],
            limit=100,
        )
        response = client.run_report(request)

        total_sessions = 0
        total_views = 0
        blog_pages = []

        for row in response.rows:
            path = row.dimension_values[0].value
            sessions = int(row.metric_values[0].value)
            views = int(row.metric_values[1].value)
            total_sessions += sessions
            total_views += views
            if "/blog/" in path:
                blog_pages.append({"path": path, "sessions": sessions, "views": views})

        blog_pages.sort(key=lambda x: x["views"], reverse=True)

        return {
            "total_sessions": total_sessions,
            "total_views": total_views,
            "blog_sessions": sum(p["sessions"] for p in blog_pages),
            "blog_views": sum(p["views"] for p in blog_pages),
            "top_blog_pages": blog_pages[:5],
        }
    except Exception as e:
        print(f"  ⚠ Analytics API error: {e}")
    return None


def site_stats():
    print("\n## 10. Site Statistics")

    # Count pillar pages
    pillars = [p.name for p in STATIC.iterdir()
               if p.is_dir() and (p / "index.html").exists()
               and p.name not in ("blog", "welcome", "mathsolver_solution_images")]
    print(f"  Pillar pages: {len(pillars)}")

    # Count blog articles
    blog_dir = STATIC / "blog"
    articles = []
    if blog_dir.exists():
        articles = [p.name for p in blog_dir.iterdir()
                    if p.is_dir() and (p / "index.html").exists()]
    print(f"  Blog articles: {len(articles)}")
    print(f"  Total content pages: {len(pillars) + len(articles) + 1}")  # +1 for homepage

    # New articles this week (from git log)
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={week_ago}", "--diff-filter=A", "--name-only", "--pretty=format:"],
            capture_output=True, text=True
        )
        new_files = [l for l in result.stdout.strip().split("\n")
                     if l.startswith("static/blog/") and l.endswith("index.html")]
        new_slugs = sorted(set(f.replace("static/blog/", "").replace("/index.html", "") for f in new_files))
        # Only count articles that still exist
        new_slugs = [s for s in new_slugs if (blog_dir / s / "index.html").exists()]
        print(f"  New articles this week: {len(new_slugs)}")
        for s in new_slugs:
            print(f"    - {s}")
    except Exception:
        print("  New articles this week: (git not available)")

    # Sitemap URLs count
    sitemap_file = STATIC / "sitemap.xml"
    if sitemap_file.exists():
        sitemap = sitemap_file.read_text()
        url_count = sitemap.count("<url>")
        print(f"  URLs in sitemap: {url_count}")

    # Google Search Console data
    print("\n  --- Google Search Console (last 7 days) ---")
    gsc = google_indexed_pages()
    if gsc:
        print(f"  Pages with impressions: {gsc['indexed_pages']}")
        print(f"  Total clicks: {gsc['total_clicks']}")
        print(f"  Total impressions: {gsc['total_impressions']}")
        if gsc["top_pages"]:
            print("  Top pages by clicks:")
            for p in gsc["top_pages"]:
                keys = p.get("keys", ["?"])
                print(f"    {keys[0]} — {p.get('clicks', 0)} clicks, {p.get('impressions', 0)} impressions")
    else:
        print("  (Google Search Console API not available)")

    # Google Analytics data
    print("\n  --- Google Analytics (last 7 days) ---")
    ga = google_analytics_traffic()
    if ga:
        print(f"  Total sessions: {ga['total_sessions']}")
        print(f"  Total page views: {ga['total_views']}")
        print(f"  Blog sessions: {ga['blog_sessions']}")
        print(f"  Blog page views: {ga['blog_views']}")
        if ga["top_blog_pages"]:
            print("  Top blog pages:")
            for p in ga["top_blog_pages"]:
                print(f"    {p['path']} — {p['views']} views, {p['sessions']} sessions")
    else:
        print("  (Google Analytics API not available)")

    return {
        "pillars": len(pillars),
        "articles": len(articles),
        "total": len(pillars) + len(articles) + 1,
        "new_this_week": len(new_slugs) if 'new_slugs' in dir() else 0,
        "new_slugs": new_slugs if 'new_slugs' in dir() else [],
        "gsc": gsc,
        "ga": ga,
    }


# ── MAIN ──

def main():
    print("=" * 60)
    print(f"SEO Audit — MathSolver — {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

    audit_robots()
    audit_sitemap()
    audit_llms()
    audit_canonical()
    audit_onpage()
    audit_404()
    audit_noindex()
    audit_homepage_schema()
    audit_sync()
    stats = site_stats()

    print("\n" + "=" * 60)
    if fixes:
        print(f"🔧 Auto-fixed {len(fixes)} issues:")
        for f in fixes:
            print(f"  - {f}")
    if issues:
        print(f"\n⚠ {len(issues)} issues found:")
        for i in issues:
            print(f"  - {i}")
    if not fixes and not issues:
        print("✅ All SEO checks passed!")
    print("=" * 60)

    # Write report
    with open("seo_report.txt", "w") as f:
        f.write(f"SEO Audit Report — {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"{'=' * 50}\n\n")
        f.write(f"SITE STATISTICS\n")
        f.write(f"  Pillar pages:         {stats['pillars']}\n")
        f.write(f"  Blog articles:        {stats['articles']}\n")
        f.write(f"  Total content pages:  {stats['total']}\n")
        f.write(f"  New this week:        {stats['new_this_week']}\n")
        for s in stats.get("new_slugs", []):
            f.write(f"    - {s}\n")

        gsc = stats.get("gsc")
        if gsc:
            f.write(f"\nGOOGLE SEARCH CONSOLE (last 7 days)\n")
            f.write(f"  Pages with impressions: {gsc['indexed_pages']}\n")
            f.write(f"  Total clicks:           {gsc['total_clicks']}\n")
            f.write(f"  Total impressions:      {gsc['total_impressions']}\n")
            if gsc["top_pages"]:
                f.write(f"  Top pages:\n")
                for p in gsc["top_pages"]:
                    keys = p.get("keys", ["?"])
                    f.write(f"    {keys[0]} — {p.get('clicks', 0)} clicks\n")

        ga = stats.get("ga")
        if ga:
            f.write(f"\nGOOGLE ANALYTICS (last 7 days)\n")
            f.write(f"  Total sessions:    {ga['total_sessions']}\n")
            f.write(f"  Total page views:  {ga['total_views']}\n")
            f.write(f"  Blog sessions:     {ga['blog_sessions']}\n")
            f.write(f"  Blog page views:   {ga['blog_views']}\n")
            if ga["top_blog_pages"]:
                f.write(f"  Top blog pages:\n")
                for p in ga["top_blog_pages"]:
                    f.write(f"    {p['path']} — {p['views']} views\n")

        f.write(f"\nAUDIT RESULTS\n")
        if fixes:
            f.write(f"  Auto-fixed: {len(fixes)}\n")
            for fix in fixes:
                f.write(f"    - {fix}\n")
        if issues:
            f.write(f"  Issues: {len(issues)}\n")
            for issue in issues:
                f.write(f"    - {issue}\n")
        if not fixes and not issues:
            f.write(f"  All SEO checks passed!\n")

    return 1 if issues and not fixes else 0


if __name__ == "__main__":
    exit(main())
