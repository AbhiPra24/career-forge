# Building CareerForge: How We Engineered a 150-Token Career Intelligence & ATS Resume Engine

[INSERT COVER IMAGE: docs/AI_Career_Intelligence_Engine.png]

Over the past two years, the internet has been flooded with generic AI resume builders. If you look under the hood of most of these tools, you will find the exact same flawed pattern:

- Context Window Bloat: They dump 4-to-6 pages of unparsed PDF text into every single prompt turn, consuming 5,000 to 10,000 tokens per query.
- Hallucinated ATS Scores: They ask an LLM "Rate this resume from 1 to 100", generating arbitrary, non-deterministic numbers with zero heuristic grounding.
- Format Destruction: They output unstructured text or broken Word templates that get immediately filtered out by enterprise ATS parsers like Taleo, Greenhouse, Workday, and Lever.
- Cold Outreach Blackholes: They generate generic cold emails to unmonitored careers@ or info@ distribution lists that trigger spam traps and bounce.

To solve this, I engineered CareerForge (cforge) — an open-source, token-optimized career intelligence suite and Model Context Protocol (MCP) server built with Python 3.10+, SQLite WAL concurrency, and deterministic LaTeX compilation.

Here is the complete engineering and architectural breakdown.

---

## 1. Token Efficiency: The ~150-Token Profile Digest Pattern

Feeding full multi-page resumes into multi-turn conversational AI agents (Claude, Gemini, Cursor) quickly exhausts token limits, increases latency, and drives up API costs.

Instead of re-parsing the entire resume on every query, CareerForge ingests the source document (PDF, DOCX, LaTeX, Markdown, or JSON) once through modular parsers and compresses it into a high-density, structured Profile Digest of roughly 150 tokens.

Example of an extracted digest:
• Candidate Name: Alex Rivera
• Seniority Level: Senior (7+ Years of Experience)
• Core Tech Stack: Go, Rust, Python, Kubernetes, Kafka, gRPC, Redis, PostgreSQL
• Top Quantified Metric: Architected streaming pipeline handling 45,000 req/s with sub-15ms P99 latency
• Primary Domains: Distributed Systems, Cloud Infrastructure, Event-Driven Architecture
• Education: B.S. in Computer Science (UC Berkeley)

The Result:
An 85% to 90% reduction in token consumption across multi-turn reasoning loops, enabling instant batch evaluations against hundreds of open requisitions in fractions of a second.

---

## 2. The 4-Factor Calibrated Role Matching Matrix

Matching candidate resumes to job descriptions is often reduced to naive keyword counting. CareerForge implements a calibrated multi-dimensional scoring formula with normalized weights:

Fit Score Formula:
Fit Score = (40% Skill Match) + (30% Experience Depth) + (20% Market Demand) + (10% Competitive Edge)

How Each Factor is Evaluated:
1. Skill Overlap (40%): Direct stack and infrastructure tool match percentage.
2. Seniority Depth (30%): Years of experience calibrated against the target role tier.
3. Market Demand (20%): Hiring velocity across Tier 1 Product Unicorns, Tech Giants, and Startups.
4. Competitive Edge (10%): Differentiating niche competencies and modern ecosystem tools.

Matches are automatically classified into Action Batches:
• Batch 1 (Immediate Apply): Fit Score 85% and above — High stack alignment, top-priority applications.
• Batch 2 (Targeted Prep): Fit Score 70% to 84% — Strong fit requiring targeted cover letters or portfolio highlights.
• Batch 3 (Safety Net): Fit Score below 70% — Secondary market options.

---

## 3. 100-Point ATS Heuristic Audit & Google XYZ Quantification

Instead of asking an AI model to guess a score, CareerForge runs a deterministic 100-point heuristic audit broken into four distinct 25-point pillars:

1. Action Verb Density (25 Points)
Scans for strong technical leadership verbs (Architected, Spearheaded, Engineered, Optimized) while penalizing passive expressions (Responsible for, Assisted with).

2. Google XYZ Metric Quantification (25 Points)
Validates that accomplishments follow the proven Google formula:
"Accomplished [X], as measured by [Y], by doing [Z]"
The engine detects scale, volumes, percentages, latency reductions, and duration transitions (such as "from 2 weeks to 2 days").

3. Canonical Section Architecture (25 Points)
Ensures structural compliance across standard alias synonyms (Skills matching Technologies, Experience matching Work History).

4. Vertical Density & Line Budget (25 Points)
Enforces strict 1-page vertical density thresholds (350 to 700 words), flagging resumes that are too sparse or overly verbose.

You can inspect your resume bullet-by-bullet from the terminal:
cforge resume audit --resume resume.pdf --detailed

---

## 4. Role-Tailored LaTeX Synthesis & PDF Compilation

CareerForge includes tight, 1-page LaTeX templates engineered for specific engineering archetypes:
• swe (Backend & Distributed Systems)
• sdet (QA Automation & Performance Engineering)
• aiml (Applied AI & LLM Systems)
• fullstack (TypeScript, React, Next.js, Node.js)
• devops (Kubernetes, Terraform, Cloud Infrastructure)
• lead (Principal Engineer & Engineering Management)

Sandboxed Compilation:
Using the CompilerBridge, the engine compiles via Tectonic, XeLaTeX, or pdfLaTeX with strict -no-shell-escape macro sandboxing to prevent arbitrary code execution, preserving clean LaTeX sources if local compilers are unavailable.

---

## 5. Recruiter Radar: Stopping Cold Outreach Bounces

Sending cold emails to invalid addresses or unmonitored distribution lists destroys domain sender reputation. CareerForge includes Recruiter Radar:

• Thread-Safe DNS and MX Host Resolution: Performs fast (under 2 seconds) MX record verification without mutating global socket timeouts.
• SSRF Guard: Blocks internal metadata and loopback host inquiries (127.0.0.1, 169.254.169.254).
• Catch-All & Generic Alias Detection: Flags distribution lists (careers@, hiring@, jobs@) that lead to unread ticket queues, reserving high-confidence flags for direct named contacts.
• 3-Tier Cold Messaging Playbook: Generates custom outreach copy tailored for Hiring Managers, Technical Recruiters, and Engineer-to-Engineer coffee chats.

---

## 6. Dual-Interface Symmetry: CLI + Model Context Protocol (MCP)

CareerForge was built from day one with dual-interface symmetry:

1. Rich Interactive CLI (cforge): Human-facing terminal interface with clean color-coded tables, panels, and machine-readable JSON support for piping into automated workflows.
2. Model Context Protocol (MCP) Server: A stdio JSON-RPC server allowing autonomous AI pair programmers (Claude Code, Cursor, Gemini CLI, Antigravity) to call CareerForge tools natively.

Exposed MCP Tools:
• talent_scout_match: 4-factor role matching and requisition discovery
• resume_architect_audit: 100-point ATS heuristic audit
• resume_architect_build: Role-tailored LaTeX and PDF compilation
• resume_architect_convert: Headless conversion between LaTeX, Markdown, and JSON
• recruiter_radar_verify: Real-time DNS/MX email deliverability verification

---

## 7. Open Source & Zero-PII Guarantee

CareerForge is strictly privacy-first:
• 100% Zero-PII Policy: All test suites and fixtures use synthetic, fictitious personas (Alex Rivera, Jordan Taylor, Morgan Chen).
• Zero Telemetry: No external tracking, analytics, or phone-home requests.
• MIT Licensed: Free and open-source for developers and teams.

---

## Getting Started & Links

You can install and run CareerForge locally in under a minute:

Step 1: Clone and install
git clone https://github.com/AbhiPra24/career-forge.git
cd career-forge
make install-all

Step 2: Run an ATS audit
cforge resume audit -r resume.pdf --detailed

Step 3: Match live requisitions
cforge match -r resume.pdf -q "Senior Backend Engineer" --report

Step 4: Verify recruiter deliverability
cforge verify-email recruiter@company.com

Links:
• Interactive Documentation & Video: https://abhipra24.github.io/career-forge/
• GitHub Repository: https://github.com/AbhiPra24/career-forge

---

How are you managing resume tailoring and AI token efficiency in your career navigation workflow? Let me know your thoughts and feedback in the comments!
