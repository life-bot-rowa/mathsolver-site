#!/usr/bin/env python3
"""
SEO patcher v2 — runs on BOTH static/blog/ and public/ so that
auto-publish workflow (cp static/blog -> public/blog) doesn't revert fixes.

Adds:
- og:image, og:site_name (if missing)
- twitter:card/title/description/image (if missing)
- Expands meta description if shorter than MIN_DESC_LEN chars

Idempotent: safe to run repeatedly.
"""

import re
from pathlib import Path

SITE_URL = "https://mathsolver.cloud"
PUBLIC = Path("public")
STATIC = Path("static")

MIN_DESC_LEN = 120
MAX_DESC_LEN = 160
# Reusable tails ranked by length, picked to land target description length in [120, 160].
TAIL_LONG = ". Free AI math solver — take a screenshot, get instant step-by-step solutions."      # 80 chars
TAIL_MED  = ". Free AI math solver with step-by-step solutions."                                   # 52 chars
TAIL_SHORT = ". Free step-by-step math help."                                                       # 30 chars


def pick_tail(desc: str) -> str:
    """Pick a tail that brings description into [120, 160] range."""
    base_len = len(desc)
    # Try long first, then medium, then short — but never exceed 160.
    for tail in (TAIL_LONG, TAIL_MED, TAIL_SHORT):
        new_len = base_len + len(tail)
        if MIN_DESC_LEN <= new_len <= MAX_DESC_LEN:
            return tail
    # If even the shortest tail overshoots, return empty (desc is already long enough or edge case).
    # If even the longest tail doesn't reach MIN, use the longest anyway.
    if base_len + len(TAIL_LONG) < MIN_DESC_LEN:
        return TAIL_LONG
    if base_len >= MIN_DESC_LEN:
        return ""  # already long enough
    # Fallback: use shortest so we don't overshoot too much
    return TAIL_SHORT


def expand_description(html: str) -> tuple[str, bool]:
    """Normalize <meta name=description>: extend if < MIN_DESC_LEN, trim if > MAX_DESC_LEN."""
    m = re.search(r'<meta name="description" content="([^"]*)">', html)
    if not m:
        return html, False

    current = m.group(1)

    # Trim if too long
    if len(current) > MAX_DESC_LEN:
        trimmed = current[:MAX_DESC_LEN].rsplit(" ", 1)[0].rstrip(",;:.") + "."
        new_tag = f'<meta name="description" content="{trimmed}">'
        html = html.replace(m.group(0), new_tag, 1)
        html = re.sub(
            r'<meta property="og:description" content="' + re.escape(current) + r'">',
            f'<meta property="og:description" content="{trimmed}">',
            html,
        )
        html = re.sub(
            r'<meta name="twitter:description" content="' + re.escape(current) + r'">',
            f'<meta name="twitter:description" content="{trimmed}">',
            html,
        )
        return html, True

    if len(current) >= MIN_DESC_LEN:
        return html, False

    tail = pick_tail(current)
    if not tail:
        return html, False

    # Avoid appending if already present (idempotency)
    if current.endswith(tail.strip()):
        return html, False

    new_desc = current.rstrip(".") + tail
    # Clamp to 160 just in case
    if len(new_desc) > MAX_DESC_LEN:
        new_desc = new_desc[:MAX_DESC_LEN].rsplit(" ", 1)[0] + "."

    new_tag = f'<meta name="description" content="{new_desc}">'
    html = html.replace(m.group(0), new_tag, 1)

    # Also update og:description and twitter:description if they match the old description
    html = re.sub(
        r'<meta property="og:description" content="' + re.escape(current) + r'">',
        f'<meta property="og:description" content="{new_desc}">',
        html,
    )
    html = re.sub(
        r'<meta name="twitter:description" content="' + re.escape(current) + r'">',
        f'<meta name="twitter:description" content="{new_desc}">',
        html,
    )
    return html, True


def add_og_twitter_tags(html: str) -> tuple[str, bool]:
    """Ensure og:image, og:site_name, twitter:card + friends exist."""
    has_twitter = "twitter:card" in html
    has_og_image = "og:image" in html
    has_og_site_name = "og:site_name" in html

    if has_twitter and has_og_image and has_og_site_name:
        return html, False

    og_title = ""
    og_desc = ""
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    if m:
        og_title = m.group(1)
    m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    if m:
        og_desc = m.group(1)
    if not og_title:
        m = re.search(r"<title>([^<]*)</title>", html)
        if m:
            og_title = m.group(1)
    if not og_desc:
        m = re.search(r'<meta name="description" content="([^"]*)"', html)
        if m:
            og_desc = m.group(1)

    new_tags = []
    if not has_og_image:
        new_tags.append(f'  <meta property="og:image" content="{SITE_URL}/favicon.png">')
    if not has_og_site_name:
        new_tags.append(f'  <meta property="og:site_name" content="MathSolver">')
    if not has_twitter:
        new_tags.append(f'  <meta name="twitter:card" content="summary">')
        new_tags.append(f'  <meta name="twitter:title" content="{og_title}">')
        new_tags.append(f'  <meta name="twitter:description" content="{og_desc}">')
        new_tags.append(f'  <meta name="twitter:image" content="{SITE_URL}/favicon.png">')

    if not new_tags:
        return html, False

    insert_block = "\n".join(new_tags)
    m = re.search(r'(<meta property="og:type" content="[^"]*">)', html)
    if m:
        html = html[: m.end()] + "\n" + insert_block + html[m.end():]
        return html, True
    m = re.search(r'(<meta name="description" content="[^"]*">)', html)
    if m:
        html = html[: m.end()] + "\n" + insert_block + html[m.end():]
        return html, True
    return html, False


def patch_file(filepath: Path) -> bool:
    html = filepath.read_text(encoding="utf-8")
    changed = False

    html, c1 = expand_description(html)
    html, c2 = add_og_twitter_tags(html)

    if c1 or c2:
        filepath.write_text(html, encoding="utf-8")
        changed = True
    return changed


def main():
    targets = []
    # static/blog (source of truth for blog posts)
    targets += sorted((STATIC / "blog").glob("*/index.html"))
    # public/blog (live)
    targets += sorted((PUBLIC / "blog").glob("*/index.html"))
    # public pillars / root
    for f in sorted(PUBLIC.glob("*/index.html")):
        if f.parent == PUBLIC or "blog" in str(f):
            continue
        targets.append(f)
    root_index = PUBLIC / "index.html"
    if root_index.exists():
        targets.append(root_index)

    count = 0
    for f in targets:
        if patch_file(f):
            count += 1

    print(f"Patched {count} / {len(targets)} files.")


if __name__ == "__main__":
    main()
