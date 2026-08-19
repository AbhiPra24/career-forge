---
name: talent-scout
description: >-
  Universal career market intelligence, 4-factor requisition matching, candidate audit,
  and strategy report generation engine. Token-optimized for ultra-fast, low-cost execution on
  lightweight models. Evaluates fit scores (0-100%) across company tiers (Product Unicorns, GCCs,
  Startups, IT Services) and produces a comprehensive `[CANDIDATE]_JOB_RESEARCH_[YEAR].md` report.
  Trigger with `/talent-scout [resume_path] [optional_query]`.
parameters:
  resume:
    type: string
    description: Path to candidate resume file (.pdf, .docx, .tex, .md, .txt)
    required: true
  query:
    type: string
    description: Target job search keywords or role title (e.g. "Senior Backend Engineer", "Lead SDET")
    required: false
  location:
    type: string
    description: Target location filter (e.g. "Remote", "San Francisco", "New York")
    required: false
  limit:
    type: integer
    description: Maximum job listings to process (default: 10)
    default: 10
---

# Universal Career Scout & Market Strategy Engine (`talent-scout`)

An intelligent end-to-end recruitment research, role-matching, and career strategy engine for software engineers, SDETs, platform/DevOps engineers, data engineers, ML engineers, product managers, and technology leaders.

Engineered for **ultra-low token consumption (85–90% reduction)** and cross-platform execution via CLI and MCP.

---

## Token-Optimized Pipeline

1. **Ingest & Extract Profile Digest:** Auto-generates a structured ~150-token Profile Digest (Name, Career Stage, Core Stack, Top Metrics).
2. **Requisition Discovery:** Discovers live requisitions across 4 company tiers (Product Unicorns, Tech Giants/GCCs, Startups, IT Services).
3. **4-Factor Fit Scoring:** Calibrates match across Skill Match (40%), Experience Depth (30%), Market Demand (20%), and Competitive Edge (10%).
4. **Strategy Markdown Report:** Generates `[CANDIDATE]_JOB_RESEARCH_[YEAR].md` with open positions table and outreach playbook.

---

## Usage

### CLI Execution
```bash
# Evaluate resume against live market requisitions
cforge match --resume path/to/resume.pdf --query "Senior Backend Engineer" --report
```

### Agent / MCP Execution
```json
{
  "name": "talent_scout_match",
  "arguments": {
    "resume_path": "/path/to/resume.pdf",
    "query": "Senior Distributed Systems Engineer",
    "limit": 10
  }
}
```
