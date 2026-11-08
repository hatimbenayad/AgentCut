"""
AgentCut MCP: Model Context Protocol Server Package
Spec reference: docs/specs/mcp-server/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-010)
"""

from agentcut.mcp.server import create_mcp_server

__all__ = ["create_mcp_server"]

