"""
Interactive Command-Line Interface for CareerForge (`cforge`)
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False

from career_forge.parsers import parse_resume_file
from career_forge.engines.digest import ProfileDigestEngine
from career_forge.engines.matcher import TalentScoutEngine
from career_forge.engines.discovery import DiscoveryEngine
from career_forge.engines.resume_builder import ResumeArchitectEngine
from career_forge.engines.compiler import CompilerBridge
from career_forge.engines.recruiter_radar import RecruiterRadarEngine


def print_banner():
    if HAS_RICH and console:
        console.print(Panel(
            "[bold cyan]⚡ CareerForge (`cforge`)[/bold cyan]\n"
            "[italic white]Production-Grade Career Intelligence & Resume Crafting Engine[/italic white]",
            border_style="cyan"
        ))
    else:
        print("=== CareerForge CLI ===")


def cmd_match(args):
    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"Error: Resume file not found at {resume_path}")
        sys.exit(1)

    doc = parse_resume_file(resume_path)
    digest_engine = ProfileDigestEngine()
    digest = digest_engine.extract_digest(doc)

    discovery = DiscoveryEngine()
    matcher = TalentScoutEngine()
    jobs = discovery.discover_jobs(query=args.query or "", location=args.location or "Remote", limit=args.limit)

    evaluations = [(job, matcher.evaluate_fit(digest, job)) for job in jobs]
    evaluations.sort(key=lambda x: x[1].fit_score, reverse=True)

    if getattr(args, "json", False):
        payload = {
            "candidate_digest": digest.to_dict(),
            "requisitions": [
                {
                    "company": job.company,
                    "title": job.title,
                    "tier": job.tier,
                    "location": job.location,
                    "salary_range": job.salary_range,
                    "fit_score": ev.fit_score,
                    "action_batch": ev.action_batch,
                    "matched_skills": ev.matched_skills,
                    "missing_skills": ev.missing_skills
                }
                for job, ev in evaluations
            ]
        }
        print(json.dumps(payload, indent=2))
        return

    print_banner()
    if HAS_RICH and console:
        console.print(f"[bold green]✔ Ingested & Digested:[/bold green] [bold]{digest.candidate_name}[/bold] ({digest.career_stage})")
        console.print(f"[cyan]Core Stack:[/cyan] {', '.join(digest.core_stack)}")
        if digest.top_metrics:
            console.print(f"[cyan]Top Metric:[/cyan] {digest.top_metrics[0]}")
    else:
        print(f"Ingested: {digest.candidate_name} ({digest.career_stage})")

    if HAS_RICH and console:
        table = Table(title="🎯 Live Requisitions & 4-Factor Fit Scores", show_header=True, header_style="bold magenta")
        table.add_column("Company", style="bold white")
        table.add_column("Role Title", style="cyan")
        table.add_column("Tier", style="yellow")
        table.add_column("Fit Score", justify="center", style="bold green")
        table.add_column("Action Batch", style="white")
        table.add_column("Matched Tech", style="dim")

        for job, ev in evaluations:
            score_color = "green" if ev.fit_score >= 85 else ("yellow" if ev.fit_score >= 70 else "red")
            matched_str = ", ".join(ev.matched_skills[:3]) if ev.matched_skills else "General"
            table.add_row(
                job.company,
                job.title,
                job.tier.split("(")[0].strip(),
                f"[{score_color}]{ev.fit_score}%[/{score_color}]",
                ev.action_batch.split("(")[1].rstrip(")"),
                matched_str
            )
        console.print(table)
    else:
        for job, ev in evaluations:
            print(f"- {job.company} | {job.title} | Score: {ev.fit_score}% | {ev.action_batch}")

    if args.report:
        report_md = discovery.generate_strategy_report(digest, jobs, matcher)
        report_path = resume_path.parent / f"{digest.candidate_name.replace(' ', '_').upper()}_JOB_RESEARCH_2026.md"
        report_path.write_text(report_md, encoding="utf-8")
        if HAS_RICH and console:
            console.print(f"[bold green]✔ Strategy Report written to:[/bold green] [underline]{report_path}[/underline]")
        else:
            print(f"Strategy Report written to: {report_path}")


def cmd_resume_audit(args):
    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"Error: Resume file not found at {resume_path}")
        sys.exit(1)

    doc = parse_resume_file(resume_path)
    engine = ResumeArchitectEngine()
    audit = engine.audit_ats_score(doc)

    if getattr(args, "json", False):
        print(json.dumps(audit.to_dict(), indent=2))
        return

    print_banner()
    if HAS_RICH and console:
        score_color = "green" if audit.total_score >= 80 else ("yellow" if audit.total_score >= 65 else "red")
        console.print(Panel(
            f"[bold {score_color}]Overall ATS Score: {audit.total_score}/100[/bold {score_color}]\n\n"
            f"• Action Verb Density: [bold]{audit.action_verb_score}/25[/bold]\n"
            f"• Metric & Google XYZ Quantification: [bold]{audit.metric_density_score}/25[/bold]\n"
            f"• Standard Structure & Sections: [bold]{audit.structure_score}/25[/bold]\n"
            f"• Brevity & Vertical Density: [bold]{audit.brevity_score}/25[/bold]",
            title="📊 100-Point ATS Heuristic Breakdown",
            border_style=score_color
        ))
        if audit.recommendations:
            console.print("[bold yellow]Recommendations for 90+ Score:[/bold yellow]")
            for rec in audit.recommendations:
                console.print(f"  [yellow]• {rec}[/yellow]")

        if getattr(args, "detailed", False) and audit.bullet_evaluations:
            bullet_table = Table(title="🔍 Bullet-by-Bullet Google XYZ Inspection", show_header=True, header_style="bold cyan")
            bullet_table.add_column("Bullet Text", style="white", max_width=45)
            bullet_table.add_column("Status", justify="center")
            bullet_table.add_column("Actionable Recommendation", style="dim yellow")
            
            for b in audit.bullet_evaluations:
                status_str = "[green]✔ Optimal[/green]" if b["status"] == "Optimal" else "[yellow]⚠ Needs Metric[/yellow]"
                bullet_table.add_row(
                    b["bullet"],
                    status_str,
                    b["suggestion"]
                )
            console.print(bullet_table)
    else:
        print(f"ATS Score: {audit.total_score}/100")
        print(f"Verbs: {audit.action_verb_score}/25, Metrics: {audit.metric_density_score}/25, Structure: {audit.structure_score}/25, Brevity: {audit.brevity_score}/25")


def cmd_resume_convert(args):
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)

    doc = parse_resume_file(input_path)
    engine = ResumeArchitectEngine()
    converted_text = engine.convert_format(doc, target_format=args.to)

    if args.output:
        out_file = Path(args.output)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(converted_text, encoding="utf-8")
        if HAS_RICH and console:
            console.print(f"[bold green]✔ Converted document saved to:[/bold green] [underline]{out_file}[/underline]")
        else:
            print(f"Converted document saved to: {out_file}")
    else:
        print(converted_text)


def cmd_resume_build(args):
    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"Error: Resume file not found at {resume_path}")
        sys.exit(1)

    print_banner()
    doc = parse_resume_file(resume_path)
    engine = ResumeArchitectEngine()
    tex_code = engine.generate_latex(doc, role_template=args.role)

    out_dir = Path(args.output or resume_path.parent)
    out_dir.mkdir(parents=True, exist_ok=True)
    candidate_slug = re.sub(r'[\s_]+', '_', engine._extract_name(doc).strip().replace('#', ''))
    tex_path = out_dir / f"{candidate_slug}_{args.role.upper()}_Resume.tex"
    tex_path.write_text(tex_code, encoding="utf-8")

    if HAS_RICH and console:
        console.print(f"[bold green]✔ Tailored LaTeX Generated:[/bold green] [underline]{tex_path}[/underline]")
    else:
        print(f"LaTeX Generated: {tex_path}")

    if args.compile:
        compiler = CompilerBridge()
        res = compiler.compile_latex_to_pdf(tex_path, output_dir=out_dir)
        if res.success:
            if HAS_RICH and console:
                console.print(f"[bold green]✔ PDF Compiled successfully via {res.engine_used}:[/bold green] [underline]{res.pdf_path}[/underline]")
            else:
                print(f"PDF Compiled: {res.pdf_path}")
        else:
            if HAS_RICH and console:
                console.print(f"[bold yellow]⚠ {res.warning}[/bold yellow]")
            else:
                print(f"Warning: {res.warning}")


def cmd_verify_email(args):
    radar = RecruiterRadarEngine()
    status = radar.verify_email(args.email)

    if getattr(args, "json", False):
        print(json.dumps(status.to_dict(), indent=2))
        return

    print_banner()
    if HAS_RICH and console:
        badge_style = "green" if "HIGH" in status.confidence else ("yellow" if "CAUTION" in status.confidence else "red")
        console.print(Panel(
            f"[bold]Target Email:[/bold] {status.email}\n"
            f"[bold]Confidence:[/bold] [{badge_style}]{status.confidence}[/{badge_style}]\n"
            f"[bold]RFC 5322 Syntax:[/bold] {'✔ Valid' if status.is_valid_syntax else '✖ Invalid'}\n"
            f"[bold]Domain DNS/MX Resolves:[/bold] {'✔ Yes' if status.domain_resolves else '✖ No'}\n"
            f"[bold]Generic Unmonitored Alias:[/bold] {'⚠ Yes (Spam / Bounce Risk)' if status.is_generic_alias else '✔ No (Named Personnel)'}",
            title="🛡️ Recruiter Email Deliverability Evaluation",
            border_style=badge_style
        ))
        if status.warnings:
            console.print("[bold red]Warnings:[/bold red]")
            for w in status.warnings:
                console.print(f"  [red]• {w}[/red]")
    else:
        print(f"Email: {status.email} | Confidence: {status.confidence}")


def cmd_mcp_serve(args):
    from career_forge.mcp_server import run_mcp_server
    run_mcp_server()


def main():
    parser = argparse.ArgumentParser(
        prog="cforge",
        description="CareerForge: Production Career Intelligence & ATS Resume Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Match command
    p_match = subparsers.add_parser("match", help="Match candidate profile against live requisitions")
    p_match.add_argument("--resume", "-r", required=True, help="Path to resume file (.pdf, .docx, .tex, .md, .txt)")
    p_match.add_argument("--query", "-q", default="", help="Target keyword or role title query")
    p_match.add_argument("--location", "-l", default="Remote", help="Location filter")
    p_match.add_argument("--limit", type=int, default=10, help="Maximum requisitions to evaluate")
    p_match.add_argument("--report", action="store_true", help="Generate strategy markdown report")
    p_match.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Resume subparser
    p_resume = subparsers.add_parser("resume", help="ATS scoring, LaTeX generation, and conversion")
    resume_subs = p_resume.add_subparsers(dest="resume_command", help="Resume actions")

    # Resume Audit
    p_audit = resume_subs.add_parser("audit", help="100-point ATS Heuristic Scoring")
    p_audit.add_argument("--resume", "-r", required=True, help="Path to resume file")
    p_audit.add_argument("--detailed", "-d", action="store_true", help="Print granular bullet-by-bullet Google XYZ inspection")
    p_audit.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # Resume Build
    p_build = resume_subs.add_parser("build", help="Build role-tailored LaTeX and compile to PDF")
    p_build.add_argument("--resume", "-r", required=True, help="Path to resume file")
    p_build.add_argument("--role", default="swe", choices=["swe", "sdet", "aiml", "lead", "fullstack", "devops", "platform", "data"], help="Role template archetype")
    p_build.add_argument("--compile", "-c", action="store_true", help="Compile .tex to .pdf via Tectonic/LaTeX")
    p_build.add_argument("--output", "-o", default=None, help="Output directory")

    # Resume Convert
    p_convert = resume_subs.add_parser("convert", help="Convert resume between formats (md, txt, json)")
    p_convert.add_argument("--input", "-i", required=True, help="Path to source document")
    p_convert.add_argument("--to", "-t", default="md", choices=["md", "txt", "json"], help="Target format")
    p_convert.add_argument("--output", "-o", default=None, help="Optional output file path")

    # Verify Email
    p_email = subparsers.add_parser("verify-email", help="Verify recruiter email deliverability & MX health")
    p_email.add_argument("email", help="Recruiter email address to verify")
    p_email.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # MCP Serve
    subparsers.add_parser("mcp-serve", help="Run as Model Context Protocol (MCP) server over stdio")

    args = parser.parse_args()
    if args.command == "match":
        cmd_match(args)
    elif args.command == "resume":
        if args.resume_command == "audit":
            cmd_resume_audit(args)
        elif args.resume_command == "build":
            cmd_resume_build(args)
        elif args.resume_command == "convert":
            cmd_resume_convert(args)
        else:
            p_resume.print_help()
    elif args.command == "verify-email":
        cmd_verify_email(args)
    elif args.command == "mcp-serve":
        cmd_mcp_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
