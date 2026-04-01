# Читаем текущий скрипт и патчим его
with open('generate_articles.py', 'r') as f:
    content = f.read()

# Fix 1: Сохранять в static/blog/slug/index.html
content = content.replace(
    'CONTENT_DIR   = Path("content/blog")',
    'CONTENT_DIR   = Path("static/blog")'
)

# Fix 2: Добавить валидацию пустых полей перед сохранением
old = '''        if score >= MIN_SCORE or verdict == "PUBLISH":
                    success = True
                    break'''
new = '''        # Check that key fields are not empty
                if not data.get('h1') or not data.get('meta_title') or not data.get('intro'):
                    print(f"  → Key fields empty! h1='{data.get('h1')}' — forcing revision")
                    validation = {"total": 0, "issues": ["h1 is empty", "meta_title is empty", "intro is empty"], "verdict": "REVISE"}
                elif score >= MIN_SCORE or verdict == "PUBLISH":
                    success = True
                    break'''
content = content.replace(old, new)

# Fix 3: Сохранять как index.html в подпапке
old_save = '''    # Hugo content file (triggers page creation)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    content_file = CONTENT_DIR / f"{url_slug}.md"
    content_file.write_text(f"""---
title: "{article['title']}"
url: "/blog/{url_slug}/"
date: {datetime.now().strftime("%Y-%m-%d")}
draft: false
---
""")

    # Hugo layout file (the actual HTML)
    layout_dir = LAYOUTS_DIR / url_slug
    layout_dir.mkdir(parents=True, exist_ok=True)
    layout_file = layout_dir / "single.html"
    layout_file.write_text(html)

    print(f"  → Saved: /blog/{url_slug}/")
    return str(content_file), str(layout_file)'''

new_save = '''    # Save as static/blog/slug/index.html — served directly by Hugo/Cloudflare
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    article_dir = CONTENT_DIR / url_slug
    article_dir.mkdir(parents=True, exist_ok=True)
    html_file = article_dir / "index.html"
    html_file.write_text(html, encoding="utf-8")
    print(f"  → Saved: /blog/{url_slug}/")
    return str(html_file)'''

content = content.replace(old_save, new_save)

# Fix 4: Упростить git_push — убрать дублирующий git config
old_git = '''def git_push(articles_published):
    titles = ", ".join([a["keyword"] for a in articles_published])
    commit_msg = f"Add {len(articles_published)} articles: {titles[:80]}"

    subprocess.run(["git", "config", "user.email", "bot@mathsolver.cloud"], check=True)
    subprocess.run(["git", "config", "user.name", "MathSolver Bot"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"\\n✅ Pushed to GitHub: {commit_msg}")'''

new_git = '''def git_push(articles_published):
    titles = ", ".join([a["keyword"] for a in articles_published])
    commit_msg = f"Auto-publish {datetime.now().strftime('%Y-%m-%d')}: {titles[:80]}"
    subprocess.run(["git", "add", "."], check=True)
    result = subprocess.run(["git", "diff", "--staged", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"\\n✅ Pushed to GitHub: {commit_msg}")
    else:
        print("\\nNo changes to push")'''

content = content.replace(old_git, new_git)

with open('generate_articles.py', 'w') as f:
    f.write(content)

print("✅ Patched!")
