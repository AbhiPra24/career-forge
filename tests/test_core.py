"""
Unit tests for CareerForge Core Infrastructure (Config, Database & Exceptions)
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from career_forge.core.config import Config, get_config
from career_forge.core.db import DatabaseManager
from career_forge.core.exceptions import (
    CareerForgeError,
    ParserError,
    CompilationError,
    DeliverabilityError,
    RateLimitError,
)


class TestCore(unittest.TestCase):
    def test_custom_exceptions(self):
        err = ParserError("Failed to parse document")
        self.assertIsInstance(err, CareerForgeError)
        self.assertEqual(str(err), "Failed to parse document")

        comp_err = CompilationError("Tectonic failed")
        self.assertIsInstance(comp_err, CareerForgeError)

    def test_config_defaults(self):
        cfg = Config()
        self.assertEqual(cfg.weight_skill_match, 0.40)
        self.assertEqual(cfg.weight_exp_depth, 0.30)
        self.assertEqual(cfg.weight_market_demand, 0.20)
        self.assertEqual(cfg.weight_competitive_edge, 0.10)
        self.assertEqual(cfg.dns_timeout, 2.0)
        self.assertAlmostEqual(cfg.weights_sum, 1.0)

    def test_config_env_override(self):
        os.environ["WEIGHT_SKILL_MATCH"] = "0.50"
        os.environ["DNS_LOOKUP_TIMEOUT_SECONDS"] = "3.5"
        try:
            cfg = get_config(reload=True)
            self.assertEqual(cfg.weight_skill_match, 0.50)
            self.assertEqual(cfg.dns_timeout, 3.5)
        finally:
            del os.environ["WEIGHT_SKILL_MATCH"]
            del os.environ["DNS_LOOKUP_TIMEOUT_SECONDS"]
            get_config(reload=True)

    def test_database_initialization_and_wal_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_cache.db"
            db_mgr = DatabaseManager(db_path=db_path)
            
            # Verify tables exist
            with db_mgr.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check journal mode (WAL or memory)
                cursor.execute("PRAGMA journal_mode;")
                mode = cursor.fetchone()[0].lower()
                self.assertIn(mode, ("wal", "memory"))
                
                # Check tables created
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = {row[0] for row in cursor.fetchall()}
                self.assertIn("jobs_cache", tables)
                self.assertIn("eval_cache", tables)
                self.assertIn("dns_negative_cache", tables)

    def test_database_cache_operations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_cache.db"
            db_mgr = DatabaseManager(db_path=db_path)
            
            # Test Job Caching
            db_mgr.cache_job("https://example.com/job/1", "Senior SWE", "Acme Corp", "Python & Distributed Systems")
            cached = db_mgr.get_cached_job("https://example.com/job/1")
            self.assertIsNotNone(cached)
            self.assertEqual(cached["title"], "Senior SWE")
            self.assertEqual(cached["company"], "Acme Corp")
            
            # Test Negative DNS Caching
            db_mgr.set_dns_status("invalid-domain.xyz", is_valid=False)
            self.assertFalse(db_mgr.get_dns_status("invalid-domain.xyz"))
            self.assertIsNone(db_mgr.get_dns_status("unseen-domain.com"))


if __name__ == "__main__":
    unittest.main()

