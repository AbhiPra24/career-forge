# GEMINI.md – CareerForge Guidelines & Developer Reference

CareerForge (`career-forge`) is an open-source, production-grade career intelligence, ATS resume tailoring, and recruiter outreach engine with Rich CLI and Model Context Protocol (MCP) server support.

---

## ⚡ Quick Reference Commands

- **Unit Tests:** `PYTHONPATH=src python3 -m unittest discover tests`
- **CLI Invocations:**
  - Audit: `PYTHONPATH=src python3 -m career_forge.cli resume audit --resume <path> [--json]`
  - Match: `PYTHONPATH=src python3 -m career_forge.cli match --resume <path> --query <keywords> [--report] [--json]`
  - Build: `PYTHONPATH=src python3 -m career_forge.cli resume build --resume <path> --role <swe|sdet|aiml|lead> [--compile]`
  - Convert: `PYTHONPATH=src python3 -m career_forge.cli resume convert --input <path> --to <md|txt|json>`
  - Verify: `PYTHONPATH=src python3 -m career_forge.cli verify-email <email> [--json]`
- **MCP Server Stdio:** `PYTHONPATH=src python3 -m career_forge.mcp_server`

---

## 🎯 Design Rules & Architecture

1. **Token Optimization:** Always leverage `ProfileDigestEngine` (~150 tokens) before multi-turn LLM reasoning.
2. **Concurrency Safety:** Always access SQLite via `DatabaseManager.get_connection()` which enforces `PRAGMA journal_mode = WAL;` and `PRAGMA busy_timeout = 5000;`.
3. **Deterministic Fallbacks:** The LaTeX compiler (`CompilerBridge`) must degrade gracefully to preserving `.tex` files when `tectonic` or `latex` is not installed on the host.
4. **Zero-PII Compliance:** Only fictitious personas from `tests/fixtures/synthetic_resumes/` are allowed in tests.
