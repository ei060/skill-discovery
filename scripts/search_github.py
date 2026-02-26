#!/usr/bin/env python3
"""
GitHub Search API wrapper for skill-discovery
Searches for repositories matching domain keywords
"""

import json
import sys
from datetime import datetime, timedelta
from urllib.parse import quote

def build_search_query(domain_config, days_back=7):
    """Build GitHub search query from domain config"""
    since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    base_query = domain_config.get("github_query", "")
    time_filter = f"pushed:>{since_date}"

    return f"{base_query} {time_filter}".strip()

def search_github(domain_config, max_results=20):
    """
    Search GitHub for repositories

    Returns list of repos with metadata
    """
    query = build_search_query(domain_config)
    encoded_query = quote(query)

    # Using GitHub Search API (no auth needed, rate limited)
    api_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=updated&order=desc&per_page={max_results}"

    print(f"Searching GitHub: {query}", file=sys.stderr)

    try:
        import urllib.request
        with urllib.request.urlopen(api_url, timeout=10) as response:
            data = json.loads(response.read().decode())

            repos = []
            for item in data.get("items", []):
                repo = {
                    "id": f"gh_{item['id']}",
                    "name": item["name"],
                    "full_name": item["full_name"],
                    "url": item["html_url"],
                    "description": item.get("description", ""),
                    "stars": item["stargazers_count"],
                    "language": item.get("language", "Unknown"),
                    "updated_at": item["updated_at"],
                    "topics": item.get("topics", []),
                    "source": "github"
                }
                repos.append(repo)

            return repos

    except Exception as e:
        print(f"GitHub search error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    # Test with browser-automation domain
    test_domain = {
        "github_query": "browser automation language:javascript OR python",
        "subreddits": ["Python"]
    }

    results = search_github(test_domain)
    print(json.dumps(results, indent=2))
