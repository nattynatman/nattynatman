"""JobRadar — marketing roles in tech, curated for Natty."""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .sources import ALL_SOURCES
from .sources.base import Job

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="JobRadar", docs_url=None, redoc_url=None)

# ---------------------------------------------------------------------------
# Simple in-memory cache
# ---------------------------------------------------------------------------
_CACHE: dict[str, list[Job]] = {}   # source -> jobs
_CACHE_TS: dict[str, float] = {}    # source -> unix timestamp
CACHE_TTL = 30 * 60  # 30 minutes


def _cache_key(source_name: str) -> str:
    return source_name


def _is_fresh(source_name: str) -> bool:
    ts = _CACHE_TS.get(source_name, 0)
    return (time.time() - ts) < CACHE_TTL


# ---------------------------------------------------------------------------
# Job fetching
# ---------------------------------------------------------------------------
async def _fetch_source(source, client: httpx.AsyncClient) -> tuple[str, list[Job]]:
    try:
        jobs = await source.fetch(client)
    except Exception:
        jobs = []
    return source.SOURCE, jobs


async def fetch_all_jobs(force: bool = False) -> list[Job]:
    all_jobs: list[Job] = []

    sources_to_fetch = [
        s for s in ALL_SOURCES
        if force or not _is_fresh(s.SOURCE)
    ]

    if sources_to_fetch:
        async with httpx.AsyncClient(
            headers={"User-Agent": "JobRadar/1.0 (+https://github.com/nattynatman)"},
            follow_redirects=True,
        ) as client:
            results = await asyncio.gather(
                *[_fetch_source(s, client) for s in sources_to_fetch],
                return_exceptions=False,
            )

        for source_key, jobs in results:
            _CACHE[source_key] = jobs
            _CACHE_TS[source_key] = time.time()

    # Merge cached results from all sources (excluding demo/fallback sources first)
    FALLBACK_SOURCES = {"demo"}
    live_sources = [s for s in ALL_SOURCES if s.SOURCE not in FALLBACK_SOURCES]
    fallback_sources = [s for s in ALL_SOURCES if s.SOURCE in FALLBACK_SOURCES]

    live_jobs: list[Job] = []
    seen_ids: set[str] = set()
    for source in live_sources:
        for job in _CACHE.get(source.SOURCE, []):
            if job.id not in seen_ids:
                seen_ids.add(job.id)
                live_jobs.append(job)

    # Only include demo fallback data if all live sources returned nothing
    if not live_jobs:
        for source in fallback_sources:
            for job in _CACHE.get(source.SOURCE, []):
                if job.id not in seen_ids:
                    seen_ids.add(job.id)
                    all_jobs.append(job)
    else:
        all_jobs = live_jobs

    all_jobs.sort(key=lambda j: j.relevance_score, reverse=True)
    return all_jobs


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.get("/api/jobs")
async def get_jobs(
    refresh: bool = Query(False),
    q: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    remote_only: bool = Query(False),
    min_score: float = Query(0.0),
):
    jobs = await fetch_all_jobs(force=refresh)

    if remote_only:
        jobs = [j for j in jobs if j.remote]
    if source:
        jobs = [j for j in jobs if j.source == source]
    if min_score > 0:
        jobs = [j for j in jobs if j.relevance_score >= min_score]
    if q:
        ql = q.lower()
        jobs = [
            j for j in jobs
            if ql in j.title.lower()
            or ql in j.company.lower()
            or ql in j.description.lower()
            or any(ql in tag for tag in j.tags)
        ]

    cache_ages = {
        s.SOURCE: round(time.time() - _CACHE_TS.get(s.SOURCE, time.time()))
        for s in ALL_SOURCES
    }
    source_counts = {}
    for j in jobs:
        source_counts[j.source] = source_counts.get(j.source, 0) + 1

    return {
        "total": len(jobs),
        "jobs": [j.model_dump() for j in jobs],
        "cache_ages_seconds": cache_ages,
        "source_counts": source_counts,
    }


@app.get("/api/sources")
async def get_sources():
    return {
        "sources": [
            {
                "key": s.SOURCE,
                "label": s.LABEL,
                "cached": _is_fresh(s.SOURCE),
                "count": len(_CACHE.get(s.SOURCE, [])),
                "needs_key": s.SOURCE == "adzuna",
                "configured": s.SOURCE != "adzuna" or bool(
                    os.environ.get("ADZUNA_APP_ID")
                ),
            }
            for s in ALL_SOURCES
        ]
    }


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
_TEMPLATE_PATH = Path(__file__).parent / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse)
async def root():
    return _TEMPLATE_PATH.read_text()
