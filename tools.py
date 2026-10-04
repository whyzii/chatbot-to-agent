from datetime import datetime, timedelta, timezone
import feedparser

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


if __name__ == "__main__":
    for item in get_latest_items():
        print(f"{item['published'][:10]}  [{item['source']}]  {item['title']}")