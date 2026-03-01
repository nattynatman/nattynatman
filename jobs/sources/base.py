"""Shared Job model and relevance scoring for the persona."""

from __future__ import annotations

import hashlib
from typing import Optional
from pydantic import BaseModel


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    url: str
    source: str           # machine key e.g. "remotive"
    source_label: str     # display name e.g. "Remotive"
    description: str
    salary: Optional[str] = None
    remote: bool = False
    tags: list[str] = []
    posted_at: Optional[str] = None
    relevance_score: float = 0.0
    logo_url: Optional[str] = None

    @staticmethod
    def make_id(source: str, raw_id: str | int) -> str:
        return hashlib.md5(f"{source}:{raw_id}".encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Relevance scoring — tuned for:
#   Retail marketing specialist @ eBay → tech / startup / B2B roles
# ---------------------------------------------------------------------------
_HIGH_VALUE = [
    ("product marketing", 3.5),
    ("product marketer", 3.5),
    ("b2b marketing", 3.0),
    ("growth marketing", 3.0),
    ("demand generation", 3.0),
    ("demand gen", 3.0),
    ("marketplace marketing", 3.0),
    ("ecommerce marketing", 2.5),
    ("e-commerce marketing", 2.5),
    ("partner marketing", 2.5),
    ("field marketing", 2.5),
    ("marketing manager", 2.0),
    ("marketing lead", 2.0),
    ("marketing specialist", 2.0),
    ("head of marketing", 2.0),
]

_CONTEXT_BOOST = [
    ("startup", 1.5),
    ("saas", 1.5),
    ("b2b", 1.5),
    ("series a", 1.5),
    ("series b", 1.5),
    ("series c", 1.0),
    ("venture", 1.0),
    ("ecommerce", 1.5),
    ("e-commerce", 1.5),
    ("marketplace", 1.5),
    ("platform", 0.5),
    ("software", 0.5),
    ("tech", 0.5),
]

_GENERAL_MARKETING = [
    ("digital marketing", 1.0),
    ("content marketing", 1.0),
    ("brand marketing", 1.0),
    ("marketing", 0.5),
]

_PENALTIES = [
    ("medical", -2.0),
    ("healthcare", -2.0),
    ("clinical", -2.0),
    ("real estate", -2.0),
    ("construction", -2.0),
    ("mining", -2.0),
    ("accounting", -1.5),
    ("insurance", -1.5),
    # Non-tech retail without an ecommerce angle
    ("brick and mortar", -2.0),
    ("grocery", -1.5),
    ("supermarket", -1.5),
]


def score_job(job: Job) -> float:
    text = f"{job.title} {job.description} {' '.join(job.tags)}".lower()

    score = 0.0
    for phrase, pts in _HIGH_VALUE:
        if phrase in text:
            score += pts
    for phrase, pts in _CONTEXT_BOOST:
        if phrase in text:
            score += pts
    for phrase, pts in _GENERAL_MARKETING:
        if phrase in text:
            score += pts
    for phrase, pts in _PENALTIES:
        if phrase in text:
            score += pts  # pts are negative

    # Boost remote jobs (flexible for someone transitioning)
    if job.remote:
        score += 0.5

    return round(max(0.0, score), 2)
