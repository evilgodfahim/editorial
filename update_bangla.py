import feedparser
import hashlib
import os
from datetime import datetime
import xml.etree.ElementTree as ET

# Bangla editorial feeds
FEEDS = [
    "https://evilgodfahim.github.io/bdpratidin-rss/feed.xml",
    "https://politepol.com/fd/DbgDjmR4B0ua.xml",
    "https://politepol.com/fd/1yC3YJpL3i6t.xml",
    "https://fetchrss.com/feed/aLNkZSZkMOtSaLNkNF2oqA-i.rss",
    "https://politepol.com/fd/lRzLqNhRg2jV.xml",
    "https://politepol.com/fd/LWVzWA8NSHfJ.xml",
    "https://politepol.com/fd/4LWXWOY5wPR9.xml",
    "https://politepol.com/fd/VnoJt9i4mZPJ.xml",
    "https://politepol.com/fd/R6Nj5lriwGBg.xml",
    "https://politepol.com/fd/MMd5ai243dRY.xml",
    "https://politepol.com/fd/aPXIv1Q7cs7S.xml",
    "https://politepol.com/fd/dwg0cNjfFTLe.xml",
    "https://politepol.com/fd/DrjUg80wxrku.xml"
]

OUTPUT_FILE = "bangla_combined.xml"
INDEX_FILE = "bangla_index.txt"
MAX_ARTICLES = 200

def get_id(entry):
    base = entry.get("id") or entry.get("link") or entry.get("title", "")
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def load_seen():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen(seen):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        for item in seen:
            f.write(item + "\n")

def main():
    seen = load_seen()
    new_articles = []

    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries:
            uid = get_id(entry)
            if uid not in seen:
                seen.add(uid)
                new_articles.append((entry, uid))

    new_articles.sort(key=lambda x: datetime(*x[0].published_parsed[:6]) if hasattr(x[0], "published_parsed") else datetime.now(), reverse=True)
    all_articles = new_articles[:MAX_ARTICLES]
    save_seen(set(uid for _, uid in all_articles))

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Bangla Editorial Combined Feed"
    ET.SubElement(channel, "link").text = "https://yourusername.github.io/bangla_combined.xml"
    ET.SubElement(channel, "description").text = "Aggregated Bangla editorial feed without duplicates"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    for entry, uid in all_articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = entry.get("title", "No title")
        ET.SubElement(item, "link").text = entry.get("link", "")
        ET.SubElement(item, "guid").text = uid
        ET.SubElement(item, "description").text = entry.get("summary", "")
        pub_date = entry.get("published", datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        ET.SubElement(item, "pubDate").text = pub_date

    ET.ElementTree(rss).write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
