from datetime import datetime, timedelta, timezone
# pyrefly: ignore [missing-import]
import feedparser
# pyrefly: ignore [missing-import]
import trafilatura
import json
from pathlib import Path


FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Ars Technica": "https://arstechnica.com/ai/feed/",
}

def get_latest_items(days: int = 7, max_items: int = 20) -> list[dict]:
    """Return recent items from all feeds, newest first."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    items = []
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            parsed = entry.get("published_parsed") or entry.get("updated_parsed")
            if not parsed:
                continue
            published = datetime(*parsed[:6], tzinfo=timezone.utc)
            if published < cutoff:
                continue
            items.append({
                "source": source,
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": published.isoformat(),
            })
    items.sort(key=lambda item: item["published"], reverse=True)
    return items[:max_items]


def fetch_article(url: str, max_chars: int = 6000) -> str:
    """Download a page and return the main article text."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    text = trafilatura.extract(downloaded) or ""
    return text[:max_chars]

PUBLISHED_PATH = Path(__file__).parent / "published.json"

def _load_published() -> list[dict]:
    if not PUBLISHED_PATH.exists():
        return []
    return json.loads(PUBLISHED_PATH.read_text())

def is_published(url: str) -> bool:
    """Check whether an item with this link is already on the website."""
    return any(item.get("source_url") == url for item in _load_published())

def save_item(item: dict) -> str:
    """Save a finished news item for the website."""
    items = _load_published()
    if any(saved.get("source_url") == item.get("source_url") for saved in items):
        return "Already saved."
    items.append(item)
    PUBLISHED_PATH.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    return f"Saved: {item.get('title')}"


if __name__ == "__main__":
    items = get_latest_items(days=7)
    for item in items:
        print(f"{item['published'][:10]}  [{item['source']}]  {item['title']}")

    test_item = {"title": "Test item", "source_url": "https://example.com/test"}
    print(is_published(test_item["source_url"]))   # False the first time
    print(save_item(test_item))                    # Saved: Test item
    print(is_published(test_item["source_url"]))   # True
    print(save_item(test_item))                    # Already saved.
    print("\n--- First article ---\n")
    print(fetch_article(items[0]["link"])[:1000])