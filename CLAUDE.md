# CLAUDE.md – CareerForge Guidelines & Commands

Welcome to **CareerForge** (`career-forge`). This file provides comprehensive context, build targets, architectural conventions, and tool execution instructions for Claude agents.

---

## 🛠️ Build & Test Commands

- **Run all tests (unittest / pytest):**
  ```bash
  PYTHONPATH=src python3 -m unittest discover tests
  # or with pytest
  python3 -m pytest tests/ -v
  ```
- **Run specific test module:**
  ```bash
  PYTHONPATH=src python3 -m unittest tests/test_matcher.py
  ```
- **Run CLI commands locally:**
  ```bash
  PYTHONPATH=src python3 -m career_forge.cli resume audit --resume tests/fixtures/synthetic_resumes/alex_rivera_backend.md
  PYTHONPATH=src python3 -m career_forge.cli match --resume tests/fixtures/synthetic_resumes/alex_rivera_backend.md --query "Distributed Systems" --report
  PYTHONPATH=src python3 -m career_forge.cli verify-email recruiter@github.com
  ```
- **Run MCP Server:**
  ```bash
  PYTHONPATH=src python3 -m career_forge.mcp_server
  ```

---

## 🏗️ Architecture & Module Organization

```
src/career_forge/
├── cli.py                   # Rich interactive CLI entrypoint
├── mcp_server.py            # Model Context Protocol stdio server
├── core/                    # SQLite database (WAL mode), Config, Custom Exceptions
├── parsers/                 # Parsers: TextParser, DocxParser, LatexParser, PdfParser
├── engines/
│   ├── digest.py            # 150-token structured profile digest extractor
│   ├── matcher.py           # 4-factor role fit scoring engine
│   ├── discovery.py         # Multi-tier requisition discovery & strategy reporting
│   ├── resume_builder.py    # 100-pt ATS audit & LaTeX synthesizer
│   ├── compiler.py          # Deterministic LaTeX compiler (Tectonic/XeLaTeX/pdfLaTeX)
│   └── recruiter_radar.py   # Non-blocking DNS/MX verifier & anti-bounce filter
└── templates/               # LaTeX role templates (swe, sdet, aiml, lead) & Markdown reports
```

---

## 🔒 Strict Zero-PII Policy

- **Never** inject real personal names, emails, phone numbers, addresses, or private company information into fixtures, code, or documentation.
- Use only synthetic personas from `tests/fixtures/synthetic_resumes/` (e.g., *Alex Rivera*, *Jordan Taylor*, *Morgan Chen*).

---

## 🛡️ Agent Tool Permissions & Guidelines

- Autonomous testing and linting (`python3 -m unittest discover tests`, `ruff check`, `ruff format`) are safe to execute without additional prompts.
- All file creations should follow the `src/career_forge` layout with matching test coverage in `tests/`.
