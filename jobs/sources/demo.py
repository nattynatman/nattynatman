"""Demo / seed data — realistic sample jobs so the UI is never empty.

Shown when all live sources return nothing (e.g. network unavailable, first load).
These are representative of the kinds of roles JobRadar surfaces.
"""

from .base import Job, score_job

SOURCE = "demo"
LABEL = "Demo (sample)"

_SEED: list[dict] = [
    {
        "id": "demo-001",
        "title": "Product Marketing Manager — Platform",
        "company": "Canva",
        "location": "Sydney, AU / Remote",
        "url": "https://www.canva.com/careers/",
        "description": (
            "Canva is looking for a Product Marketing Manager to lead GTM strategy for our "
            "B2B platform offering. You'll own positioning, messaging, and launch execution "
            "for new product lines targeting enterprise and SMB markets. "
            "Background in SaaS or marketplace businesses strongly preferred."
        ),
        "salary": "AUD 130,000–165,000",
        "remote": True,
        "tags": ["product marketing", "b2b", "saas", "gtm", "startup"],
        "posted_at": "2026-02-25T00:00:00Z",
    },
    {
        "id": "demo-002",
        "title": "Growth Marketing Lead",
        "company": "Afterpay",
        "location": "Melbourne, AU",
        "url": "https://www.afterpay.com/en-AU/careers",
        "description": (
            "Drive acquisition and retention growth across Afterpay's merchant and consumer "
            "segments. Own performance marketing, lifecycle campaigns, and experimentation. "
            "Strong ecommerce and marketplace background highly valued. "
            "Will work cross-functionally with Product and Data."
        ),
        "salary": "AUD 120,000–145,000",
        "remote": False,
        "tags": ["growth marketing", "ecommerce", "performance marketing", "fintech"],
        "posted_at": "2026-02-20T00:00:00Z",
    },
    {
        "id": "demo-003",
        "title": "B2B Marketing Manager",
        "company": "Shopify",
        "location": "Remote (APAC)",
        "url": "https://www.shopify.com/careers",
        "description": (
            "Join Shopify's merchant marketing team to develop and execute B2B campaigns "
            "targeting mid-market and enterprise merchants. You'll create content, "
            "drive webinar programs, and own demand generation for Shopify Plus. "
            "Strong understanding of ecommerce platforms required."
        ),
        "salary": "USD 95,000–130,000",
        "remote": True,
        "tags": ["b2b marketing", "demand generation", "ecommerce", "saas"],
        "posted_at": "2026-02-18T00:00:00Z",
    },
    {
        "id": "demo-004",
        "title": "Head of Marketing — APAC",
        "company": "Algolia",
        "location": "Sydney, AU / Remote",
        "url": "https://www.algolia.com/careers",
        "description": (
            "Algolia is hiring a Head of Marketing for APAC to own regional GTM. "
            "You'll build and manage a team, drive pipeline through events, content, "
            "and digital campaigns, and partner closely with Sales. "
            "Experience in B2B SaaS or developer tools strongly preferred."
        ),
        "salary": "AUD 160,000–200,000",
        "remote": True,
        "tags": ["b2b", "saas", "head of marketing", "apac", "startup"],
        "posted_at": "2026-02-15T00:00:00Z",
    },
    {
        "id": "demo-005",
        "title": "Demand Generation Manager",
        "company": "Atlassian",
        "location": "Sydney, AU",
        "url": "https://www.atlassian.com/company/careers",
        "description": (
            "Own and execute multi-channel demand generation programs for Atlassian's "
            "enterprise segment. Drive pipeline through paid media, content syndication, "
            "webinars, and marketing automation. Work closely with SDR and Sales teams. "
            "Strong data orientation and B2B experience required."
        ),
        "salary": "AUD 115,000–145,000",
        "remote": False,
        "tags": ["demand generation", "demand gen", "b2b", "enterprise", "saas"],
        "posted_at": "2026-02-12T00:00:00Z",
    },
    {
        "id": "demo-006",
        "title": "Senior Growth Marketer",
        "company": "Rokt",
        "location": "Sydney / New York / Remote",
        "url": "https://rokt.com/careers/",
        "description": (
            "Rokt — the ecommerce technology company — is growing its marketing team. "
            "We're looking for a Senior Growth Marketer to own paid acquisition, SEO, "
            "and conversion optimisation. Deep ecommerce, marketplace, or retail tech "
            "experience is a big plus. Series D company, scaling fast."
        ),
        "salary": "AUD 125,000–155,000",
        "remote": True,
        "tags": ["growth marketing", "ecommerce", "marketplace", "series d", "startup"],
        "posted_at": "2026-02-10T00:00:00Z",
    },
    {
        "id": "demo-007",
        "title": "Partner Marketing Manager",
        "company": "Stripe",
        "location": "Remote (APAC)",
        "url": "https://stripe.com/jobs",
        "description": (
            "Develop and execute co-marketing initiatives with Stripe's ecosystem of "
            "platform and integration partners in APAC. Create joint campaigns, "
            "manage MDF budgets, and measure partner-sourced pipeline. "
            "Fintech, payments, or marketplace experience valued."
        ),
        "salary": "USD 100,000–140,000",
        "remote": True,
        "tags": ["partner marketing", "b2b", "marketplace", "fintech", "saas"],
        "posted_at": "2026-02-08T00:00:00Z",
    },
    {
        "id": "demo-008",
        "title": "Content Marketing Manager — B2B",
        "company": "Culture Amp",
        "location": "Melbourne, AU / Remote",
        "url": "https://www.cultureamp.com/about/careers",
        "description": (
            "Culture Amp is looking for a Content Marketing Manager to drive thought "
            "leadership and inbound demand for our people management platform. "
            "You'll own the editorial calendar, SEO content strategy, and work closely "
            "with demand gen on content distribution. B2B SaaS background preferred."
        ),
        "salary": "AUD 105,000–130,000",
        "remote": True,
        "tags": ["content marketing", "b2b", "saas", "seo", "startup"],
        "posted_at": "2026-02-05T00:00:00Z",
    },
]


async def fetch(client) -> list[Job]:
    jobs = []
    for item in _SEED:
        job = Job(
            id=Job.make_id(SOURCE, item["id"]),
            title=item["title"],
            company=item["company"],
            location=item["location"],
            url=item["url"],
            source=SOURCE,
            source_label=LABEL,
            description=item["description"],
            salary=item.get("salary"),
            remote=item.get("remote", False),
            tags=item.get("tags", []),
            posted_at=item.get("posted_at", ""),
        )
        job.relevance_score = score_job(job)
        jobs.append(job)
    return jobs
