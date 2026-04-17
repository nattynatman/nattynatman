"""HN 'Who is Hiring?' — high-signal startup jobs via Algolia HN search API."""

from __future__ import annotations
import re
import httpx
from .base import Job, score_job

SOURCE = "hn_hiring"
LABEL = "HN Who's Hiring"
ALGOLIA = "https://hn.algolia.com/api/v1"

MARKETING_KEYWORDS = [
    "marketing", "growth", "demand generation", "demand gen",
    "product marketing", "brand", "comms", "communications",
    "b2b marketing", "content marketing",
]


async def _get_latest_thread_id(client: httpx.AsyncClient) -> int | None:
    """Find the most recent 'Ask HN: Who is hiring?' story ID."""
    try:
        r = await client.get(
            f"{ALGOLIA}/search",
            params={
                "query": "Ask HN: Who is hiring?",
                "tags": "ask_hn",
                "hitsPerPage": 5,
            },
            timeout=10,
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
        # Filter for the canonical monthly post (high points, author=whoishiring)
        for hit in hits:
            if hit.get("author") == "whoishiring" and "who is hiring" in hit.get("title", "").lower():
                return int(hit["objectID"])
    except Exception:
        pass
    return None


def _extract_fields(text: str) -> dict:
    """Best-effort extraction of company, location, remote, salary from HN comment."""
    # HN comments are typically: "Company | Role | Location | Remote? | Salary | URL"
    parts = [p.strip() for p in re.split(r"\s*\|\s*", text.split("\n")[0]) if p.strip()]

    company = parts[0] if parts else "Unknown"
    role_hint = parts[1] if len(parts) > 1 else ""
    location = "Unknown"
    salary = None
    remote = False

    for part in parts[2:]:
        low = part.lower()
        if "remote" in low:
            remote = True
            location = part
        elif re.search(r"\$[\d,]+|\d+k", low):
            salary = part
        elif re.match(r"[A-Z][a-z]", part) and len(part) < 50 and not location:
            location = part

    return {
        "company": company,
        "role_hint": role_hint,
        "location": location or "Unknown",
        "salary": salary,
        "remote": remote,
    }


async def fetch(client: httpx.AsyncClient) -> list[Job]:
    jobs: list[Job] = []

    story_id = await _get_latest_thread_id(client)
    if not story_id:
        return jobs

    # Search comments on the thread for marketing-adjacent roles
    for keyword in MARKETING_KEYWORDS[:6]:  # limit API calls
        try:
            r = await client.get(
                f"{ALGOLIA}/search",
                params={
                    "query": keyword,
                    "tags": f"comment,story_{story_id}",
                    "hitsPerPage": 20,
                    "restrictSearchableAttributes": "comment_text",
                },
                timeout=10,
            )
            r.raise_for_status()
            hits = r.json().get("hits", [])
        except Exception:
            continue

        for hit in hits:
            raw_text = hit.get("comment_text", "") or ""
            # Strip HTML tags (HN API returns basic HTML)
            clean = re.sub(r"<[^>]+>", " ", raw_text).strip()
            if not clean:
                continue

            # Skip if this comment doesn't actually mention a marketing role
            if not any(kw in clean.lower() for kw in MARKETING_KEYWORDS):
                continue

            fields = _extract_fields(clean)
            hn_url = f"https://news.ycombinator.com/item?id={hit['objectID']}"

            job = Job(
                id=Job.make_id(SOURCE, hit["objectID"]),
                title=fields["role_hint"] or "Marketing Role",
                company=fields["company"],
                location=fields["location"],
                url=hn_url,
                source=SOURCE,
                source_label=LABEL,
                description=clean[:800],
                salary=fields["salary"],
                remote=fields["remote"],
                tags=["startup", "hn"],
                posted_at=hit.get("created_at", ""),
            )
            job.relevance_score = score_job(job)
            jobs.append(job)

    # Deduplicate by job id
    seen: set[str] = set()
    deduped = []
    for j in jobs:
        if j.id not in seen:
            seen.add(j.id)
            deduped.append(j)

    return deduped
