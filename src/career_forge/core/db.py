"""
Thread-safe SQLite Database & Caching Engine with WAL Concurrency Support
"""

import sqlite3
import json
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from career_forge.core.config import get_config
from career_forge.core.exceptions import DatabaseError


class DatabaseManager:
    """Manages persistent SQLite cache with WAL mode & busy timeout for concurrency."""
    
    CURRENT_SCHEMA_VERSION = 1

    def __init__(self, db_path: Optional[Path] = None):
        cfg = get_config()
        self.db_path = Path(db_path or cfg.db_path)
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager yielding an initialized SQLite connection with WAL mode."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode and 5000ms busy timeout
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA busy_timeout = 5000;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            if conn:
                conn.close()

    def _init_db(self):
        """Initializes tables and ensures schema migrations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Schema version tracking
            cursor.execute("PRAGMA user_version;")
            version = cursor.fetchone()[0]

            if version < self.CURRENT_SCHEMA_VERSION:
                # 1. Jobs Cache
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs_cache (
                        url TEXT PRIMARY KEY,
                        title TEXT,
                        company TEXT,
                        clean_text TEXT,
                        raw_html TEXT,
                        tier TEXT,
                        location TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 2. Evaluation Cache
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS eval_cache (
                        cache_key TEXT PRIMARY KEY,
                        fit_score REAL,
                        skill_score REAL,
                        exp_score REAL,
                        demand_score REAL,
                        edge_score REAL,
                        breakdown_json TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 3. DNS / MX Negative Cache
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dns_negative_cache (
                        domain TEXT PRIMARY KEY,
                        is_valid INTEGER,
                        error_message TEXT,
                        checked_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                cursor.execute(f"PRAGMA user_version = {self.CURRENT_SCHEMA_VERSION};")

    def cache_job(self, url: str, title: str, company: str, clean_text: str,
                  tier: str = "General", location: str = "Remote", raw_html: str = ""):
        """Caches a scraped job listing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO jobs_cache (url, title, company, clean_text, raw_html, tier, location, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (url, title, company, clean_text, raw_html, tier, location, datetime.datetime.utcnow().isoformat()))

    def get_cached_job(self, url: str) -> Optional[Dict[str, Any]]:
        """Retrieves a cached job if present."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs_cache WHERE url = ?;", (url,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def set_dns_status(self, domain: str, is_valid: bool, error_message: str = ""):
        """Stores domain DNS/MX resolution status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO dns_negative_cache (domain, is_valid, error_message, checked_at)
                VALUES (?, ?, ?, ?);
            """, (domain.lower().strip(), 1 if is_valid else 0, error_message, datetime.datetime.utcnow().isoformat()))

    def get_dns_status(self, domain: str) -> Optional[bool]:
        """Checks if a domain validation result is cached."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_valid FROM dns_negative_cache WHERE domain = ?;", (domain.lower().strip(),))
            row = cursor.fetchone()
            if row is not None:
                return bool(row["is_valid"])
        return None


_global_db: Optional[DatabaseManager] = None


def get_db(db_path: Optional[Path] = None) -> DatabaseManager:
    """Retrieves global DatabaseManager instance."""
    global _global_db
    if _global_db is None or db_path is not None:
        _global_db = DatabaseManager(db_path=db_path)
    return _global_db
