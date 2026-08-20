# ⚡ CareerForge (`career-forge`)

> **Production-Grade Career Intelligence, ATS Resume Crafting & Verified Recruiter Outreach Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](pyproject.toml)
[![Architecture: MCP Ready](https://img.shields.io/badge/MCP-Ready-purple.svg)](src/career_forge/mcp_server.py)
[![Privacy: Zero-PII Guarantee](https://img.shields.io/badge/Privacy-100%25%20Zero--PII-success.svg)](#privacy--zero-pii-guarantee)
[![LinkedIn: Read Article](https://img.shields.io/badge/LinkedIn-Technical%20Article-0A66C2.svg?logo=linkedin)](https://www.linkedin.com/pulse/building-careerforge-how-we-engineered-150-token-career-prakash-cdirf/)

---

## 🌟 Highlights

- **⚡ Token-Optimized Pipeline (85–90% cost reduction):** Automatically compresses unstructured resumes of any format into a structured ~150-token **Profile Digest** once, reusing it across multi-turn queries.
- **🎯 4-Factor Fit Scoring:** Computes calibrated role compatibility across *Skill Match (40%)*, *Experience Depth (30%)*, *Market Demand (20%)*, and *Competitive Edge (10%)*.
- **📄 ATS-Optimized LaTeX Resume Builder:** Features 100-point heuristic scoring (Google XYZ metric quantification, action verb density, 1-page vertical layout) and deterministic compilation to PDF via Tectonic, XeLaTeX, or pdfLaTeX.
- **🔄 Multi-Format Bidirectional Conversion:** Ingests PDF, DOCX (sequential XML traversal), LaTeX, Markdown, Plain Text, and JSON.
- **🛡️ Recruiter Radar & Deliverability Engine:** Non-blocking DNS/MX validation ($\le 2\text{s}$ timeout) with anti-bounce catch-all detection and 3-layer tailored outreach copy generation.
- **🤖 Dual-Interface Symmetry:** Interactive terminal CLI (`cforge`) + Model Context Protocol (`MCP`) server for AI agents (Claude, Gemini, Cursor, Antigravity).

---

## 🏗️ Architecture

```
career-forge/
├── pyproject.toml                     # Modern build config & CLI console scripts
├── README.md                          # Comprehensive docs & usage
├── skills/                            # First-Class Agent Skills
│   ├── talent-scout/SKILL.md          # 4-factor matching & requisition discovery
│   ├── resume-architect/SKILL.md      # ATS scoring, LaTeX build & conversion
│   └── recruiter-radar/SKILL.md       # DNS/MX deliverability verification
├── src/career_forge/
│   ├── cli.py                         # Rich interactive CLI
│   ├── mcp_server.py                  # Model Context Protocol stdio server
│   ├── core/                          # SQLite (WAL mode), config, typed exceptions
│   ├── parsers/                       # PDF, DOCX (w:p & w:tbl), LaTeX, MD, JSON
│   ├── engines/                       # Digest, Matcher, ResumeBuilder, Compiler, RecruiterRadar
│   └── templates/                     # LaTeX role templates & Strategy Markdown templates
└── tests/                             # Pytest suite with 100% synthetic personas
    └── fixtures/synthetic_resumes/
```

---

## 🚀 Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/career-forge.git
cd career-forge

# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

### 2. Basic CLI Usage

```bash
# 1. Audit resume ATS score and metric density
cforge resume audit --resume path/to/resume.pdf

# 2. Build role-tailored LaTeX and compiled PDF resume
cforge resume build --resume path/to/resume.pdf --role swe --compile --output ./dist

# 3. Match candidate against open requisitions and generate strategy report
cforge match --resume path/to/resume.pdf --query "Senior Backend Engineer" --location "Remote" --report

# 4. Verify recruiter email deliverability & MX health
cforge verify-email recruiter@targetcompany.com
```

### 3. Running as an MCP Server

Add `career-forge` to your AI assistant's MCP configuration (Claude Desktop, Cursor, Antigravity):

```json
{
  "mcpServers": {
    "career-forge": {
      "command": "cforge",
      "args": ["mcp-serve"]
    }
  }
}
```

---

## 🔒 Privacy & Zero-PII Guarantee

CareerForge is strictly designed with privacy-first principles:
- **No data telemetry:** Zero external tracking or phone-home telemetry.
- **Synthetic Test Suites:** All fixtures, tests, and mock files use fictitious personas (e.g. *Alex Rivera*, *Jordan Taylor*, *Morgan Chen*).
- **Safe by default:** No sensitive environment variables or credentials are ever written into repository tracking.

---

## 📜 License

Distributed under the [MIT License](LICENSE).
