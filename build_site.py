"""Build the website (docs/index.html) from published.json.

Run:  python build_site.py
"""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
PUBLISHED_PATH = ROOT / "published.json"
OUTPUT_PATH = ROOT / "docs" / "index.html"

# Order of the sections on the page, and the color that marks each category
CATEGORIES = {
    "New models": "#2563eb",
    "Research": "#7c3aed",
    "Tools and products": "#0f766e",
    "Industry and funding": "#c2410c",
    "Policy and safety": "#475569",
}

LATEST_COUNT = 5   # stories in the "Latest" column next to the lead story

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI News, Explained Simply</title>
<meta name="description" content="The important AI news, explained in plain English for people who can't keep up.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&family=Geist:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --paper: #ffffff; --ink: #14161a; --muted: #5b616e; --rule: #e2e4e8;
    --link: #1d4ed8; --soft: #f4f5f7;
    --serif: "Newsreader", Georgia, serif;
    --sans: "Geist", ui-sans-serif, system-ui, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    :root { --paper: #121418; --ink: #eceef1; --muted: #9aa1ad; --rule: #2a2e35;
            --link: #8fb2ff; --soft: #1b1e24; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans);
         font-size: 16px; line-height: 1.55; -webkit-font-smoothing: antialiased; }
  a { color: inherit; text-decoration: none; }
  .wrap { max-width: 1120px; margin: 0 auto; padding: 0 24px; }

  /* masthead */
  .masthead { border-bottom: 1px solid var(--rule); }
  .masthead .wrap { display: flex; flex-wrap: wrap; align-items: baseline;
                    justify-content: space-between; gap: 8px 24px; padding-top: 28px; padding-bottom: 18px; }
  .brand { font-family: var(--serif); font-weight: 700; font-size: clamp(1.9rem, 4vw, 2.8rem);
           letter-spacing: -0.02em; line-height: 1; margin: 0; }
  .tagline { color: var(--muted); font-size: .95rem; margin: 0; }
  nav { border-bottom: 1px solid var(--rule); }
  nav .wrap { display: flex; gap: 22px; overflow-x: auto; padding-top: 12px; padding-bottom: 12px;
              font-size: .9rem; font-weight: 500; white-space: nowrap; }
  nav a { color: var(--muted); display: inline-flex; align-items: center; gap: 8px; }
  nav a:hover { color: var(--ink); }
  .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }

  /* top: lead story + latest column */
  .top { display: grid; grid-template-columns: 1fr; gap: 36px; padding: 36px 0 44px;
         border-bottom: 1px solid var(--rule); }
  @media (min-width: 860px) { .top { grid-template-columns: 2fr 1fr; gap: 48px; } }
  .kicker { display: inline-flex; align-items: center; gap: 8px; font-size: .85rem; font-weight: 600; }
  .lead h2 { font-family: var(--serif); font-weight: 700; font-size: clamp(2rem, 4.6vw, 3.3rem);
             line-height: 1.08; letter-spacing: -0.02em; margin: 14px 0 18px; max-width: 22ch; }
  .lead h2 a:hover { color: var(--link); }
  .lead .summary { font-family: var(--serif); font-size: 1.3rem; line-height: 1.5; margin: 0 0 18px; max-width: 38em; }
  .why { background: var(--soft); border-left: 3px solid var(--accent, var(--muted));
         padding: 12px 16px; margin: 0 0 18px; max-width: 38em; }
  .why strong { font-weight: 600; }
  .byline { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 14px; color: var(--muted); font-size: .88rem; }
  .byline .source { color: var(--ink); font-weight: 500; }
  .read { color: var(--link); font-weight: 500; }
  .read:hover { text-decoration: underline; }

  .latest h3 { font-size: 1rem; font-weight: 600; margin: 0 0 6px; padding-bottom: 10px; border-bottom: 2px solid var(--ink); }
  .latest ol { list-style: none; margin: 0; padding: 0; }
  .latest li { padding: 14px 0; border-bottom: 1px solid var(--rule); }
  .latest li a { font-family: var(--serif); font-size: 1.12rem; font-weight: 600; line-height: 1.3; display: block; margin: 6px 0; }
  .latest li a:hover { color: var(--link); }
  .small { font-size: .8rem; color: var(--muted); display: flex; align-items: center; gap: 8px; }

  /* status labels: how confirmed the news is */
  .status { font-size: .75rem; font-weight: 500; padding: 1px 8px; border-radius: 4px; }
  .status.official { background: var(--ink); color: var(--paper); }
  .status.reported { border: 1px solid var(--muted); color: var(--muted); }
  .status.rumor { border: 1px dashed #b45309; color: #b45309; }

  /* category sections: each category is one column of stories */
  .sections { display: grid; grid-template-columns: 1fr; gap: 40px 40px; padding: 40px 0 16px;
              border-bottom: 1px solid var(--rule); }
  @media (min-width: 700px) { .sections { grid-template-columns: repeat(2, 1fr); } }
  @media (min-width: 1000px) { .sections { grid-template-columns: repeat(3, 1fr); } }
  section.category { border-top: 3px solid var(--color); padding-top: 12px; }
  section.category > h2 { font-size: 1.05rem; font-weight: 600; margin: 0 0 4px; }
  .story { padding: 14px 0 16px; border-bottom: 1px solid var(--rule); }
  .story:last-child { border-bottom: 0; }
  .story h3 { font-family: var(--serif); font-size: 1.25rem; font-weight: 600; line-height: 1.25; margin: 8px 0 8px; }
  .story h3 a:hover { color: var(--link); }
  .story p { margin: 0 0 10px; color: var(--muted); }

  footer { padding: 36px 0 56px; color: var(--muted); font-size: .9rem; }
  footer p { max-width: 42em; margin: 0 0 8px; }

  a:focus-visible { outline: 2px solid var(--link); outline-offset: 3px; border-radius: 2px; }
</style>
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <h1 class="brand">AI News, Explained Simply</h1>
    <p class="tagline">The important AI news in plain English. Updated {{updated}}.</p>
  </div>
</header>
<nav aria-label="Sections"><div class="wrap">{{nav}}</div></nav>
<main class="wrap">
  {{top}}
  {{sections}}
</main>
<footer>
  <div class="wrap">
    <p>Stories are found and summarized by an AI agent from official company blogs and news sites, then checked against the source. Every story links to its original article.</p>
    <p><strong>Official</strong> means the company announced it. <strong>Reported</strong> means a news outlet reported it. <strong>Rumor</strong> means it is not confirmed.</p>
  </div>
</footer>
</body>
</html>
"""

e = html.escape


def load_items() -> list[dict]:
    """Read published.json, keep only published items, newest first."""
    if not PUBLISHED_PATH.exists():
        return []
    items = json.loads(PUBLISHED_PATH.read_text())
    items = [item for item in items if item.get("decision") == "publish"]
    items.sort(key=lambda item: item.get("published", ""), reverse=True)
    return items


def nice_date(value: str) -> str:
    """'2026-10-02T15:00:00+00:00' -> '2 Oct 2026'."""
    try:
        return datetime.fromisoformat(value).strftime("%-d %b %Y")
    except (ValueError, TypeError):
        return ""


def slug(category: str) -> str:
    return category.lower().replace(" ", "-")


def kicker(item: dict) -> str:
    """Colored dot + category name."""
    category = item.get("category", "")
    color = CATEGORIES.get(category, "#6b7280")
    return f'<span class="kicker"><span class="dot" style="background:{color}"></span>{e(category)}</span>'


def status_label(item: dict) -> str:
    status = item.get("status", "")
    if status not in ("official", "reported", "rumor"):
        return ""
    return f'<span class="status {status}">{status.capitalize()}</span>'


def byline(item: dict) -> str:
    parts = []
    if item.get("source"):
        parts.append(f'<span class="source">{e(item["source"])}</span>')
    date = nice_date(item.get("published", ""))
    if date:
        parts.append(f"<span>{date}</span>")
    parts.append(status_label(item))
    return "".join(part for part in parts if part)


def render_lead(item: dict) -> str:
    url = e(item.get("source_url", ""))
    color = CATEGORIES.get(item.get("category", ""), "#6b7280")
    why = item.get("why_it_matters", "")
    why_html = f'<p class="why" style="--accent:{color}"><strong>Why it matters:</strong> {e(why)}</p>' if why else ""
    return f"""
    <article class="lead">
      {kicker(item)}
      <h2><a href="{url}" target="_blank" rel="noopener">{e(item.get("title", ""))}</a></h2>
      <p class="summary">{e(item.get("summary", ""))}</p>
      {why_html}
      <div class="byline">{byline(item)}<a class="read" href="{url}" target="_blank" rel="noopener">Read the original article</a></div>
    </article>"""


def render_latest(items: list[dict]) -> str:
    if not items:
        return ""
    rows = "".join(
        f'<li><span class="small">{kicker(item)}</span>'
        f'<a href="{e(item.get("source_url", ""))}" target="_blank" rel="noopener">{e(item.get("title", ""))}</a>'
        f'<span class="small">{e(item.get("source", ""))} {nice_date(item.get("published", ""))}</span></li>'
        for item in items
    )
    return f'<aside class="latest" aria-label="Latest stories"><h3>Latest</h3><ol>{rows}</ol></aside>'


def render_story(item: dict) -> str:
    url = e(item.get("source_url", ""))
    return f"""
      <article class="story">
        <div class="small">{status_label(item)}<span>{nice_date(item.get("published", ""))}</span></div>
        <h3><a href="{url}" target="_blank" rel="noopener">{e(item.get("title", ""))}</a></h3>
        <p>{e(item.get("summary", ""))}</p>
        <div class="byline"><span class="source">{e(item.get("source", ""))}</span><a class="read" href="{url}" target="_blank" rel="noopener">Read more</a></div>
      </article>"""


def build():
    items = load_items()

    if items:
        lead, rest = items[0], items[1:]
        top = f'<div class="top">{render_lead(lead)}{render_latest(rest[:LATEST_COUNT])}</div>'
    else:
        rest = []
        top = '<div class="top"><p>No stories yet. Run the agent to add the first ones.</p></div>'

    nav_links, sections = [], []
    for category, color in CATEGORIES.items():
        in_category = [item for item in rest if item.get("category") == category]
        if not in_category:
            continue
        nav_links.append(f'<a href="#{slug(category)}"><span class="dot" style="background:{color}"></span>{e(category)}</a>')
        stories = "".join(render_story(item) for item in in_category)
        sections.append(
            f'<section class="category" id="{slug(category)}" style="--color:{color}">'
            f'<h2>{e(category)}</h2>{stories}</section>'
        )

    page = (TEMPLATE
            .replace("{{updated}}", datetime.now().strftime("%A %-d %B %Y"))
            .replace("{{nav}}", "".join(nav_links))
            .replace("{{top}}", top)
            .replace("{{sections}}", f'<div class="sections">{"".join(sections)}</div>' if sections else ""))

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(page, encoding="utf-8")
    print(f"Built {OUTPUT_PATH} with {len(items)} stories.")


if __name__ == "__main__":
    build()