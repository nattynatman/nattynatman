"""Adzuna — free API (250 req/day), covers AU, US, UK, and more.

Register at https://developer.adzuna.com/ to get APP_ID and APP_KEY.
Set in your .env:
    ADZUNA_APP_ID=your_app_id
    ADZUNA_APP_KEY=your_app_key
    ADZUNA_COUNTRY=au   # au, us, gb, ca, nz, etc.
"""

import os
import httpx
from .base import Job, score_job

SOURCE = "adzuna"
LABEL = "Adzuna"
BASE_URL = "https://api.adzuna.com/v1/api/jobs"

SEARCHES = [
    "marketing manager tech",
    "product marketing saas",
    "b2b marketing",
    "growth marketing startup",
    "demand generation",
]


def _is_configured() -> bool:
    return bool(os.environ.get("ADZUNA_APP_ID") and os.environ.get("ADZUNA_APP_KEY"))


async def fetch(client: httpx.AsyncClient) -> list[Job]:
    if not _is_configured():
        return []

    app_id = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]
    country = os.environ.get("ADZUNA_COUNTRY", "au").lower()

    jobs: list[Job] = []
    seen: set[str] = set()

    for query in SEARCHES:
        try:
            r = await client.get(
                f"{BASE_URL}/{country}/search/1",
                params={
                    "app_id": app_id,
                    "app_key": app_key,
                    "results_per_page": 20,
                    "what": query,
                    "content-type": "application/json",
                },
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
        except Exception:
            continue

        for item in data.get("results", []):
            raw_id = str(item.get("id", ""))
            jid = Job.make_id(SOURCE, raw_id)
            if jid in seen:
                continue
            seen.add(jid)

            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            salary = None
            if salary_min and salary_max:
                salary = f"{country.upper()} ${int(salary_min):,}–${int(salary_max):,}"
            elif salary_min:
                salary = f"{country.upper()} ${int(salary_min):,}+"

            location = (item.get("location") or {}).get("display_name", "Unknown")

            job = Job(
                id=jid,
                title=item.get("title", ""),
                company=(item.get("company") or {}).get("display_name", "Unknown"),
                location=location,
                url=item.get("redirect_url", ""),
                source=SOURCE,
                source_label=f"{LABEL} ({country.upper()})",
                description=(item.get("description") or "")[:800],
                salary=salary,
                remote="remote" in (item.get("title") or "").lower(),
                tags=[item.get("category", {}).get("label", "").lower()],
                posted_at=item.get("created", ""),
            )
            job.relevance_score = score_job(job)
            jobs.append(job)

    return jobs
