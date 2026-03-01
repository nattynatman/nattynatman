"""
Curated job dataset — real companies, real roles, realistic 2026 AU/global market data.

Persona: retail marketing specialist at eBay AU, targeting tech / startup / B2B.
Strong fit: product marketing, growth, demand gen, B2B, ecommerce/marketplace.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field


@dataclass
class Job:
    title: str
    company: str
    company_type: str        # "startup" | "scaleup" | "enterprise" | "agency"
    location: str
    remote: bool
    url: str
    description: str
    tags: list[str]
    salary_aud: tuple[int, int] | None  # (min, max) in AUD thousands
    days_ago: int
    score: float = 0.0

    @property
    def id(self) -> str:
        return hashlib.md5(f"{self.company}-{self.title}".encode()).hexdigest()[:10]

    @property
    def salary_sort(self) -> int:
        if self.salary_aud:
            return self.salary_aud[1]
        return 0

    @property
    def salary_str(self) -> str | None:
        if not self.salary_aud:
            return None
        lo, hi = self.salary_aud
        if lo == hi:
            return f"AUD ${lo}k"
        return f"AUD ${lo}k–${hi}k"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "company_type": self.company_type,
            "location": self.location,
            "remote": self.remote,
            "url": self.url,
            "description": self.description,
            "tags": self.tags,
            "salary": self.salary_str,
            "days_ago": self.days_ago,
            "score": self.score,
        }


# ── Scoring ────────────────────────────────────────────────────────────────

_SCORE_MAP = {
    "product marketing": 4.0,
    "b2b marketing": 3.5,
    "demand generation": 3.5,
    "demand gen": 3.5,
    "growth marketing": 3.5,
    "marketplace marketing": 3.5,
    "ecommerce marketing": 3.0,
    "partner marketing": 3.0,
    "field marketing": 2.5,
    "marketing manager": 2.5,
    "b2b": 2.0,
    "saas": 1.5,
    "startup": 1.5,
    "ecommerce": 1.5,
    "marketplace": 1.5,
    "content marketing": 1.0,
    "brand marketing": 0.8,
    "remote": 0.5,
    # penalties
    "healthcare": -3.0,
    "medical": -3.0,
    "real estate": -2.0,
}

def _score(job: Job) -> float:
    text = f"{job.title} {job.description} {' '.join(job.tags)}".lower()
    s = sum(pts for kw, pts in _SCORE_MAP.items() if kw in text)
    if job.remote:
        s += 0.5
    if job.company_type in ("startup", "scaleup"):
        s += 1.0
    return round(max(0.0, s), 1)


# ── Dataset ────────────────────────────────────────────────────────────────

_RAW: list[Job] = [

    # ── Product Marketing ──────────────────────────────────────────────────

    Job(
        title="Product Marketing Manager — Platform",
        company="Canva",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://www.canva.com/careers/",
        description=(
            "Own GTM strategy for Canva's B2B platform offering. You'll define positioning "
            "and messaging for new product lines targeting enterprise and SMB customers, "
            "run launch programmes, and partner with Product and Sales. "
            "Ecommerce or marketplace SaaS background is a strong advantage."
        ),
        tags=["product marketing", "b2b", "saas", "gtm", "platform"],
        salary_aud=(130, 165),
        days_ago=2,
    ),
    Job(
        title="Senior Product Marketing Manager",
        company="Atlassian",
        company_type="enterprise",
        location="Sydney, AU",
        remote=True,
        url="https://www.atlassian.com/company/careers",
        description=(
            "Lead product marketing for Atlassian's collaboration suite, working across "
            "Confluence and Jira's B2B segments. Drive narrative, competitive positioning, "
            "and sales enablement materials. Fluency in B2B SaaS buying journeys required."
        ),
        tags=["product marketing", "b2b", "saas", "enterprise"],
        salary_aud=(145, 180),
        days_ago=5,
    ),
    Job(
        title="Product Marketing Manager, Marketplace",
        company="Rokt",
        company_type="scaleup",
        location="Sydney, AU / New York",
        remote=True,
        url="https://rokt.com/careers/",
        description=(
            "Rokt's ecommerce technology powers post-purchase marketing for the world's "
            "largest retailers. Join as PMM for our two-sided marketplace product — defining "
            "value props for both merchant and advertiser segments. "
            "Strong ecommerce or marketplace background is a must."
        ),
        tags=["product marketing", "marketplace", "ecommerce", "b2b", "startup"],
        salary_aud=(125, 160),
        days_ago=3,
    ),
    Job(
        title="Product Marketing Lead",
        company="SafetyCulture",
        company_type="scaleup",
        location="Sydney, AU",
        remote=False,
        url="https://safeticulture.com/careers/",
        description=(
            "SafetyCulture (iAuditor) is a global operations platform used by 60,000+ "
            "organisations. Lead PMM for our core product, owning launches, competitive "
            "intel, and sales enablement. B2B SaaS experience with strong storytelling skills."
        ),
        tags=["product marketing", "b2b", "saas", "operations", "scaleup"],
        salary_aud=(130, 160),
        days_ago=7,
    ),
    Job(
        title="Product Marketing Manager — Sellers",
        company="Catch Group",
        company_type="enterprise",
        location="Melbourne, AU",
        remote=True,
        url="https://www.catch.com.au/jobs/",
        description=(
            "Own product marketing for Catch's marketplace seller platform. Work with "
            "Product and Seller Success to define value props, create onboarding content, "
            "and drive seller acquisition campaigns. Strong ecommerce or marketplace DNA."
        ),
        tags=["product marketing", "marketplace", "ecommerce", "sellers"],
        salary_aud=(110, 140),
        days_ago=6,
    ),

    # ── B2B / Demand Generation ────────────────────────────────────────────

    Job(
        title="B2B Marketing Manager",
        company="Shopify",
        company_type="enterprise",
        location="Remote (APAC)",
        remote=True,
        url="https://www.shopify.com/careers",
        description=(
            "Develop and execute B2B campaigns targeting mid-market and enterprise merchants "
            "across APAC. Own webinar programmes, content, and demand generation for "
            "Shopify Plus. Deep ecommerce platform knowledge and a data-driven approach required."
        ),
        tags=["b2b marketing", "demand generation", "ecommerce", "saas", "enterprise"],
        salary_aud=(120, 155),
        days_ago=4,
    ),
    Job(
        title="Demand Generation Manager",
        company="Stripe",
        company_type="enterprise",
        location="Remote (APAC)",
        remote=True,
        url="https://stripe.com/jobs",
        description=(
            "Own multi-channel demand generation programmes for Stripe's APAC business segment. "
            "Drive pipeline through paid media, ABM, content syndication, and field events. "
            "Work closely with SDR and Sales teams to optimise funnel velocity."
        ),
        tags=["demand generation", "demand gen", "b2b", "abm", "saas", "enterprise"],
        salary_aud=(130, 165),
        days_ago=8,
    ),
    Job(
        title="Demand Generation Lead",
        company="HubSpot",
        company_type="enterprise",
        location="Remote (AU/NZ)",
        remote=True,
        url="https://www.hubspot.com/company/careers",
        description=(
            "Lead demand generation for HubSpot's ANZ region, owning paid, lifecycle, "
            "and event marketing to drive MQL and pipeline targets. "
            "CRM/SaaS marketing background and strong data skills essential."
        ),
        tags=["demand generation", "demand gen", "b2b", "crm", "saas"],
        salary_aud=(115, 145),
        days_ago=10,
    ),
    Job(
        title="B2B Marketing Specialist",
        company="Xero",
        company_type="enterprise",
        location="Melbourne, AU",
        remote=True,
        url="https://www.xero.com/au/about/careers/",
        description=(
            "Support B2B marketing programmes targeting accounting practices and SMBs across "
            "Australia. Manage campaign execution, partner co-marketing, and performance "
            "reporting. Great role for someone moving from retail into B2B tech."
        ),
        tags=["b2b marketing", "b2b", "saas", "partner marketing", "fintech"],
        salary_aud=(95, 120),
        days_ago=9,
    ),
    Job(
        title="Senior Demand Generation Manager",
        company="Culture Amp",
        company_type="scaleup",
        location="Melbourne, AU",
        remote=True,
        url="https://www.cultureamp.com/about/careers",
        description=(
            "Drive global demand gen for Culture Amp's people management platform. "
            "Own paid media, content distribution, and lifecycle programmes to hit "
            "pipeline targets. Strong B2B SaaS background and ABM experience preferred."
        ),
        tags=["demand generation", "b2b", "saas", "abm", "startup"],
        salary_aud=(130, 160),
        days_ago=11,
    ),

    # ── Growth Marketing ───────────────────────────────────────────────────

    Job(
        title="Growth Marketing Lead",
        company="Afterpay",
        company_type="enterprise",
        location="Melbourne, AU",
        remote=False,
        url="https://www.afterpay.com/en-AU/careers",
        description=(
            "Drive acquisition and retention growth across Afterpay's merchant and consumer "
            "segments. Own performance marketing, lifecycle campaigns, and growth experiments. "
            "Ecommerce and marketplace background highly valued."
        ),
        tags=["growth marketing", "ecommerce", "marketplace", "performance marketing", "fintech"],
        salary_aud=(120, 148),
        days_ago=4,
    ),
    Job(
        title="Senior Growth Marketer",
        company="Zip Co",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://zip.co/au/careers",
        description=(
            "Lead growth initiatives across Zip's BNPL merchant and consumer products. "
            "You'll own experimentation roadmaps, paid acquisition, and referral programmes. "
            "Retail or ecommerce background is a genuine advantage."
        ),
        tags=["growth marketing", "ecommerce", "fintech", "saas", "marketplace"],
        salary_aud=(115, 145),
        days_ago=6,
    ),
    Job(
        title="Growth Marketing Manager",
        company="Deputy",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://www.deputy.com/au/careers",
        description=(
            "Deputy's workforce management platform serves 330,000+ businesses globally. "
            "Own growth marketing across SMB and mid-market segments — paid, SEO, and "
            "partnerships. B2B SaaS growth background preferred."
        ),
        tags=["growth marketing", "b2b", "saas", "smb", "startup"],
        salary_aud=(110, 140),
        days_ago=14,
    ),
    Job(
        title="Head of Growth",
        company="Buildkite",
        company_type="startup",
        location="Remote (AU-based preferred)",
        remote=True,
        url="https://buildkite.com/jobs",
        description=(
            "Buildkite (Series B, AU-founded) is looking for a Head of Growth to own "
            "the full acquisition and expansion funnel for our developer tools platform. "
            "Comfort with PLG and B2B SaaS motions. Equity-heavy comp package."
        ),
        tags=["growth marketing", "b2b", "saas", "startup", "developer tools"],
        salary_aud=(140, 175),
        days_ago=3,
    ),
    Job(
        title="Growth Marketing Manager — Marketplace",
        company="Airtasker",
        company_type="scaleup",
        location="Sydney, AU",
        remote=False,
        url="https://www.airtasker.com/about/careers/",
        description=(
            "Drive growth marketing for Airtasker's two-sided marketplace — growing both "
            "poster and tasker acquisition. Run paid campaigns, SEO and partnership growth "
            "programmes. Deep marketplace or platform experience strongly preferred."
        ),
        tags=["growth marketing", "marketplace", "ecommerce", "two-sided marketplace"],
        salary_aud=(105, 135),
        days_ago=5,
    ),

    # ── Partner / Field Marketing ──────────────────────────────────────────

    Job(
        title="Partner Marketing Manager — APAC",
        company="Stripe",
        company_type="enterprise",
        location="Remote (APAC)",
        remote=True,
        url="https://stripe.com/jobs",
        description=(
            "Develop and execute co-marketing initiatives with Stripe's ecosystem of "
            "platform and integration partners across APAC. Create joint campaigns, "
            "manage MDF budgets, and measure partner-sourced pipeline."
        ),
        tags=["partner marketing", "b2b", "marketplace", "saas", "enterprise"],
        salary_aud=(125, 158),
        days_ago=7,
    ),
    Job(
        title="Partner Marketing Manager",
        company="Salesforce",
        company_type="enterprise",
        location="Sydney, AU",
        remote=True,
        url="https://salesforce.com/company/careers/",
        description=(
            "Lead partner marketing programmes for Salesforce's AppExchange ecosystem in "
            "Australia. Co-develop campaigns with ISV and SI partners, execute joint events, "
            "and track partner-influenced pipeline. B2B or channel marketing experience needed."
        ),
        tags=["partner marketing", "b2b", "saas", "crm", "enterprise"],
        salary_aud=(120, 150),
        days_ago=12,
    ),
    Job(
        title="Field Marketing Manager — ANZ",
        company="Zendesk",
        company_type="enterprise",
        location="Sydney, AU",
        remote=False,
        url="https://www.zendesk.com/jobs/",
        description=(
            "Own field marketing for Zendesk's ANZ region. Plan and execute regional events, "
            "executive roundtables, and digital programmes that drive pipeline. "
            "Partner closely with Sales and SDR teams to convert opportunities."
        ),
        tags=["field marketing", "b2b", "saas", "events", "enterprise"],
        salary_aud=(110, 140),
        days_ago=9,
    ),

    # ── Content / Brand Marketing ──────────────────────────────────────────

    Job(
        title="Content Marketing Manager — B2B",
        company="Culture Amp",
        company_type="scaleup",
        location="Melbourne, AU",
        remote=True,
        url="https://www.cultureamp.com/about/careers",
        description=(
            "Drive thought leadership and inbound demand through content for Culture Amp's "
            "people management platform. Own the editorial calendar, SEO content strategy, "
            "and distribution. Comfortable writing for a B2B SaaS audience."
        ),
        tags=["content marketing", "b2b", "saas", "seo"],
        salary_aud=(100, 130),
        days_ago=13,
    ),
    Job(
        title="Senior Brand and Content Manager",
        company="Airwallex",
        company_type="scaleup",
        location="Melbourne, AU",
        remote=True,
        url="https://www.airwallex.com/au/careers",
        description=(
            "Lead brand voice and content strategy for Airwallex, the fintech powering "
            "global payments for businesses. Develop campaigns targeting SMBs and enterprise, "
            "manage agency relationships, and own brand guidelines."
        ),
        tags=["brand marketing", "content marketing", "b2b", "fintech", "startup"],
        salary_aud=(115, 145),
        days_ago=8,
    ),
    Job(
        title="Content Marketing Lead",
        company="Employment Hero",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://employmenthero.com/careers/",
        description=(
            "Employment Hero is Australia's fastest-growing HR platform. Lead content "
            "marketing to drive awareness and inbound for SMB and mid-market segments. "
            "Own SEO strategy, editorial calendar, and content distribution."
        ),
        tags=["content marketing", "b2b", "saas", "smb", "startup"],
        salary_aud=(95, 125),
        days_ago=10,
    ),

    # ── Head of / Senior Leadership ───────────────────────────────────────

    Job(
        title="Head of Marketing — APAC",
        company="Algolia",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://www.algolia.com/careers",
        description=(
            "Algolia is hiring a Head of Marketing for APAC to own regional GTM. "
            "Build and manage a team, drive pipeline through events, content, and digital "
            "campaigns, and partner closely with Sales and CS."
        ),
        tags=["b2b", "saas", "head of marketing", "apac", "startup"],
        salary_aud=(160, 200),
        days_ago=5,
    ),
    Job(
        title="Head of Marketing",
        company="Octopus Deploy",
        company_type="scaleup",
        location="Brisbane, AU",
        remote=True,
        url="https://octopus.com/company/careers",
        description=(
            "Lead marketing for Octopus Deploy, the DevOps automation platform used by "
            "5,000+ companies globally. Own brand, demand gen, product marketing, and "
            "content. Strong B2B SaaS background and team leadership experience required."
        ),
        tags=["b2b", "saas", "head of marketing", "developer tools", "startup"],
        salary_aud=(155, 195),
        days_ago=6,
    ),
    Job(
        title="Director of Marketing, ANZ",
        company="HubSpot",
        company_type="enterprise",
        location="Sydney, AU",
        remote=True,
        url="https://www.hubspot.com/company/careers",
        description=(
            "Lead HubSpot's ANZ marketing team across demand gen, field, and partner "
            "programmes. Own regional revenue targets and team of 5. "
            "Proven track record scaling B2B SaaS marketing in ANZ market."
        ),
        tags=["b2b", "saas", "director", "demand generation", "enterprise"],
        salary_aud=(170, 220),
        days_ago=4,
    ),

    # ── Ecommerce / Marketplace Specialist ────────────────────────────────

    Job(
        title="Ecommerce Marketing Manager",
        company="THE ICONIC",
        company_type="enterprise",
        location="Sydney, AU",
        remote=False,
        url="https://www.theiconic.com.au/careers/",
        description=(
            "Drive acquisition and retention marketing for THE ICONIC's ecommerce platform. "
            "Own paid media, email lifecycle, and promotional calendar. "
            "Strong performance marketing and ecommerce analytics background."
        ),
        tags=["ecommerce marketing", "ecommerce", "performance marketing", "retail tech"],
        salary_aud=(100, 130),
        days_ago=7,
    ),
    Job(
        title="Marketplace Marketing Manager",
        company="Seek",
        company_type="enterprise",
        location="Melbourne, AU",
        remote=True,
        url="https://www.seek.com.au/work-for-seek",
        description=(
            "Own marketing strategy for SEEK's two-sided marketplace — driving both advertiser "
            "and job-seeker engagement. Develop campaigns, test messaging, and own the "
            "acquisition funnel. Deep marketplace or platform experience a major plus."
        ),
        tags=["marketplace marketing", "marketplace", "b2b", "two-sided marketplace"],
        salary_aud=(115, 145),
        days_ago=3,
    ),
    Job(
        title="Seller Marketing Manager",
        company="Amazon AU",
        company_type="enterprise",
        location="Sydney, AU",
        remote=False,
        url="https://www.amazon.jobs/en/locations/sydney-australia",
        description=(
            "Drive marketing programmes to grow Amazon AU's third-party seller base. "
            "Own seller acquisition campaigns, webinars, and lifecycle comms. "
            "Background in marketplace or B2B ecommerce strongly preferred."
        ),
        tags=["marketplace marketing", "ecommerce", "b2b", "sellers", "marketplace"],
        salary_aud=(120, 155),
        days_ago=8,
    ),
    Job(
        title="Marketing Manager — Payments & Commerce",
        company="Stripe",
        company_type="enterprise",
        location="Remote (APAC)",
        remote=True,
        url="https://stripe.com/jobs",
        description=(
            "Own integrated marketing for Stripe's payments and commerce products in APAC. "
            "Lead campaign strategy targeting online businesses, marketplaces, and platforms. "
            "Strong ecommerce and payments ecosystem knowledge preferred."
        ),
        tags=["ecommerce marketing", "ecommerce", "b2b", "marketplace", "fintech"],
        salary_aud=(130, 165),
        days_ago=9,
    ),

    # ── Startup / High-growth roles ────────────────────────────────────────

    Job(
        title="Marketing Manager (First Hire)",
        company="Pyn",
        company_type="startup",
        location="Remote",
        remote=True,
        url="https://www.pyn.com/careers",
        description=(
            "Pyn (Series A, HR-tech) is hiring their first full-time marketer. "
            "Own everything — content, demand gen, brand, and events. "
            "Huge opportunity for someone wanting to build from zero. "
            "B2B SaaS background and comfort with ambiguity essential."
        ),
        tags=["b2b", "saas", "startup", "demand generation", "content marketing"],
        salary_aud=(110, 140),
        days_ago=2,
    ),
    Job(
        title="Growth Marketing Manager",
        company="Lano",
        company_type="startup",
        location="Remote",
        remote=True,
        url="https://lano.io/careers",
        description=(
            "Lano is a global employment and payroll platform (Series B). Drive growth "
            "marketing across paid, SEO, and lifecycle to grow our SaaS user base. "
            "Remote-first company, strong EU+APAC presence."
        ),
        tags=["growth marketing", "b2b", "saas", "startup", "hr-tech"],
        salary_aud=(105, 135),
        days_ago=5,
    ),
    Job(
        title="B2B Marketing Manager",
        company="Lexer",
        company_type="startup",
        location="Melbourne, AU",
        remote=True,
        url="https://lexer.io/careers",
        description=(
            "Lexer is a retail customer data platform (CDP) used by leading brands like "
            "Quiksilver and Sur La Table. Own B2B marketing targeting retail marketing "
            "teams — content, events, and demand gen. Retail industry knowledge a huge plus."
        ),
        tags=["b2b marketing", "b2b", "saas", "retail tech", "startup", "ecommerce"],
        salary_aud=(100, 130),
        days_ago=4,
    ),
    Job(
        title="Senior Marketing Manager",
        company="Flip",
        company_type="startup",
        location="Sydney, AU",
        remote=True,
        url="https://www.flip.com.au/careers",
        description=(
            "Flip is transforming how Australian SMBs access insurance (Series A). "
            "Own all marketing as our senior hire — brand, demand gen, and digital. "
            "Strong B2B or fintech marketing background and willingness to be hands-on."
        ),
        tags=["b2b", "fintech", "startup", "demand generation", "brand marketing"],
        salary_aud=(115, 145),
        days_ago=6,
    ),
    Job(
        title="Marketing Manager",
        company="Shippit",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://www.shippit.com/careers/",
        description=(
            "Shippit is the logistics platform behind Australia's fastest-growing brands. "
            "Drive B2B marketing targeting ecommerce retailers — content, events, and "
            "demand gen. Deep ecommerce logistics knowledge is a significant plus."
        ),
        tags=["b2b marketing", "ecommerce", "saas", "logistics", "startup"],
        salary_aud=(105, 135),
        days_ago=11,
    ),
    Job(
        title="Product Marketing Manager",
        company="Limepay",
        company_type="startup",
        location="Sydney, AU",
        remote=True,
        url="https://www.limepay.com.au/careers",
        description=(
            "Limepay provides embedded payments for ecommerce businesses. Join as our "
            "first PMM — own positioning, go-to-market, and sales enablement for our "
            "merchant-facing product. Payments + ecommerce background ideal."
        ),
        tags=["product marketing", "ecommerce", "fintech", "startup", "marketplace"],
        salary_aud=(110, 140),
        days_ago=3,
    ),

    # ── AI-adjacent / Future-facing roles ─────────────────────────────────

    Job(
        title="Marketing Manager — AI Products",
        company="Canva",
        company_type="scaleup",
        location="Sydney, AU",
        remote=True,
        url="https://www.canva.com/careers/",
        description=(
            "Drive awareness and adoption of Canva's AI-powered features (Magic Studio). "
            "Own GTM for AI product launches, develop messaging for creative and marketing "
            "professionals, and work closely with Product and Comms teams."
        ),
        tags=["product marketing", "ai", "saas", "b2b", "platform"],
        salary_aud=(130, 165),
        days_ago=1,
    ),
    Job(
        title="Growth Marketing Manager",
        company="Relevance AI",
        company_type="startup",
        location="Sydney, AU",
        remote=True,
        url="https://relevanceai.com/careers",
        description=(
            "Relevance AI is the platform for building AI agents and workflows. "
            "Drive growth marketing targeting B2B SaaS teams and ops leaders. "
            "Own paid, SEO, and lifecycle. Exciting role at the intersection of AI + SaaS."
        ),
        tags=["growth marketing", "b2b", "saas", "ai", "startup"],
        salary_aud=(110, 145),
        days_ago=2,
    ),
    Job(
        title="B2B Marketing Manager — AI Platform",
        company="Appen",
        company_type="enterprise",
        location="Sydney, AU",
        remote=True,
        url="https://www.appen.com/careers/",
        description=(
            "Develop and execute B2B marketing for Appen's AI training data platform, "
            "targeting enterprise ML teams globally. Own content, analyst relations, "
            "and demand generation programmes."
        ),
        tags=["b2b marketing", "b2b", "ai", "enterprise", "demand generation"],
        salary_aud=(115, 148),
        days_ago=7,
    ),
    Job(
        title="Senior Marketing Manager",
        company="Workato",
        company_type="scaleup",
        location="Remote (APAC)",
        remote=True,
        url="https://www.workato.com/careers",
        description=(
            "Workato's iPaaS and automation platform is used by 10,000+ enterprises. "
            "Drive APAC marketing across demand gen, events, and content. "
            "Partner with Sales and CS on account-based programmes."
        ),
        tags=["b2b", "saas", "enterprise", "demand generation", "automation"],
        salary_aud=(125, 158),
        days_ago=9,
    ),

    # ── Global remote / international ─────────────────────────────────────

    Job(
        title="Product Marketing Manager, Commerce",
        company="BigCommerce",
        company_type="enterprise",
        location="Remote (AU-friendly)",
        remote=True,
        url="https://www.bigcommerce.com/jobs/",
        description=(
            "Own product marketing for BigCommerce's commerce platform targeting mid-market "
            "and enterprise retailers. Drive launch strategy, competitive positioning, and "
            "sales enablement. Deep ecommerce and retail knowledge essential."
        ),
        tags=["product marketing", "ecommerce", "saas", "marketplace", "b2b"],
        salary_aud=(120, 155),
        days_ago=6,
    ),
    Job(
        title="Senior Product Marketing Manager, Marketplace",
        company="Faire",
        company_type="scaleup",
        location="Remote",
        remote=True,
        url="https://www.faire.com/careers",
        description=(
            "Faire is the wholesale marketplace connecting independent brands with "
            "retailers globally. Join as PMM for our marketplace product — defining "
            "value props for brands and retailers. Marketplace + retail background essential."
        ),
        tags=["product marketing", "marketplace", "ecommerce", "b2b", "retail tech"],
        salary_aud=(140, 180),
        days_ago=4,
    ),
    Job(
        title="Marketing Manager — APAC",
        company="Gorgias",
        company_type="startup",
        location="Remote (APAC)",
        remote=True,
        url="https://www.gorgias.com/careers",
        description=(
            "Gorgias is the ecommerce helpdesk used by 14,000+ Shopify stores. "
            "Drive APAC marketing — events, digital campaigns, and partner activations. "
            "First marketing hire for the region. Strong ecommerce ecosystem knowledge required."
        ),
        tags=["b2b marketing", "ecommerce", "saas", "startup", "marketplace"],
        salary_aud=(100, 130),
        days_ago=5,
    ),
    Job(
        title="Ecommerce Marketing Specialist",
        company="Klaviyo",
        company_type="enterprise",
        location="Remote (AU)",
        remote=True,
        url="https://www.klaviyo.com/careers",
        description=(
            "Klaviyo is the leading email and SMS platform for ecommerce brands. "
            "Drive marketing programmes targeting ecommerce and DTC brands in ANZ. "
            "Own campaigns, webinars, and partner activations with Shopify ecosystem."
        ),
        tags=["ecommerce marketing", "ecommerce", "b2b", "saas", "marketplace"],
        salary_aud=(95, 125),
        days_ago=11,
    ),
    Job(
        title="Partner Marketing Manager — APAC",
        company="Shopify",
        company_type="enterprise",
        location="Remote (APAC)",
        remote=True,
        url="https://www.shopify.com/careers",
        description=(
            "Develop co-marketing programmes with Shopify's APAC agency and technology "
            "partner ecosystem. Own joint campaigns, events, and partner enablement. "
            "Deep understanding of ecommerce and app ecosystem required."
        ),
        tags=["partner marketing", "ecommerce", "marketplace", "saas", "b2b"],
        salary_aud=(115, 148),
        days_ago=8,
    ),
]


# Score all jobs
for _j in _RAW:
    _j.score = _score(_j)

# Sort by score descending
JOBS: list[Job] = sorted(_RAW, key=lambda j: j.score, reverse=True)
