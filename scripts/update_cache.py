#!/usr/bin/env python3
"""
Cache management for skill-discovery
Handles reading, writing, and TTL checking
"""

import json
import sys
import os
from datetime import datetime

def get_cache_path(domain_id, cache_dir="cache"):
    """Get cache file path for a domain"""
    return os.path.join(cache_dir, f"{domain_id}.json")

def read_cache(domain_id, cache_dir="cache"):
    """Read cache for a domain"""
    cache_path = get_cache_path(domain_id, cache_dir)

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"Cache file corrupted: {cache_path}", file=sys.stderr)
        return None

def write_cache(domain_id, data, cache_dir="cache"):
    """Write cache for a domain"""
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = get_cache_path(domain_id, cache_dir)

    cache_data = {
        "domain": domain_id,
        "last_updated": datetime.now().isoformat(),
        "data": data
    }

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

    return cache_data

def is_cache_fresh(cache_entry, ttl_seconds):
    """Check if cache is still fresh"""
    if not cache_entry:
        return False

    last_updated = cache_entry.get("last_updated")
    if not last_updated:
        return False

    try:
        last_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        age_seconds = (datetime.now(last_time.tzinfo) - last_time).total_seconds()

        return age_seconds < ttl_seconds
    except:
        return False

def trim_cache(cache_data, max_items=100):
    """Trim cache to max items, keep most recent"""
    if not isinstance(cache_data, list):
        return cache_data

    # Sort by updated_at or created_at if available
    try:
        cache_data.sort(
            key=lambda x: x.get("updated_at") or x.get("created_at") or "",
            reverse=True
        )
    except:
        pass

    return cache_data[:max_items]

def get_last_update_time(domain_id, cache_dir="cache"):
    """Get last update timestamp for a domain"""
    cache = read_cache(domain_id, cache_dir)
    if cache:
        return cache.get("last_updated")
    return None

if __name__ == "__main__":
    # Test cache operations
    domain = "browser-automation"

    # Write test cache
    test_data = [
        {"name": "puppeteer", "url": "https://github.com/...", "stars": 100}
    ]

    write_cache(domain, test_data)

    # Read back
    cached = read_cache(domain)
    print(f"Cache fresh: {is_cache_fresh(cached, 3600)}")
    print(json.dumps(cached, indent=2))
