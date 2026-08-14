from __future__ import annotations
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def _duckduckgo_instant(query: str) -> Dict[str, Any]:
    """Use DuckDuckGo Instant Answer JSON as a cheap fallback."""
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        logger.debug("DuckDuckGo instant failed: %s", exc)
        return {}

def search_duckduckgo_html(query: str, top_k: int = 5) -> List[Dict[str, str]]:
    """Scrape DuckDuckGo HTML search results for lightweight web search.

    Returns list of dicts: {'title', 'url', 'snippet'}.
    """
    results: List[Dict[str, str]] = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; OpenJarvis/1.0)"}
        r = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Results anchors are 'a.result__a' or divs with class 'result'
        for a in soup.select("a.result__a")[:top_k]:
            title = a.get_text(strip=True)
            href = a.get("href")
            snippet = ""
            parent = a.find_parent("div", class_="result")
            if parent:
                snippet_el = parent.select_one(".result__snippet")
                snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
            results.append({"title": title, "url": href, "snippet": snippet})
        if results:
            return results
    except Exception as exc:
        logger.debug("DDG HTML search failed: %s", exc)

    # Fallback to instant answer (not full SERP)
    inst = _duckduckgo_instant(query)
    abstract = inst.get("AbstractText") or inst.get("Answer") or ""
    if abstract:
        results.append({"title": "DuckDuckGo Instant Answer", "url": "", "snippet": abstract})
    return results

def web_search(query: str, top_k: int = 5) -> List[Dict[str, str]]:
    """Public entry: returns a list of search result dicts."""
    return search_duckduckgo_html(query, top_k=top_k)
