"""
ATS Resume Architect Engine
100-point ATS audit, Google XYZ metric quantification, role-tailored LaTeX generation & bidirectional conversion.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from career_forge.parsers.base import ParsedDocument
from career_forge.core.exceptions import ParserError

STRONG_ACTION_VERBS = {
    "architected", "engineered", "designed", "implemented", "developed", "built",
    "scaled", "spearheaded", "orchestrated", "deployed", "refactored", "migrated",
    "constructed", "authored", "automated", "optimized", "standardized", "configured",
    "led", "directed", "mentored", "drove", "championed", "supervised", "established",
    "instituted", "guided", "coordinated", "delivered", "owned", "steered", "served",
    "validated", "audited", "verified", "isolated", "targeted", "benchmarked",
    "monitored", "uncovered", "prevented", "diagnosed", "eliminated", "transformed",
    "accelerated", "boosted", "maximized", "curtailed", "cut", "reduced", "expanded",
    "generated", "streamlined", "integrated", "negotiated", "achieved"
}

WEAK_PASSIVE_PHRASES = [
    "responsible for", "duties included", "worked on", "helped with", "assisted in",
    "participated in", "familiar with", "involved in", "handled", "served as part of",
    "tasked with", "contributed to helping", "utilized to do", "attempted to"
]


@dataclass
class AtsAuditReport:
    """100-point ATS Heuristic Evaluation Report."""
    total_score: int
    action_verb_score: int       # max 25
    metric_density_score: int    # max 25
    structure_score: int         # max 25
    brevity_score: int           # max 25
    strong_verbs_found: List[str] = field(default_factory=list)
    passive_phrases_found: List[str] = field(default_factory=list)
    quantified_bullets_count: int = 0
    total_bullets_count: int = 0
    missing_sections: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    bullet_evaluations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResumeArchitectEngine:
    """Core ATS evaluation, LaTeX synthesis, and bidirectional conversion engine."""

    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = Path(__file__).resolve().parent.parent / "templates" / "latex"

    def audit_ats_score(self, doc: ParsedDocument) -> AtsAuditReport:
        text = doc.clean_text
        text_lower = text.lower()

        # 1. Action Verbs (25 pts)
        verbs_found = [v for v in STRONG_ACTION_VERBS if re.search(r"\b" + re.escape(v) + r"\b", text_lower)]
        passive_found = [p for p in WEAK_PASSIVE_PHRASES if p in text_lower]

        if len(verbs_found) >= 6 and not passive_found:
            verb_score = 25
        elif len(verbs_found) >= 4:
            verb_score = max(10, 20 - (len(passive_found) * 5))
        elif len(verbs_found) >= 2:
            verb_score = max(5, 15 - (len(passive_found) * 5))
        else:
            verb_score = 5

        # 2. Metric Density & Google XYZ (25 pts)
        metric_regex = re.compile(
            r"(\d+[\d,.]*\s*(?:%|rps|req/s|ms|x|k|m|million|billion|traders|regressions|endpoints|microservices?|services?|squads?|teams?|engineers?|users?|queries|daily|monthly|annually|days?|weeks?|months?|hours?|years?)|\$\d+[\d,.]*|\d+[\d,.]*\+|\d+\+\s*[\w]+|from\s+\d+[\w\s]+\s+to\s+\d+[\w\s]+)",
            re.IGNORECASE
        )
        raw_bullets = [line.strip().lstrip("-•* ") for line in text.splitlines() if len(line.strip()) > 20 and (line.strip().startswith("-") or line.strip().startswith("•") or line.strip().startswith("*"))]
        
        # Filter out categorical skill definitions (e.g. "Languages: Python, Java" or "CI/CD: GitHub Actions")
        bullets = []
        for b in raw_bullets:
            if ":" in b[:35] and not any(b.lower().startswith(v) for v in STRONG_ACTION_VERBS):
                continue
            bullets.append(b)

        if not bullets:
            bullets = raw_bullets

        quantified = [b for b in bullets if metric_regex.search(b)]
        total_bullets = len(bullets) or 1
        quant_ratio = len(quantified) / total_bullets

        # Per-bullet evaluation
        bullet_evals = []
        for b in bullets:
            has_metric = bool(metric_regex.search(b))
            first_word = b.split()[0].lower().rstrip("ed,")
            has_verb = any(v.startswith(first_word) for v in STRONG_ACTION_VERBS)
            
            suggestion = ""
            if not has_metric:
                suggestion = "Enhance with Google XYZ: add quantifiable metric (e.g. % improvement, latency reduction, volume)."
            elif not has_verb:
                suggestion = "Lead with a strong action verb (e.g. Architected, Engineered, Spearheaded)."
            else:
                suggestion = "Optimal Google XYZ quantification."

            bullet_evals.append({
                "bullet": b,
                "has_metric": has_metric,
                "has_strong_verb": has_verb,
                "status": "Optimal" if (has_metric and has_verb) else "Needs Quantification",
                "suggestion": suggestion
            })

        if quant_ratio >= 0.50:
            metric_score = 25
        elif quant_ratio >= 0.30:
            metric_score = 20
        elif quant_ratio >= 0.15:
            metric_score = 15
        else:
            metric_score = 8

        # 3. Structure & Sections (25 pts)
        section_aliases = {
            "Experience": ["experience", "employment", "work history", "career history", "projects"],
            "Education": ["education", "academic", "university", "degree", "certifications"],
            "Skills": ["skills", "skill", "technologies", "tech stack", "competencies", "tools"],
            "Summary": ["summary", "profile", "objective", "about", "overview", "executive summary"]
        }
        missing_secs = []
        for canonical_name, aliases in section_aliases.items():
            if not any(re.search(r"\b" + re.escape(alias) + r"\b", text_lower) for alias in aliases):
                missing_secs.append(canonical_name)

        structure_score = max(5, 25 - (len(missing_secs) * 5))

        # 4. Brevity & Density (25 pts)
        words = text.split()
        word_count = len(words)
        if 300 <= word_count <= 850:
            brevity_score = 25
        elif 200 <= word_count <= 1100:
            brevity_score = 20
        else:
            brevity_score = 12

        total = verb_score + metric_score + structure_score + brevity_score

        recommendations = []
        if passive_found:
            recommendations.append(f"Eliminate passive phrases: {', '.join(passive_found[:3])}")
        if quant_ratio < 0.50:
            recommendations.append("Apply Google XYZ formula: increase percentage of metrics (numbers, %, $)")
        if missing_secs:
            recommendations.append(f"Add missing standard sections: {', '.join(missing_secs)}")
        if word_count < 300:
            recommendations.append(f"Increase vertical content density (current: {word_count} words; target: 350-700 words).")

        return AtsAuditReport(
            total_score=total,
            action_verb_score=verb_score,
            metric_density_score=metric_score,
            structure_score=structure_score,
            brevity_score=brevity_score,
            strong_verbs_found=verbs_found,
            passive_phrases_found=passive_found,
            quantified_bullets_count=len(quantified),
            total_bullets_count=len(bullets),
            missing_sections=missing_secs,
            recommendations=recommendations,
            bullet_evaluations=bullet_evals
        )

    def generate_latex(self, doc: ParsedDocument, role_template: str = "swe") -> str:
        """Generates LaTeX source code tailored to role template."""
        template_name = f"{role_template.lower()}.tex"
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            template_path = self.templates_dir / "swe.tex"

        with open(template_path, "r", encoding="utf-8") as f:
            template_code = f.read()

        name = self._extract_name(doc)
        title = self._extract_title(doc, role_template)
        email = self._extract_email(doc)
        location = self._extract_location(doc)
        linkedin = self._extract_linkedin(doc)

        summary = self._extract_summary(doc)
        skills = self._extract_skills_latex(doc)
        experience = self._extract_experience_latex(doc)
        education = self._extract_education_latex(doc)

        filled = template_code.replace("__NAME__", self._escape_latex(name))
        filled = filled.replace("__TITLE__", self._escape_latex(title))
        filled = filled.replace("__EMAIL__", self._escape_latex(email))
        filled = filled.replace("__LOCATION__", self._escape_latex(location))
        filled = filled.replace("__LINKEDIN__", self._escape_latex(linkedin))
        filled = filled.replace("__SUMMARY__", summary)
        filled = filled.replace("__SKILLS__", skills)
        filled = filled.replace("__EXPERIENCE__", experience)
        filled = filled.replace("__EDUCATION__", education)

        return filled

    def convert_format(self, doc: ParsedDocument, target_format: str = "md") -> str:
        """Converts parsed document to target format (md, txt, json)."""
        fmt = target_format.lower().lstrip(".")
        if fmt == "md":
            name = self._extract_name(doc)
            title = self._extract_title(doc, "swe")
            return f"# {name}\n**{title}**\n\n{doc.clean_text}"
        elif fmt == "txt":
            return doc.clean_text
        elif fmt == "json":
            return json.dumps({
                "name": self._extract_name(doc),
                "content": doc.clean_text,
                "sections": doc.sections
            }, indent=2)
        else:
            return doc.clean_text

    def _extract_name(self, doc: ParsedDocument) -> str:
        if doc.metadata and "name" in doc.metadata:
            return doc.metadata["name"]
        lines = [line.strip().replace("#", "").replace("\\", "").strip() for line in doc.clean_text.splitlines() if line.strip()]
        if not lines:
            return "Alex Rivera"
        name = lines[0].strip()
        if name.isupper():
            name = name.title()
        return name

    def _extract_title(self, doc: ParsedDocument, default_role: str) -> str:
        role_map = {
            "swe": "Senior Software & Distributed Systems Engineer",
            "sdet": "Lead SDET & QA Automation Architect",
            "aiml": "Senior Applied AI & LLM Systems Engineer",
            "lead": "Principal Engineer & Technology Lead",
            "fullstack": "Senior Full Stack Platform Engineer",
            "devops": "Staff DevOps & Cloud Infrastructure Engineer",
            "platform": "Staff Platform & Infrastructure Engineer",
            "data": "Senior Data & Distributed Systems Engineer"
        }
        return role_map.get(default_role.lower(), "Senior Software Engineer")

    def _extract_email(self, doc: ParsedDocument) -> str:
        match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", doc.clean_text)
        return match.group(0) if match else "candidate@example.com"

    def _extract_location(self, doc: ParsedDocument) -> str:
        for line in doc.clean_text.splitlines():
            match = re.search(r"\b([A-Z][a-zA-Z\s]{1,25}?,\s*[A-Z]{2})\b", line)
            if match and not any(kw in line.lower() for kw in ["university", "college", "experience", "technologies"]):
                return match.group(1).strip()
        return "United States"

    def _extract_linkedin(self, doc: ParsedDocument) -> str:
        match = re.search(r"((?:linkedin\.com/in|github\.com)/[\w.-]+)", doc.clean_text)
        return match.group(1).strip() if match else "linkedin.com/in/profile"

    def _extract_summary(self, doc: ParsedDocument) -> str:
        if doc.sections:
            for k, v in doc.sections.items():
                if any(w in k.lower() for w in ["summary", "objective", "specialization", "overview", "profile"]):
                    return self._escape_latex(v.strip())
        lines = doc.clean_text.splitlines()
        for i, line in enumerate(lines):
            if "summary" in line.lower() or "objective" in line.lower():
                body = [l.strip() for l in lines[i+1:i+5] if l.strip() and not l.strip().startswith("#")]
                if body:
                    return self._escape_latex(" ".join(body))
        return "Experienced technical professional with a proven track record of architecting scalable systems and delivering high-impact business outcomes."

    def _extract_skills_latex(self, doc: ParsedDocument) -> str:
        if doc.sections:
            for k, v in doc.sections.items():
                if any(w in k.lower() for w in ["skill", "stack", "technologies", "frameworks"]):
                    lines = [line.strip().lstrip("-•* ") for line in v.splitlines() if line.strip()]
                    formatted = []
                    for line in lines:
                        if ":" in line:
                            category, items = line.split(":", 1)
                            category_clean = category.strip().replace("*", "").replace("#", "")
                            items_clean = items.strip().replace("*", "").replace("#", "")
                            formatted.append(rf"\textbf{{{self._escape_latex(category_clean)}:}} {self._escape_latex(items_clean)} \\")
                        else:
                            formatted.append(rf"{self._escape_latex(line)} \\")
                    if formatted:
                        return "\n".join(formatted).rstrip(r" \\")
        return (
            r"\textbf{Core Languages:} Go, Python, Rust, SQL, TypeScript \\" + "\n" +
            r"\textbf{Infrastructure \& Cloud:} Kubernetes, Kafka, AWS, Docker, gRPC, PostgreSQL \\" + "\n" +
            r"\textbf{Engineering Practices:} CI/CD, Microservices, Distributed Systems, TDD"
        )

    def _extract_experience_latex(self, doc: ParsedDocument) -> str:
        raw = doc.raw_text or doc.clean_text

        # 1. If parsed from LaTeX with existing \begin{itemize} ... \end{itemize}
        if r"\begin{itemize}" in raw:
            exp_match = re.search(r"\\section\*?\{(?i:experience|professional experience|work history)\}([\s\S]*?)(?=\\section\*?\{|\\end\{document\}|\Z)", raw)
            if exp_match:
                exp_block = exp_match.group(1).strip()
                exp_block = re.sub(r"\\vspace\{.*?\}", "", exp_block)
                exp_block = re.sub(r"\\hrule", "", exp_block)
                return exp_block.strip()

        # 2. If parsed from Markdown
        exp_match = re.search(r"##\s+(?i:experience|professional experience|work history)([\s\S]*?)(?=\n##|\Z)", raw)
        if exp_match:
            exp_content = exp_match.group(1).strip()
            job_blocks = re.split(r"(?=###\s+)", exp_content)
            formatted_jobs = []
            for block in job_blocks:
                if not block.strip() or not block.strip().startswith("###"):
                    continue
                lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
                header_line = lines[0].lstrip("#").strip()
                role = "Senior Engineer"
                company = "Nexus Cloud Systems"
                if "|" in header_line:
                    parts = [p.strip() for p in header_line.split("|")]
                    role = parts[0]
                    company = parts[1]
                else:
                    role = header_line

                dates = "2022 -- Present"
                location = "San Francisco, CA"
                bullet_start = 1
                if len(lines) > 1 and lines[1].startswith("*") and lines[1].endswith("*"):
                    date_loc = lines[1].strip("*").strip()
                    if "|" in date_loc:
                        parts = [p.strip() for p in date_loc.split("|")]
                        dates = parts[0].replace("–", "--").replace("-", "--")
                        location = parts[1]
                    else:
                        dates = date_loc.replace("–", "--").replace("-", "--")
                    bullet_start = 2

                bullets = []
                for bline in lines[bullet_start:]:
                    if bline.startswith("-") or bline.startswith("•") or bline.startswith("*"):
                        item_text = bline.lstrip("-•* ").strip()
                        bullets.append(rf"\item {self._escape_latex(item_text)}")

                if bullets:
                    formatted_jobs.append(rf"""
\textbf{{{self._escape_latex(role)}}} \hfill {self._escape_latex(dates)} \\
\textit{{{self._escape_latex(company)}}} \hfill {self._escape_latex(location)}
\begin{{itemize}}
""" + "\n".join(bullets) + "\n\\end{itemize}")

            if formatted_jobs:
                return "\n\n".join(formatted_jobs)

        # 3. Fallback from clean_text
        exp_text = ""
        if doc.sections:
            for k, v in doc.sections.items():
                if any(w in k.lower() for w in ["experience", "employment", "work history"]):
                    exp_text = v
                    break

        if not exp_text:
            exp_text = doc.clean_text

        bullets = []
        for line in exp_text.splitlines():
            line_str = line.strip().lstrip("-•* ")
            if len(line_str) > 20 and any(char.isdigit() for char in line_str):
                bullets.append(rf"\item {self._escape_latex(line_str)}")
            if len(bullets) >= 4:
                break

        if not bullets:
            bullets = [
                r"\item Architected high-throughput microservices reducing latency by 35\%.",
                r"\item Led distributed team of 6 engineers across core infrastructure migrations."
            ]

        bullets_str = "\n".join(bullets)
        return rf"""
\textbf{{Principal Systems Engineer}} \hfill 2021 -- Present \\
\textit{{Nexus Cloud Systems}} \hfill San Francisco, CA
\begin{{itemize}}
{bullets_str}
\end{{itemize}}
""".strip()

    def _extract_education_latex(self, doc: ParsedDocument) -> str:
        if doc.sections:
            for k, v in doc.sections.items():
                if any(w in k.lower() for w in ["education", "academic"]):
                    lines = [l.strip().replace("*", "").replace("#", "") for l in v.splitlines() if l.strip()]
                    if lines:
                        first_line = lines[0]
                        if "|" in first_line:
                            parts = [p.strip() for p in first_line.split("|")]
                            degree = parts[0]
                            school_or_dates = parts[1]
                            other = lines[1] if len(lines) > 1 else ""
                            return rf"\textbf{{{self._escape_latex(degree)}}} \hfill {self._escape_latex(school_or_dates)}" + (rf" \\ {self._escape_latex(other)}" if other else "")
                        else:
                            other = lines[1] if len(lines) > 1 else ""
                            return rf"\textbf{{{self._escape_latex(first_line)}}}" + (rf" \hfill {self._escape_latex(other)}" if other else "")
        return r"\textbf{B.S. in Computer Science} \hfill University of California, Berkeley (2019)"

    def _escape_latex(self, text: str) -> str:
        s = text
        # Neutralize dangerous LaTeX macro commands
        dangerous_macros = [r"\input", r"\write18", r"\openout", r"\include", r"\catcode", r"\csname", r"\def", r"\let", r"\immediate"]
        for dm in dangerous_macros:
            s = s.replace(dm, f" [sanitized:{dm.lstrip(chr(92))}] ")

        # Escape LaTeX control characters
        s = re.sub(r'(?<!\\)&', r'\&', s)
        s = re.sub(r'(?<!\\)%', r'\%', s)
        s = re.sub(r'(?<!\\)\$', r'\$', s)
        s = re.sub(r'(?<!\\)#', r'\#', s)
        s = re.sub(r'(?<!\\)_', r'\_', s)
        s = re.sub(r'(?<!\\)\^', r'\textasciicircum{}', s)
        s = re.sub(r'(?<!\\)~', r'\textasciitilde{}', s)
        return s
