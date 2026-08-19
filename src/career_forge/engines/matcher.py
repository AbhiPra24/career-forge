"""
4-Factor Role Matching & Evaluation Engine (TalentScoutEngine)
Calculates calibrated fit scores across Skill Match, Experience Depth, Market Demand, and Competitive Edge.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from career_forge.core.config import get_config
from career_forge.core.db import get_db
from career_forge.engines.digest import ProfileDigest


@dataclass
class JobListing:
    """Standardized representation of a job listing / requisition."""
    title: str
    company: str
    location: str
    tier: str
    requirements: List[str]
    description: str
    url: str = ""
    salary_range: str = "Market Benchmark"


@dataclass
class EvaluationResult:
    """Comprehensive evaluation score and breakdown."""
    fit_score: float
    skill_score: float
    exp_score: float
    demand_score: float
    edge_score: float
    action_batch: str
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TalentScoutEngine:
    """Evaluates candidate ProfileDigest against JobListing requisitions."""

    def __init__(self):
        self.config = get_config()
        self.db = get_db()

    def evaluate_fit(self, digest: ProfileDigest, job: JobListing) -> EvaluationResult:
        # Check cache
        cache_key = self._compute_cache_key(digest, job)
        
        # 1. Skill Match Score (0 - 100%)
        candidate_skills = {s.lower() for s in digest.core_stack}
        job_reqs = [r.lower() for r in job.requirements]
        
        matched = []
        missing = []
        for req in job_reqs:
            if any(req in cs or cs in req for cs in candidate_skills) or any(req in word for word in digest.domain_expertise):
                matched.append(req.title())
            else:
                missing.append(req.title())
        
        if job_reqs:
            skill_score = (len(matched) / len(job_reqs)) * 100.0
        else:
            skill_score = 75.0

        # 2. Experience Depth Score (0 - 100%)
        exp_score = self._calculate_exp_score(digest, job)

        # 3. Market Demand Score (0 - 100%)
        demand_score = self._calculate_demand_score(job)

        # 4. Competitive Edge Score (0 - 100%)
        edge_score = self._calculate_edge_score(digest, job)

        # Weighted aggregate
        w_skill = self.config.weight_skill_match
        w_exp = self.config.weight_exp_depth
        w_demand = self.config.weight_market_demand
        w_edge = self.config.weight_competitive_edge

        fit_score = (
            (skill_score * w_skill)
            + (exp_score * w_exp)
            + (demand_score * w_demand)
            + (edge_score * w_edge)
        )
        fit_score = round(min(100.0, max(0.0, fit_score)), 1)

        # Classify Action Batch
        if fit_score >= 85.0:
            action_batch = "Batch 1 (Immediate Apply)"
        elif fit_score >= 70.0:
            action_batch = "Batch 2 (Targeted Prep)"
        else:
            action_batch = "Batch 3 (Safety Net / Alternate)"

        # Strengths & Risks
        strengths = []
        risks = []
        if skill_score >= 70:
            strengths.append(f"Strong core stack alignment ({len(matched)} matching key technologies).")
        if digest.top_metrics:
            strengths.append(f"Verified high-impact metrics: '{digest.top_metrics[0]}'")
        if missing:
            risks.append(f"Skill delta in: {', '.join(missing[:3])}")
        if exp_score < 70:
            risks.append("Target role seniority may require additional domain framing.")

        return EvaluationResult(
            fit_score=fit_score,
            skill_score=round(skill_score, 1),
            exp_score=round(exp_score, 1),
            demand_score=round(demand_score, 1),
            edge_score=round(edge_score, 1),
            action_batch=action_batch,
            matched_skills=matched,
            missing_skills=missing,
            strengths=strengths,
            risks=risks
        )

    def _calculate_exp_score(self, digest: ProfileDigest, job: JobListing) -> float:
        yoe = digest.years_of_experience or 4
        title_lower = job.title.lower()
        if "principal" in title_lower or "staff" in title_lower or "architect" in title_lower:
            return 95.0 if yoe >= 8 else (75.0 if yoe >= 5 else 50.0)
        elif "senior" in title_lower or "lead" in title_lower:
            return 95.0 if yoe >= 5 else (80.0 if yoe >= 3 else 60.0)
        elif "mid" in title_lower or "engineer ii" in title_lower:
            return 90.0 if yoe >= 2 else 70.0
        else:
            return 85.0

    def _calculate_demand_score(self, job: JobListing) -> float:
        # Tier-based demand multiplier
        if "Tier 1" in job.tier:
            return 92.0
        elif "Tier 2" in job.tier:
            return 88.0
        elif "Tier 3" in job.tier:
            return 95.0
        else:
            return 78.0

    def _calculate_edge_score(self, digest: ProfileDigest, job: JobListing) -> float:
        score = 70.0
        if digest.top_metrics and len(digest.top_metrics) >= 2:
            score += 15.0
        if any(role.lower() in job.title.lower() for role in digest.target_roles):
            score += 15.0
        return min(100.0, score)

    def _compute_cache_key(self, digest: ProfileDigest, job: JobListing) -> str:
        raw = f"{digest.candidate_name}:{digest.core_stack}:{job.title}:{job.company}:{job.requirements}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
