#!/usr/bin/env python3
"""
Merge and deduplicate results from multiple sources
"""

import json
import sys
from urllib.parse import urlparse

def normalize_url(url):
    """Normalize URL for deduplication"""
    try:
        parsed = urlparse(url.lower())
        return f"{parsed.netloc}{parsed.path}".rstrip('/')
    except:
        return url.lower()

def calculate_score(item, domain_keywords):
    """Calculate relevance score for an item"""
    score = 0

    # Base score by source
    source_bonus = {
        "github": 10,
        "reddit": 8,
        "web": 5
    }
    score += source_bonus.get(item.get("source", ""), 0)

    # Popularity bonus
    if item.get("source") == "github":
        stars = item.get("stars", 0)
        if stars > 1000:
            score += 5
        elif stars > 100:
            score += 3
        elif stars > 10:
            score += 1

    elif item.get("source") == "reddit":
        upvotes = item.get("upvotes", 0)
        if upvotes > 100:
            score += 5
        elif upvotes > 10:
            score += 2

    # Keyword matching
    text = f"{item.get('name', '')} {item.get('description', '')} {item.get('title', '')}".lower()
    for keyword in domain_keywords:
        if keyword.lower() in text:
            score += 2

    return score

def merge_results(github_results, reddit_results, web_results, domain_keywords):
    """
    Merge results from all sources, deduplicate, and rank

    Returns ranked list of unique items
    """
    all_items = []

    # Collect all items
    all_items.extend(github_results)
    all_items.extend(reddit_results)
    all_items.extend(web_results)

    # Deduplicate by URL
    seen_urls = {}
    unique_items = []

    for item in all_items:
        url = item.get("url", "")
        if not url:
            continue

        norm_url = normalize_url(url)

        if norm_url not in seen_urls:
            seen_urls[norm_url] = item
            unique_items.append(item)
        else:
            # Keep the one with higher source priority
            existing = seen_urls[norm_url]
            source_priority = {"github": 3, "reddit": 2, "web": 1}

            if source_priority.get(item.get("source", ""), 0) > source_priority.get(existing.get("source", ""), 0):
                seen_urls[norm_url] = item
                # Replace in list
                idx = unique_items.index(existing)
                unique_items[idx] = item

    # Score and rank
    for item in unique_items:
        item["score"] = calculate_score(item, domain_keywords)

    # Sort by score (descending)
    unique_items.sort(key=lambda x: x.get("score", 0), reverse=True)

    return unique_items

if __name__ == "__main__":
    # Test merge
    github = [
        {"name": "puppeteer", "url": "https://github.com/puppeteer/puppeteer", "stars": 100, "source": "github"}
    ]

    reddit = [
        {"title": "Puppeteer tutorial", "url": "https://github.com/puppeteer/puppeteer", "upvotes": 50, "source": "reddit"}
    ]

    merged = merge_results(github, reddit, [], ["puppeteer", "automation"])
    print(json.dumps(merged, indent=2))
