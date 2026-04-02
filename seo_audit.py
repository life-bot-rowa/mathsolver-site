"""Weekly SEO audit — checks all items and fixes what it can."""

import os
import re
from pathlib import Path

SITE_URL = "https://mathsolver.cloud"
STATIC = Path("static")
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


# ── MAIN ──

def main():
    print("=" * 60)
    print("SEO Audit — MathSolver")
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
        f.write(f"SEO Audit Report\n")
        f.write(f"Fixes: {len(fixes)}\n")
        f.write(f"Issues: {len(issues)}\n")
        for fix in fixes:
            f.write(f"Fixed: {fix}\n")
        for issue in issues:
            f.write(f"Issue: {issue}\n")

    return 1 if issues and not fixes else 0


if __name__ == "__main__":
    exit(main())
