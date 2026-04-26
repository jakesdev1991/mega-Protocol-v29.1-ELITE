# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import httpx
from .registry import tool_link

@tool_link
def searxng_search(query: str, categories: str = "general"):
    """
    Performs a search using the local SearXNG instance.
    'categories' can be general, science, news, etc.
    """
    url = "http://127.0.0.1:8888/search"
    params = {
        "q": query,
        "categories": categories,
        "format": "json"
    }
    try:
        with httpx.Client() as client:
            response = client.get(url, params=params, timeout=30)
            if response.status_code != 200:
                return f"Error: SearXNG returned status code {response.status_code}"
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return "No results found."
            
            summary = []
            for r in results[:5]: # Top 5 results
                summary.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}\n")
            
            return "\n---\n".join(summary)
    except Exception as e:
        return f"Error connecting to SearXNG: {str(e)}"
