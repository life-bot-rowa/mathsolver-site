#!/usr/bin/env python3
"""
Send generation report via Gmail API
Called after generate_articles.py completes
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

def build_report():
    progress_file = Path(".generation_progress.json")
    if not progress_file.exists():
        return "No progress file found.", []

    progress = json.loads(progress_file.read_text())
    published = progress.get("published", [])
    needs_review = progress.get("needs_review", [])

    # Get today's articles (published today)
    today = datetime.now().strftime("%Y-%m-%d")
    todays_published = [a for a in published if a.get("published_at","").startswith(today)]
    todays_review = [a for a in needs_review if a.get("published_at","").startswith(today)]

    site_url = "https://mathsolver.cloud"

    lines = []
    lines.append(f"📊 MathSolver Article Generation Report")
    lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"")
    lines.append(f"✅ Published today: {len(todays_published)}")
    lines.append(f"⚠️  Needs review: {len(todays_review)}")
    lines.append(f"📚 Total published: {len(published)}")
    lines.append(f"")

    if todays_published:
        lines.append("--- PUBLISHED TODAY ---")
        for a in todays_published:
            url = f"{site_url}/blog/{a.get('slug','')}"
            lines.append(f"• {a.get('keyword','').title()}")
            lines.append(f"  {url}")
            lines.append(f"  Score: {a.get('score','?')}/7 | Cluster: {a.get('cluster','')}")
            lines.append("")

    if todays_review:
        lines.append("--- NEEDS REVIEW ---")
        for a in todays_review:
            lines.append(f"• {a.get('slug','')}")
            lines.append(f"  Score: {a.get('score','?')}/7")
            lines.append("")

    return "\n".join(lines), todays_published, todays_review

if __name__ == "__main__":
    report, published, review = build_report()
    print(report)
    
    # Write report to file for GitHub Actions
    Path("daily_report.txt").write_text(report)
    print(f"\nReport saved to daily_report.txt")
