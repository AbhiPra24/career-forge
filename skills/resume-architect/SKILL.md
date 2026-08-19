---
name: resume-architect
description: >-
  ATS-optimized LaTeX resume craftsman, 100-point heuristic auditor, Google XYZ metric enhancer,
  and multi-format bidirectional converter. Ingests candidate background from any format (.pdf, .docx, .tex, .md, .txt, .json),
  evaluates action verb and metric density, generates role-tailored LaTeX resumes (SWE, SDET, AI/ML, Lead),
  and deterministically compiles to PDF via Tectonic or LaTeX.
  Trigger with `/resume-audit [resume_path]` or `/resume-build [resume_path] [role]`.
parameters:
  resume:
    type: string
    description: Path to candidate resume file
    required: true
  role:
    type: string
    description: Target role archetype (swe, sdet, aiml, lead)
    default: swe
  compile:
    type: boolean
    description: Compile generated LaTeX to PDF
    default: true
---

# ATS Resume Architect & LaTeX Compiler (`resume-architect`)

A high-craftsmanship resume engine delivering modern 1-page vertical density, Google XYZ metric quantification (*Accomplished [X] as measured by [Y], by doing [Z]*), and 100-point ATS heuristic scoring.

---

## Capabilities

1. **100-Point ATS Heuristic Scoring:**
   - Action Verb Strength (25 pts)
   - Metric & Google XYZ Quantification (25 pts)
   - Standard Headings & Structure (25 pts)
   - 1-Page Layout Density & Brevity (25 pts)
2. **Role-Tailored LaTeX Synthesis:**
   - Pre-built, battle-tested templates: `swe`, `sdet`, `aiml`, `lead`.
3. **Deterministic Compiler Bridge:**
   - Automatic fallback discovery: `tectonic` -> `xelatex` -> `pdflatex` -> graceful `.tex` preservation.

---

## Usage

### CLI Execution
```bash
# 1. Audit resume ATS health
cforge resume audit --resume path/to/resume.pdf

# 2. Build role-tailored LaTeX and compiled PDF
cforge resume build --resume path/to/resume.pdf --role swe --compile --output ./dist
```

### Agent / MCP Execution
```json
{
  "name": "resume_architect_build",
  "arguments": {
    "resume_path": "/path/to/resume.pdf",
    "role": "aiml",
    "compile_pdf": true
  }
}
```
