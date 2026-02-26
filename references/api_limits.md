# API Limits and Rate Limiting

## GitHub Search API

**Rate Limits** (without authentication):
- 60 requests per hour
- IP-based rate limiting

**Rate Limits** (with authentication):
- 5000 requests per hour
- Requires GitHub account token

**Best Practices**:
1. Cache results aggressively
2. Use specific queries to reduce need for pagination
3. Fallback to WebSearch with "site:github.com" when rate limited
4. Store rate limit reset time in cache

**Error Handling**:
```python
# Check for 403 (rate limit)
if response.status == 403:
    # Log rate limit reset time from headers
    reset_time = response.headers.get('X-RateLimit-Reset')
    # Use WebSearch fallback
```

---

## Reddit API

**Rate Limits** (JSON API, no authentication):
- ~30 requests per minute
- Unknown exact limit, seems IP-based

**Best Practices**:
1. Space out requests between subreddits
2. Use /new.json instead of /hot.json for recent content
3. No auth needed for basic reading

**Error Handling**:
- 429: Too many requests, backoff and retry
- 404: Subreddit doesn't exist or is private
- 403: Subreddit is restricted

---

## WebSearch

**Rate Limits**:
- Managed by Claude Code infrastructure
- Generally unlimited for reasonable use

**Best Practices**:
1. Use specific queries
2. Filter by date when possible ("after:2026-02-19")
3. Prioritize GitHub/Reddit results over general web

**Query Patterns**:
```
"{domain} tools 2026"
"best {technology} alternatives"
"new {domain} frameworks"
"{domain} tutorial examples"
```

---

## Fallback Strategy

When primary APIs fail:

1. **GitHub rate limit**:
   ```python
   # Fallback to WebSearch
   query = f"site:github.com {github_search_query}"
   ```

2. **Reddit fails**:
   - Skip Reddit results
   - Continue with GitHub + WebSearch

3. **All fail**:
   - Use existing cache (even if stale)
   - Show user warning with last successful update time
   - Suggest manual alternatives

---

## Caching Strategy

**Why cache aggressively**:
- Avoid hitting rate limits
- Faster response times
- Work offline (briefly)
- Track history over time

**Cache Hierarchy**:
1. Memory cache (session) - instant
2. File cache (persistent) - fast
3. Fresh API search - slow but accurate

**TTL Guidelines**:
- Hot domains (AI): 6 hours
- Medium (browser automation): 12 hours
- Cold (scripts): 24 hours

**Force refresh**:
- User explicitly requests
- Cache is empty/invalid
- Suspected data staleness
