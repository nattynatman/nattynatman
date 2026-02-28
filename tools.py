"""Tool implementations for the competitor insights agent."""

import httpx
from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 8) -> list[dict]:
    """Search the web using DuckDuckGo."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
    return results


def fetch_webpage(url: str, max_chars: int = 8000) -> str:
    """Fetch and return the text content of a webpage."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            text = response.text

        # Strip HTML tags with a simple approach
        import re
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
        text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]
    except Exception as e:
        return f"Error fetching {url}: {e}"


# Tool schemas for Claude's tool_use API
TOOL_SCHEMAS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for information about AI competitors, market trends, "
            "product features, pricing, funding, and news. Use targeted queries for "
            "best results (e.g. 'Voiceflow pricing 2025', 'n8n vs Relevance AI')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 8, max 15).",
                    "default": 8,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_webpage",
        "description": (
            "Fetch the content of a specific URL (e.g. a competitor's pricing page, "
            "blog post, or product announcement). Useful for getting detailed info "
            "beyond what search snippets provide."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch.",
                },
            },
            "required": ["url"],
        },
    },
]


def execute_tool(name: str, inputs: dict) -> str:
    """Dispatch and execute a tool by name, returning a string result."""
    if name == "web_search":
        results = web_search(
            query=inputs["query"],
            max_results=min(inputs.get("max_results", 8), 15),
        )
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r['title']}\nURL: {r['url']}\n{r['snippet']}\n")
        return "\n".join(lines)

    elif name == "fetch_webpage":
        return fetch_webpage(url=inputs["url"])

    else:
        return f"Unknown tool: {name}"
