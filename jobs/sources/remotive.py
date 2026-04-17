"""Remotive.io — free remote tech jobs API, no auth required."""

import httpx
from .base import Job, score_job

SOURCE = "remotive"
LABEL = "Remotive"
BASE_URL = "https://remotive.com/api/remote-jobs"
CATEGORIES = ["marketing", "product"]


async def fetch(client: httpx.AsyncClient) -> list[Job]:
    jobs: list[Job] = []
    for category in CATEGORIES:
        try:
            r = await client.get(
                BASE_URL,
                params={"category": category, "limit": 100},
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
        except Exception:
            continue

        for item in data.get("jobs", []):
            title = item.get("title", "")
            description = item.get("description", "")
            tags = item.get("tags", []) or []

            location = item.get("candidate_required_location", "") or "Remote"
            salary = item.get("salary") or None

            job = Job(
                id=Job.make_id(SOURCE, item.get("id", item.get("url", title))),
                title=title,
                company=item.get("company_name", "Unknown"),
                location=location,
                url=item.get("url", ""),
                source=SOURCE,
                source_label=LABEL,
                description=description[:800],
                salary=salary,
                remote=True,
                tags=[t.lower() for t in tags if isinstance(t, str)],
                posted_at=item.get("publication_date", ""),
                logo_url=item.get("company_logo", None),
            )
            job.relevance_score = score_job(job)
            jobs.append(job)

    return jobs
