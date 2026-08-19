"""
Profile Digest & Token Optimization Engine
Extracts a compact ~150-token structured profile summary from raw/parsed resume documents.
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from career_forge.parsers.base import ParsedDocument

KNOWN_STACK_KEYWORDS = [
    # Languages
    "Python", "Go", "Rust", "Java", "TypeScript", "JavaScript", "C++", "C#", "SQL", "Scala", "Ruby", "Swift", "Kotlin",
    # Distributed & Cloud
    "Kubernetes", "Docker", "Kafka", "gRPC", "Redis", "PostgreSQL", "MySQL", "Cassandra", "MongoDB", "Elasticsearch",
    "AWS", "GCP", "Azure", "Terraform", "Envoy", "Prometheus", "Grafana", "OpenTelemetry", "RabbitMQ",
    # AI & ML
    "PyTorch", "TensorFlow", "Hugging Face", "vLLM", "LangChain", "LangGraph", "LlamaIndex", "TensorRT", "Triton", "CUDA",
    # Testing & QA
    "Playwright", "Cypress", "Selenium", "PyTest", "TestNG", "RestAssured", "k6", "JMeter", "Locust", "Postman", "CI/CD", "GitHub Actions"
]

EXPERIENCE_KEYWORDS = {
    "Lead": ("LEAD / PRINCIPAL (8+ YoE)", 8),
    "Principal": ("LEAD / PRINCIPAL (8+ YoE)", 8),
    "Staff": ("STAFF / ARCHITECT (10+ YoE)", 10),
    "Architect": ("STAFF / ARCHITECT (10+ YoE)", 10),
    "Senior": ("SENIOR (5+ YoE)", 5),
    "Sr.": ("SENIOR (5+ YoE)", 5),
    "Mid": ("MID-LEVEL (3-5 YoE)", 3),
    "Junior": ("EARLY CAREER (0-2 YoE)", 1),
    "Associate": ("EARLY CAREER (0-2 YoE)", 1),
    "Intern": ("INTERN / STUDENT", 0),
}


@dataclass
class ProfileDigest:
    """Compact ~150-token profile digest representation."""
    candidate_name: str
    career_stage: str
    target_roles: List[str] = field(default_factory=list)
    core_stack: List[str] = field(default_factory=list)
    domain_expertise: List[str] = field(default_factory=list)
    top_metrics: List[str] = field(default_factory=list)
    years_of_experience: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class ProfileDigestEngine:
    """Engine to extract compact structured digest from ParsedDocument."""

    def extract_digest(self, doc: ParsedDocument) -> ProfileDigest:
        clean_text = doc.clean_text
        name = self._extract_name(doc)
        stack = self._extract_stack(clean_text)
        career_stage, yoe = self._detect_career_stage(clean_text)
        domains = self._detect_domains(clean_text, stack)
        metrics = self._extract_top_metrics(clean_text)
        roles = self._infer_target_roles(clean_text, domains)

        # Keep metrics concise
        concise_metrics = [m[:120] + "..." if len(m) > 120 else m for m in metrics[:4]]

        return ProfileDigest(
            candidate_name=name,
            career_stage=career_stage,
            target_roles=roles,
            core_stack=stack[:10],  # keep top 10 most salient
            domain_expertise=domains,
            top_metrics=concise_metrics,
            years_of_experience=yoe
        )

    def _extract_name(self, doc: ParsedDocument) -> str:
        # Check metadata
        if doc.metadata and "name" in doc.metadata:
            return doc.metadata["name"]
        
        lines = [line.strip() for line in doc.clean_text.splitlines() if line.strip()]
        if not lines:
            return "Candidate Name"
        
        first_line = lines[0].replace("#", "").replace("\\", "").strip()
        # Title case name extraction
        words = first_line.split()
        if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            return first_line.title()

        # Fallback to first line
        return first_line[:40].title()

    def _extract_stack(self, text: str) -> List[str]:
        found = []
        text_lower = text.lower()
        for kw in KNOWN_STACK_KEYWORDS:
            # Word boundary matching
            pattern = r"(?i)\b" + re.escape(kw.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found.append(kw)
        return found

    def _detect_career_stage(self, text: str) -> (str, int):
        # Check explicit years of experience like "7+ years", "8+ years"
        yoe_match = re.search(r"(\d+)\+?\s*(?:years|yrs|yoe)", text, re.IGNORECASE)
        if yoe_match:
            yoe = int(yoe_match.group(1))
            if yoe >= 10:
                return "STAFF / ARCHITECT (10+ YoE)", yoe
            elif yoe >= 7:
                return "LEAD / SENIOR (7+ YoE)", yoe
            elif yoe >= 5:
                return "SENIOR (5+ YoE)", yoe
            elif yoe >= 3:
                return "MID-LEVEL (3-5 YoE)", yoe
            else:
                return "EARLY CAREER (0-2 YoE)", yoe

        for kw, (stage, default_yoe) in EXPERIENCE_KEYWORDS.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
                return stage, default_yoe

        return "EXPERIENCED PROFESSIONAL", 4

    def _detect_domains(self, text: str, stack: List[str]) -> List[str]:
        domains = []
        text_lower = text.lower()
        if any(w in text_lower for w in ["distributed", "microservices", "kubernetes", "kafka", "grpc"]):
            domains.append("Distributed Systems & Backend")
        if any(w in text_lower for w in ["sdet", "qa", "playwright", "cypress", "automation", "k6"]):
            domains.append("Quality Engineering & Automation")
        if any(w in text_lower for w in ["ai", "llm", "rag", "pytorch", "vllm", "transformers", "machine learning"]):
            domains.append("Applied AI & LLM Systems")
        if any(w in text_lower for w in ["frontend", "react", "typescript", "full stack", "fullstack"]):
            domains.append("Full Stack & Web Architecture")
        if any(w in text_lower for w in ["cloud", "devops", "terraform", "aws", "infra"]):
            domains.append("Cloud Infrastructure & DevOps")

        return domains or ["Software Engineering"]

    def _extract_top_metrics(self, text: str) -> List[str]:
        """Extracts bullet points or sentences containing concrete quantifiable metrics."""
        metric_regex = re.compile(r"(\d+[\d,.]*\s*(?:%|rps|req/s|ms|x|k|m|million|billion|traders|regressions|endpoints)|\$\d+[\d,.]*|\d+\+\s*critical)", re.IGNORECASE)
        matches = []
        for line in text.splitlines():
            line_str = line.strip().lstrip("-•* ").strip()
            if len(line_str) >= 20 and metric_regex.search(line_str):
                matches.append(line_str)
        return matches

    def _infer_target_roles(self, text: str, domains: List[str]) -> List[str]:
        roles = []
        if "Distributed Systems & Backend" in domains:
            roles.extend(["Senior Backend Engineer", "Distributed Systems Engineer", "Principal Platform Engineer"])
        if "Quality Engineering & Automation" in domains:
            roles.extend(["Lead SDET", "Staff QA Automation Engineer", "Head of Quality Engineering"])
        if "Applied AI & LLM Systems" in domains:
            roles.extend(["Senior Applied AI Engineer", "LLM Systems Architect", "AI Infrastructure Engineer"])
        if "Full Stack & Web Architecture" in domains:
            roles.extend(["Senior Full Stack Engineer", "Staff Web Architect"])
        return roles or ["Software Engineer", "Technical Lead"]
