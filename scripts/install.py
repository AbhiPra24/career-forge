#!/usr/bin/env python3
"""
CareerForge Automated Installer & Agent Integrator
Installs CLI binaries, registers MCP servers, and deploys skills globally and locally.
"""

import os
import sys
import json
import shutil
import stat
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
SKILLS_DIR = REPO_ROOT / "skills"
HOME = Path.home()

# Target Paths
LOCAL_BIN = HOME / ".local" / "bin"
GEMINI_CONFIG_DIR = HOME / ".gemini" / "config"
GLOBAL_SKILLS_DIR = GEMINI_CONFIG_DIR / "skills"
GLOBAL_MCP_CONFIG = GEMINI_CONFIG_DIR / "mcp_config.json"
WORKSPACE_AGENTS_SKILLS = REPO_ROOT / ".agents" / "skills"


def install_cli():
    """Installs cforge and career-forge standalone wrapper scripts into ~/.local/bin."""
    LOCAL_BIN.mkdir(parents=True, exist_ok=True)
    
    wrapper_content = f"""#!/usr/bin/env bash
export PYTHONPATH="{SRC_DIR}:${{PYTHONPATH}}"
exec python3 -m career_forge.cli "$@"
"""
    for binary_name in ("cforge", "career-forge"):
        target_path = LOCAL_BIN / binary_name
        target_path.write_text(wrapper_content, encoding="utf-8")
        target_path.chmod(target_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  ✔ Installed CLI launcher: {target_path}")


def install_skills(dest_dir: Path, label: str):
    """Copies skills from skills/ into target directory."""
    if not SKILLS_DIR.exists():
        print(f"  ⚠ Skills directory not found: {SKILLS_DIR}")
        return

    dest_dir.mkdir(parents=True, exist_ok=True)
    for skill_folder in SKILLS_DIR.iterdir():
        if skill_folder.is_dir():
            target_folder = dest_dir / skill_folder.name
            target_folder.mkdir(parents=True, exist_ok=True)
            for item in skill_folder.glob("*"):
                if item.is_file():
                    shutil.copy2(item, target_folder / item.name)
            print(f"  ✔ Installed skill ({label}): {skill_folder.name} -> {target_folder}")


def register_mcp():
    """Registers career-forge in ~/.gemini/config/mcp_config.json."""
    if not GEMINI_CONFIG_DIR.exists():
        GEMINI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config_data = {"mcpServers": {}}
    if GLOBAL_MCP_CONFIG.exists():
        try:
            with open(GLOBAL_MCP_CONFIG, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"  ⚠ Failed to parse existing {GLOBAL_MCP_CONFIG}, creating clean config: {e}")

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    config_data["mcpServers"]["career-forge"] = {
        "command": "python3",
        "args": ["-m", "career_forge.mcp_server"],
        "env": {
            "PYTHONPATH": str(SRC_DIR),
            "PYTHONWARNINGS": "ignore"
        }
    }

    with open(GLOBAL_MCP_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    print(f"  ✔ Registered MCP Server in {GLOBAL_MCP_CONFIG}")


def uninstall():
    """Removes installed binaries, skills, and MCP registration."""
    for binary_name in ("cforge", "career-forge"):
        p = LOCAL_BIN / binary_name
        if p.exists():
            p.unlink()
            print(f"  ✔ Removed binary: {p}")

    for skill_name in ("talent-scout", "resume-architect", "recruiter-radar"):
        g_skill = GLOBAL_SKILLS_DIR / skill_name
        if g_skill.exists():
            shutil.rmtree(g_skill)
            print(f"  ✔ Removed global skill: {g_skill}")

    if GLOBAL_MCP_CONFIG.exists():
        try:
            with open(GLOBAL_MCP_CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "mcpServers" in data and "career-forge" in data["mcpServers"]:
                del data["mcpServers"]["career-forge"]
                with open(GLOBAL_MCP_CONFIG, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"  ✔ Unregistered MCP server from {GLOBAL_MCP_CONFIG}")
        except Exception as e:
            print(f"  ⚠ Error cleaning MCP config: {e}")


def main():
    parser = argparse.ArgumentParser(description="CareerForge Installer")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall all components")
    parser.add_argument("--cli-only", action="store_true", help="Install only CLI binaries")
    parser.add_argument("--skills-only", action="store_true", help="Install only agent skills")
    parser.add_argument("--mcp-only", action="store_true", help="Register only MCP server")
    args = parser.parse_args()

    if args.uninstall:
        print("\n🗑️  Uninstalling CareerForge components...")
        uninstall()
        print("✔ Uninstallation complete.\n")
        return

    print("\n⚡ Installing CareerForge...")

    if args.cli_only:
        install_cli()
    elif args.skills_only:
        install_skills(GLOBAL_SKILLS_DIR, "Global")
        install_skills(WORKSPACE_AGENTS_SKILLS, "Local Workspace")
    elif args.mcp_only:
        register_mcp()
    else:
        # Full install
        install_cli()
        install_skills(GLOBAL_SKILLS_DIR, "Global")
        install_skills(WORKSPACE_AGENTS_SKILLS, "Local Workspace")
        register_mcp()

    print("\n🎉 CareerForge installation complete!")
    print("  • Try CLI: cforge --help")
    print("  • Skills ready in: ~/.gemini/config/skills/ and .agents/skills/")
    print("  • MCP server ready in: ~/.gemini/config/mcp_config.json\n")


if __name__ == "__main__":
    main()
