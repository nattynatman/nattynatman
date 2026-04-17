"""
JobRadar — self-contained job dashboard.

No scraping, no external APIs. Just a rich curated dataset of
real marketing-in-tech roles, served with a fast in-memory search.

Run:  uvicorn jobs.app:app --reload --port 8000
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from .data import JOBS, Job

app = FastAPI(title="JobRadar", docs_url=None, redoc_url=None)

# ── API ────────────────────────────────────────────────────────────────────

@app.get("/api/jobs")
def get_jobs(
    q: Optional[str] = Query(None),
    role: Optional[str] = Query(None),     # filter chip: "pmm", "growth", "b2b", "content"
    remote_only: bool = Query(False),
    min_score: float = Query(0.0),
    sort: str = Query("score"),            # "score" | "date" | "salary"
):
    jobs = list(JOBS)

    if remote_only:
        jobs = [j for j in jobs if j.remote]

    if role:
        tag_map = {
            "pmm":     ["product marketing"],
            "growth":  ["growth marketing", "growth"],
            "b2b":     ["b2b", "b2b marketing", "demand generation", "demand gen"],
            "content": ["content marketing", "content"],
            "partner": ["partner marketing"],
            "brand":   ["brand", "brand marketing"],
        }
        tags = tag_map.get(role, [role])
        jobs = [
            j for j in jobs
            if any(t in j.tags or t in j.title.lower() or t in j.description.lower()
                   for t in tags)
        ]

    if min_score > 0:
        jobs = [j for j in jobs if j.score >= min_score]

    if q:
        ql = q.lower()
        ql_words = ql.split()
        def matches(j: Job) -> bool:
            text = f"{j.title} {j.company} {j.location} {' '.join(j.tags)} {j.description}".lower()
            return all(w in text for w in ql_words)
        jobs = [j for j in jobs if matches(j)]

    if sort == "date":
        jobs.sort(key=lambda j: j.days_ago)
    elif sort == "salary":
        jobs.sort(key=lambda j: j.salary_sort, reverse=True)
    else:
        jobs.sort(key=lambda j: j.score, reverse=True)

    # Tag cloud counts (unfiltered by role, for filter UI)
    tag_counts = {}
    for j in JOBS:
        for t in j.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    return {
        "total": len(jobs),
        "total_all": len(JOBS),
        "jobs": [j.to_dict() for j in jobs],
        "tag_counts": dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:20]),
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    for j in JOBS:
        if j.id == job_id:
            return j.to_dict()
    return {"error": "not found"}, 404


# ── Frontend ───────────────────────────────────────────────────────────────

_HTML = Path(__file__).parent / "templates" / "index.html"

@app.get("/", response_class=HTMLResponse)
def root():
    return _HTML.read_text()
