# GitHub Copilot Instructions for CareerForge

You are assisting with development on **CareerForge** (`career-forge`), a production-grade Python package for career intelligence, ATS resume generation, job requisition matching, and recruiter email verification.

## Conventions
- **Python Version:** 3.10+
- **Code Style:** Type annotations on all public methods and functions. Clean docstrings.
- **Testing:** `unittest` and `pytest` compatible test suites under `tests/`.
- **Database:** SQLite with Write-Ahead Logging (`WAL`) mode and busy timeout handling in `career_forge.core.db`.
- **Security & Privacy:** Strictly zero-PII in fixtures, code, templates, and commits. All mock personas must use fictional data.
- **CLI Commands:** Built with `argparse` and `rich` in `career_forge.cli`.
