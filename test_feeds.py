# pyrefly: ignore [missing-import]
import feedparser

FEEDS = [
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://blog.google/technology/ai/rss/",
    "https://huggingface.co/blog/feed.xml",
    "https://arstechnica.com/ai/feed/",
]

for url in FEEDS:
    feed = feedparser.parse(url)
    print(f"\n{url} -> {len(feed.entries)} items")
    for entry in feed.entries[:3]:
        print(f"  - {entry.get('title')} ({entry.get('published', 'no date')})")