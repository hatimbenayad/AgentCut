"""
AgentCut MCP Server CLI Entrypoint
Supports stdio transport (Claude Desktop / CLI) and SSE transport (FastAPI HTTP).
Usage:
  python -m agentcut.mcp.cli --transport stdio
  python -m agentcut.mcp.cli --transport sse --port 8000
"""

import argparse
import sys
import asyncio
from agentcut.mcp.server import create_mcp_server

def main():
    parser = argparse.ArgumentParser(description="AgentCut Model Context Protocol (MCP) Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport mechanism")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for SSE transport")
    parser.add_argument("--db", type=str, default="./agentcut.db", help="Path to project SQLite database")
    args = parser.parse_args()

    server = create_mcp_server(db_path=args.db)

    if args.transport == "stdio":
        print(f"Starting AgentCut MCP Server on stdio transport...", file=sys.stderr)
        server.run(transport="stdio")
    elif args.transport == "sse":
        print(f"Starting AgentCut MCP Server on SSE transport at http://{args.host}:{args.port}/sse...", file=sys.stderr)
        server.run(transport="sse")

if __name__ == "__main__":
    main()

