---
name: recruiter-radar
description: >-
  Recruiter email deliverability verification, non-blocking DNS/MX health checker,
  anti-bounce catch-all detection, and personalized 3-layer outreach messaging engine.
  Prevents spam flags and email bounces before sending candidate outreach.
  Trigger with `/verify-email [email_address]`.
parameters:
  email:
    type: string
    description: Recruiter or hiring manager email address to verify
    required: true
---

# Recruiter Radar & Outreach Deliverability Engine (`recruiter-radar`)

Enforces deliverability guardrails before reaching out to engineering managers and technical talent partners.

---

## Deliverability Guardrails

1. **RFC 5322 Syntax Check:** Strict regex formatting validation.
2. **Non-Blocking DNS/MX Verification:** Real-time host resolution with strict timeout ($\le 2\text{s}$) and SQLite negative caching.
3. **Anti-Bounce Catch-All Filter:** Detects unmonitored generic prefixes (`recruiting@`, `careers@`, `jobs@`, `hr@`, `info@`, `contact@`).
4. **3-Layer Outreach Generator:** Produces tailored cold email copy for Hiring Managers, Technical Recruiters, and Peer Referrals.

---

## Usage

### CLI Execution
```bash
# Verify email deliverability
cforge verify-email recruiter@targetcompany.com
```

### Agent / MCP Execution
```json
{
  "name": "recruiter_radar_verify",
  "arguments": {
    "email": "sarah.lead@company.com"
  }
}
```
