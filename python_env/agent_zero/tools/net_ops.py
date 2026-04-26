# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import httpx
import socket
from .registry import tool_link

@tool_link
def web_get(url: str):
    """Performs an HTTP GET request and returns the status and a snippet of content."""
    try:
        with httpx.Client() as client:
            response = client.get(url)
            return {
                "status_code": response.status_code,
                "snippet": response.text[:500] + "..." if len(response.text) > 500 else response.text
            }
    except Exception as e:
        return f"Error connecting to {url}: {str(e)}"

@tool_link
def resolve_dns(hostname: str):
    """Resolves a hostname to an IP address."""
    try:
        return socket.gethostbyname(hostname)
    except Exception as e:
        return f"Error resolving {hostname}: {str(e)}"
