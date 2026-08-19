"""
Model Context Protocol (MCP) Stdio Server for CareerForge
Exposes CareerForge tools to AI agents (Claude, Gemini, Cursor, Antigravity) over standard JSON-RPC.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from career_forge.parsers import parse_resume_file
from career_forge.engines.digest import ProfileDigestEngine
from career_forge.engines.matcher import TalentScoutEngine
from career_forge.engines.discovery import DiscoveryEngine
from career_forge.engines.resume_builder import ResumeArchitectEngine
from career_forge.engines.compiler import CompilerBridge
from career_forge.engines.recruiter_radar import RecruiterRadarEngine

SERVER_INFO = {
    "name": "career-forge",
    "version": "0.1.0"
}

TOOLS_SPEC = [
    {
        "name": "talent_scout_match",
        "description": "Extracts compact candidate digest, discovers live open requisitions across company tiers, and calculates 4-factor fit scores (0-100%).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resume_path": {"type": "string", "description": "Absolute path to candidate resume file (.pdf, .docx, .tex, .md, .txt)"},
                "query": {"type": "string", "description": "Target role or technology search keywords (e.g. 'Senior Backend Engineer')"},
                "location": {"type": "string", "description": "Location filter (e.g. 'Remote', 'San Francisco')", "default": "Remote"},
                "limit": {"type": "integer", "description": "Maximum job requisitions to evaluate (default 10)", "default": 10}
            },
            "required": ["resume_path"]
        }
    },
    {
        "name": "resume_architect_audit",
        "description": "Performs a 100-point ATS Heuristic Audit (Action Verbs, Google XYZ Metric Quantification, Structure, Brevity).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resume_path": {"type": "string", "description": "Path to candidate resume file"}
            },
            "required": ["resume_path"]
        }
    },
    {
        "name": "resume_architect_build",
        "description": "Generates a role-tailored LaTeX resume and compiles it directly to PDF using Tectonic / LaTeX.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "resume_path": {"type": "string", "description": "Path to source resume file"},
                "role": {"type": "string", "enum": ["swe", "sdet", "aiml", "lead"], "description": "Role template archetype", "default": "swe"},
                "compile_pdf": {"type": "boolean", "description": "Whether to compile .tex to .pdf", "default": True},
                "output_dir": {"type": "string", "description": "Output directory for generated files"}
            },
            "required": ["resume_path"]
        }
    },
    {
        "name": "recruiter_radar_verify",
        "description": "Performs email deliverability verification, non-blocking DNS/MX host resolution, and anti-bounce catch-all detection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Target recruiter or hiring manager email address"}
            },
            "required": ["email"]
        }
    }
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches tool call to corresponding CareerForge engine."""
    if name == "talent_scout_match":
        resume_path = Path(arguments["resume_path"])
        doc = parse_resume_file(resume_path)
        digest = ProfileDigestEngine().extract_digest(doc)
        matcher = TalentScoutEngine()
        discovery = DiscoveryEngine()
        jobs = discovery.discover_jobs(
            query=arguments.get("query", ""),
            location=arguments.get("location", "Remote"),
            limit=arguments.get("limit", 10)
        )
        evaluations = []
        for job in jobs:
            ev = matcher.evaluate_fit(digest, job)
            evaluations.append({
                "company": job.company,
                "title": job.title,
                "tier": job.tier,
                "location": job.location,
                "salary_range": job.salary_range,
                "fit_score": ev.fit_score,
                "action_batch": ev.action_batch,
                "matched_skills": ev.matched_skills,
                "missing_skills": ev.missing_skills
            })
        return {
            "candidate_digest": digest.to_dict(),
            "requisitions_evaluated_count": len(evaluations),
            "evaluations": evaluations
        }

    elif name == "resume_architect_audit":
        resume_path = Path(arguments["resume_path"])
        doc = parse_resume_file(resume_path)
        audit = ResumeArchitectEngine().audit_ats_score(doc)
        return audit.to_dict()

    elif name == "resume_architect_build":
        resume_path = Path(arguments["resume_path"])
        doc = parse_resume_file(resume_path)
        role = arguments.get("role", "swe")
        engine = ResumeArchitectEngine()
        tex_code = engine.generate_latex(doc, role_template=role)
        
        out_dir = Path(arguments.get("output_dir") or resume_path.parent)
        out_dir.mkdir(parents=True, exist_ok=True)
        tex_path = out_dir / f"{doc.clean_text.splitlines()[0].replace(' ', '_').strip('#')}_{role.upper()}_Resume.tex"
        tex_path.write_text(tex_code, encoding="utf-8")

        pdf_path_str = None
        warning_str = None
        if arguments.get("compile_pdf", True):
            comp_res = CompilerBridge().compile_latex_to_pdf(tex_path, output_dir=out_dir)
            if comp_res.success:
                pdf_path_str = str(comp_res.pdf_path)
            else:
                warning_str = comp_res.warning

        return {
            "latex_path": str(tex_path),
            "pdf_path": pdf_path_str,
            "warning": warning_str
        }

    elif name == "recruiter_radar_verify":
        radar = RecruiterRadarEngine()
        status = radar.verify_email(arguments["email"])
        return status.to_dict()

    else:
        raise ValueError(f"Unknown tool: {name}")


def process_jsonrpc_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes a single incoming JSON-RPC 2.0 message."""
    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_SPEC}
        }
    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            res = handle_tool_call(tool_name, args)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": str(e)}
            }
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    return None


def run_mcp_server():
    """Stdio loop for Model Context Protocol."""
    for line in sys.stdin:
        line_str = line.strip()
        if not line_str:
            continue
        try:
            msg = json.loads(line_str)
            response = process_jsonrpc_message(msg)
            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
