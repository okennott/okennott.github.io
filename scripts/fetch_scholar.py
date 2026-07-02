#!/usr/bin/env python3
"""Fetch Google Scholar stats for K.O. Onditi and write to assets/data/scholar-stats.json."""

import json
import time
import sys
import os

SCHOLAR_ID = "qnHYvIIAAAAJ"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "data", "scholar-stats.json")

def fetch_stats():
    try:
        from scholarly import scholarly
    except ImportError:
        print("Install scholarly: pip install scholarly", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching Scholar profile for id={SCHOLAR_ID}...")
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "counts"])

    stats = {
        "citations":            author.get("citedby", 0),
        "citations_since_2021": author.get("citedby5y", 0),
        "h_index":              author.get("hindex", 0),
        "h_index_since_2021":   author.get("hindex5y", 0),
        "i10_index":            author.get("i10index", 0),
        "i10_index_since_2021": author.get("i10index5y", 0),
        "total_publications":   len(author.get("publications", [])),
        "last_updated":         time.strftime("%Y-%m-%d"),
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(stats, f, indent=2)
        f.write("\n")

    print(f"Written: {stats}")

if __name__ == "__main__":
    fetch_stats()
