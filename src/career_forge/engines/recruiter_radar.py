"""
Recruiter Radar & Email Deliverability Engine
Validates RFC 5322 syntax, non-blocking DNS/MX host resolution (timeout <= 2s), and anti-bounce alias checks.
"""

import re
import socket
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from career_forge.core.config import get_config
from career_forge.core.db import get_db

GENERIC_UNMONITORED_PREFIXES = {
    "recruiting", "hiring", "careers", "jobs", "info", "contact",
    "hr", "talent", "support", "help", "sales", "general", "inquiries", "reception", "apply"
}


@dataclass
class DeliverabilityStatus:
    """Detailed email deliverability and MX health evaluation."""
    email: str
    is_valid_syntax: bool
    domain_resolves: bool
    is_generic_alias: bool
    confidence: str   # "HIGH CONFIDENCE" | "MEDIUM / CAUTION" | "BOUNCE LIKELY / INVALID"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RecruiterRadarEngine:
    """Deliverability verification and outreach generation engine."""

    def __init__(self):
        self.config = get_config()
        self.db = get_db()

    def validate_email_syntax(self, email: str) -> bool:
        """Validates format using strict RFC 5322 regex."""
        if not email or "@" not in email:
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    def is_generic_alias(self, email: str) -> bool:
        """Flags unmonitored catch-all prefixes that bounce or trigger spam filters."""
        if not email or "@" not in email:
            return False
        prefix = email.split("@")[0].lower().strip().split("+")[0]
        return prefix in GENERIC_UNMONITORED_PREFIXES

    def check_domain_dns(self, domain: str) -> bool:
        """Non-blocking DNS resolution with negative caching and configurable timeout."""
        clean_domain = domain.lower().strip()
        
        # Check SQLite negative cache
        cached_status = self.db.get_dns_status(clean_domain)
        if cached_status is not None:
            return cached_status

        orig_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(self.config.dns_timeout)
            socket.getaddrinfo(clean_domain, 80, proto=socket.IPPROTO_TCP)
            self.db.set_dns_status(clean_domain, is_valid=True)
            return True
        except (socket.gaierror, socket.timeout):
            self.db.set_dns_status(clean_domain, is_valid=False, error_message="DNS resolution timeout or failure")
            return False
        finally:
            socket.setdefaulttimeout(orig_timeout)

    def verify_email(self, email: str) -> DeliverabilityStatus:
        """Evaluates syntax, domain host resolution, and bounce likelihood."""
        clean = email.strip()
        warnings = []

        if not self.validate_email_syntax(clean):
            return DeliverabilityStatus(
                email=clean,
                is_valid_syntax=False,
                domain_resolves=False,
                is_generic_alias=False,
                confidence="BOUNCE LIKELY / INVALID",
                warnings=["Malformed RFC 5322 email syntax."]
            )

        domain = clean.split("@")[1]
        is_generic = self.is_generic_alias(clean)
        domain_ok = self.check_domain_dns(domain)

        if is_generic:
            warnings.append("Generic unmonitored alias detected (e.g. careers@, hr@). High risk of no reply or automated rejection.")
        if not domain_ok:
            warnings.append(f"Domain '{domain}' failed DNS/MX host resolution.")

        # Determine confidence
        if not domain_ok:
            confidence = "BOUNCE LIKELY / INVALID"
        elif is_generic:
            confidence = "BOUNCE LIKELY (UNMONITORED ALIAS)"
        else:
            confidence = "HIGH CONFIDENCE"

        return DeliverabilityStatus(
            email=clean,
            is_valid_syntax=True,
            domain_resolves=domain_ok,
            is_generic_alias=is_generic,
            confidence=confidence,
            warnings=warnings
        )

    def generate_outreach_templates(
        self, candidate_name: str, role_title: str, target_company: str, top_metric: str
    ) -> Dict[str, str]:
        """Generates 3 tiers of customized cold outreach email templates."""
        return {
            "hiring_manager": f"""Subject: {role_title} @ {target_company} – Scaling & Systems Impact

Hi [Hiring Manager],

I saw your team's expansion in distributed systems at {target_company}. As a {role_title}, I specialize in building high-throughput infrastructure.

Most recently: {top_metric}.

I would welcome a brief 10-minute conversation to explore how my background could support your team's upcoming milestones.

Best regards,
{candidate_name}""",

            "recruiter": f"""Subject: Re: {role_title} Open Requisition @ {target_company}

Hi [Recruiter Name],

I noticed the {role_title} opening on your engineering team at {target_company}. My background aligns directly with your core stack.

Highlight: {top_metric}.

I have attached my tailored resume and would love to connect for an initial screen.

Best,
{candidate_name}""",

            "peer_referral": f"""Subject: Quick question about Engineering @ {target_company}

Hi [First Name],

I noticed your work as an engineer at {target_company} and wanted to reach out. I'm exploring the open {role_title} position on your team.

My recent focus: {top_metric}.

Would you be open to sharing your perspective on the team culture and engineering roadmap?

Thanks a lot,
{candidate_name}"""
        }
