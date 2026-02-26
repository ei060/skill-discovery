#!/usr/bin/env python3
"""
Reddit API fetcher for skill-discovery
Fetches posts from relevant subreddits
"""

import json
import sys
from datetime import datetime

def search_reddit(domain_config, max_results=10):
    """
    Search Reddit for relevant posts

    Returns list of posts with metadata
    """
    subreddits = domain_config.get("subreddits", [])
    all_posts = []

    for subreddit in subreddits:
        reddit_url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={max_results}"

        print(f"Fetching r/{subreddit}...", file=sys.stderr)

        try:
            import urllib.request
            headers = {'User-Agent': 'skill-discovery/1.0'}

            req = urllib.request.Request(reddit_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

                for post in data.get("data", {}).get("children", []):
                    post_data = post["data"]
                    post_obj = {
                        "id": f"reddit_{post_data['id']}",
                        "title": post_data["title"],
                        "url": f"https://reddit.com{post_data['permalink']}",
                        "subreddit": post_data["subreddit"],
                        "upvotes": post_data.get("ups", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "created_utc": post_data["created_utc"],
                        "selftext": post_data.get("selftext", "")[:500],  # Truncate
                        "source": "reddit"
                    }
                    all_posts.append(post_obj)

        except Exception as e:
            print(f"Reddit error for r/{subreddit}: {e}", file=sys.stderr)
            continue

    return all_posts

def filter_recent(posts, hours=24):
    """Filter posts from last N hours"""
    from datetime import datetime, timedelta
    cutoff = datetime.now().timestamp() - (hours * 3600)

    return [p for p in posts if p.get("created_utc", 0) > cutoff]

if __name__ == "__main__":
    test_domain = {
        "subreddits": ["Python", "automation"]
    }

    results = search_reddit(test_domain)
    recent = filter_recent(results, hours=48)

    print(json.dumps(recent, indent=2))
