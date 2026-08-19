"""
Unit tests for CareerForge Model Context Protocol (MCP) Server
"""

import json
import unittest
from pathlib import Path

from career_forge.mcp_server import process_jsonrpc_message, handle_tool_call

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "synthetic_resumes"


class TestMCPServer(unittest.TestCase):
    def test_mcp_initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        res = process_jsonrpc_message(req)
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["result"]["serverInfo"]["name"], "career-forge")

    def test_mcp_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        res = process_jsonrpc_message(req)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("talent_scout_match", tool_names)
        self.assertIn("resume_architect_audit", tool_names)
        self.assertIn("resume_architect_build", tool_names)
        self.assertIn("recruiter_radar_verify", tool_names)

    def test_mcp_tool_call_match(self):
        resume_path = str(FIXTURES_DIR / "alex_rivera_backend.md")
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "talent_scout_match",
                "arguments": {
                    "resume_path": resume_path,
                    "query": "Distributed Systems",
                    "limit": 5
                }
            }
        }
        res = process_jsonrpc_message(req)
        self.assertEqual(res["id"], 3)
        content_text = res["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertEqual(payload["candidate_digest"]["candidate_name"], "Alex Rivera")
        self.assertGreaterEqual(payload["requisitions_evaluated_count"], 5)

    def test_mcp_tool_call_verify_email(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "recruiter_radar_verify",
                "arguments": {
                    "email": "lead.recruiter@github.com"
                }
            }
        }
        res = process_jsonrpc_message(req)
        self.assertEqual(res["id"], 4)
        content_text = res["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertTrue(payload["is_valid_syntax"])


if __name__ == "__main__":
    unittest.main()
