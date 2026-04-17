"""Claude-powered job source — uses the Anthropic API to synthesise realistic,
current marketing-in-tech job listings for the persona.

Works anywhere the ANTHROPIC_API_KEY is set (including in sandboxed environments
where external job board APIs are blocked).
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone

try:
    import anthropic as _anthropic
except ImportError:
    _anthropic = None  # type: ignore

from .base import Job, score_job

SOURCE = "claude_ai"
LABEL = "Claude AI (synthesised)"

_PROMPT = """\
You are a specialist tech recruiter with deep knowledge of the current (early 2026)
job market in Australia and globally.

Generate 14 realistic, current-style job listings for this candidate profile:

CANDIDATE:
- Current role: Retail Marketing Specialist at eBay (AU)
- Background: ecommerce, marketplace platforms, digital marketing, B2B partnerships
- Target: transition into tech startups, scale-ups, or established tech/SaaS companies
- Ideal roles: product marketing, growth marketing, B2B marketing, demand generation,
  ecommerce/marketplace marketing, partner marketing
- Seniority: mid-level to senior (not entry-level, not C-suite)
- Location preference: AU-based or fully remote

Use REAL companies that actually hire for these roles. Mix of:
- Global tech companies with AU offices (Shopify, Stripe, Atlassian, etc.)
- AU tech scale-ups (Canva, Afterpay, Rokt, Culture Amp, SafetyCulture, etc.)
- B2B SaaS startups
- Well-funded AI companies with marketing needs
Include a mix of AU-based, APAC remote, and global remote roles.

Return ONLY a JSON array (no markdown, no explanation) with this exact schema per item:
{
  "title": "Job Title",
  "company": "Company Name",
  "location": "City, Country or Remote",
  "url": "https://careers.company.com or https://company.com/jobs (real careers URL)",
  "description": "2-3 sentence description of the role and what makes it a good fit",
  "salary": "AUD/USD XX,000–XX,000 or null",
  "remote": true or false,
  "tags": ["tag1", "tag2", "tag3"],
  "days_ago": 1 to 14
}

Make descriptions specific and compelling. Tags should include role type, company type,
and skills (e.g. "product marketing", "b2b", "saas", "ecommerce", "startup").
Salary ranges should be realistic for 2026 AU/US market rates."""


async def fetch(client_unused) -> list[Job]:  # noqa: ARG001
    if _anthropic is None:
        return []
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []

    try:
        ai = _anthropic.Anthropic(api_key=api_key)
        response = ai.messages.create(
            model="claude-haiku-4-5-20251001",  # fast + cheap for this use-case
            max_tokens=4096,
            messages=[{"role": "user", "content": _PROMPT}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        items: list[dict] = json.loads(raw)
    except Exception:
        return []

    jobs: list[Job] = []
    now = datetime.now(timezone.utc)

    for i, item in enumerate(items):
        try:
            days_ago = int(item.get("days_ago", 3))
            posted = (now - timedelta(days=days_ago)).isoformat()

            job = Job(
                id=Job.make_id(SOURCE, f"{item.get('company', '')}-{item.get('title', '')}-{i}"),
                title=item.get("title", ""),
                company=item.get("company", "Unknown"),
                location=item.get("location", "Remote"),
                url=item.get("url", ""),
                source=SOURCE,
                source_label=LABEL,
                description=item.get("description", ""),
                salary=item.get("salary") or None,
                remote=bool(item.get("remote", False)),
                tags=[t.lower() for t in (item.get("tags") or []) if isinstance(t, str)],
                posted_at=posted,
            )
            job.relevance_score = score_job(job)
            jobs.append(job)
        except Exception:
            continue

    return jobs
