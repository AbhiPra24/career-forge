"""
Global configuration management for CareerForge
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

try:
    from dotenv import load_dotenv
    # Load .env if present
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    """Application configuration and scoring hyperparameters."""
    
    # 4-Factor Scoring Weights (Default: 40% / 30% / 20% / 10%)
    weight_skill_match: float = field(
        default_factory=lambda: float(os.getenv("WEIGHT_SKILL_MATCH", "0.40"))
    )
    weight_exp_depth: float = field(
        default_factory=lambda: float(os.getenv("WEIGHT_EXP_DEPTH", "0.30"))
    )
    weight_market_demand: float = field(
        default_factory=lambda: float(os.getenv("WEIGHT_MARKET_DEMAND", "0.20"))
    )
    weight_competitive_edge: float = field(
        default_factory=lambda: float(os.getenv("WEIGHT_COMPETITIVE_EDGE", "0.10"))
    )
    
    # Database path
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("CAREER_FORGE_DB_PATH", "jobs_cache.db"))
    )
    
    # Cache Time-to-Live (in days)
    cache_ttl_days: int = field(
        default_factory=lambda: int(os.getenv("CAREER_FORGE_CACHE_TTL_DAYS", "14"))
    )
    
    # Recruiter Radar settings
    dns_timeout: float = field(
        default_factory=lambda: float(os.getenv("DNS_LOOKUP_TIMEOUT_SECONDS", "2.0"))
    )
    
    # Optional LLM & Scraping API keys
    gemini_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY")
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    firecrawl_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("FIRECRAWL_API_KEY")
    )
    
    @property
    def weights_sum(self) -> float:
        return (
            self.weight_skill_match
            + self.weight_exp_depth
            + self.weight_market_demand
            + self.weight_competitive_edge
        )


_global_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """Retrieve global configuration instance."""
    global _global_config
    if _global_config is None or reload:
        _global_config = Config()
    return _global_config
