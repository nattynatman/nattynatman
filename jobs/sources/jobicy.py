"""Jobicy — free remote jobs API, no auth required."""

import httpx
from .base import Job, score_job

SOURCE = "jobicy"
LABEL = "Jobicy"
BASE_URL = "https://jobicy.com/api/v2/remote-jobs"


async def fetch(client: httpx.AsyncClient) -> list[Job]:
    jobs: list[Job] = []
    try:
        r = await client.get(
            BASE_URL,
            params={"count": 50, "tag": "marketing", "industry": "tech"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return jobs

    for item in data.get("jobs", []):
        salary_min = item.get("annualSalaryMin")
        salary_max = item.get("annualSalaryMax")
        currency = item.get("salaryCurrency", "USD")
        if salary_min and salary_max:
            salary = f"{currency} {salary_min:,}–{salary_max:,}"
        elif salary_min:
            salary = f"{currency} {salary_min:,}+"
        else:
            salary = None

        geo = item.get("jobGeo", "") or "Remote"
        tags = item.get("jobIndustry", []) or []
        if isinstance(tags, str):
            tags = [tags]

        job = Job(
            id=Job.make_id(SOURCE, item.get("id", item.get("url", ""))),
            title=item.get("jobTitle", ""),
            company=item.get("companyName", "Unknown"),
            location=geo,
            url=item.get("url", ""),
            source=SOURCE,
            source_label=LABEL,
            description=(item.get("jobExcerpt") or item.get("jobDescription") or "")[:800],
            salary=salary,
            remote=True,
            tags=[t.lower() for t in tags if isinstance(t, str)],
            posted_at=item.get("pubDate", ""),
            logo_url=item.get("companyLogo", None),
        )
        job.relevance_score = score_job(job)
        jobs.append(job)

    return jobs
