"""The Muse — free public jobs API, strong on startup/tech companies."""

import httpx
from .base import Job, score_job

SOURCE = "themuse"
LABEL = "The Muse"
BASE_URL = "https://www.themuse.com/api/public/jobs"
CATEGORIES = ["Marketing & PR", "Business Development", "Data & Analytics"]
LEVELS = ["Mid Level", "Senior Level", "Management"]


async def _fetch_page(
    client: httpx.AsyncClient,
    category: str,
    page: int,
) -> list[dict]:
    try:
        r = await client.get(
            BASE_URL,
            params={"category": category, "page": page, "level": LEVELS},
            timeout=15,
        )
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []


async def fetch(client: httpx.AsyncClient) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()

    for category in CATEGORIES:
        items = await _fetch_page(client, category, 1)
        for item in items:
            raw_id = str(item.get("id", ""))
            jid = Job.make_id(SOURCE, raw_id)
            if jid in seen:
                continue
            seen.add(jid)

            locations = item.get("locations", []) or []
            location_str = ", ".join(loc.get("name", "") for loc in locations) or "Flexible"
            is_remote = any(
                "remote" in (loc.get("name", "") or "").lower() for loc in locations
            )

            levels = [lv.get("name", "") for lv in (item.get("levels") or [])]
            tags = [cat.get("name", "") for cat in (item.get("categories") or [])]
            tags += levels

            company = item.get("company", {}) or {}

            job = Job(
                id=jid,
                title=item.get("name", ""),
                company=company.get("name", "Unknown"),
                location=location_str,
                url=(item.get("refs") or {}).get("landing_page", ""),
                source=SOURCE,
                source_label=LABEL,
                description=(item.get("contents") or "")[:800],
                remote=is_remote,
                tags=[t.lower() for t in tags if t],
                posted_at=item.get("publication_date", ""),
            )
            job.relevance_score = score_job(job)
            jobs.append(job)

    return jobs
