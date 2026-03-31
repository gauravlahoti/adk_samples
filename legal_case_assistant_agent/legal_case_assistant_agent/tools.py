"""
Tool configuration for the Legal Case Assistant Agent.

Connects to MCP Toolbox for Databases to access the legal cases
database via the ToolboxToolset.
"""

import os
import logging
from dotenv import load_dotenv
from google.adk.tools.toolbox_toolset import ToolboxToolset

load_dotenv()

LOG_PREFIX = "LEGAL_CASE_AGENT"

TOOLBOX_URL = os.environ.get("TOOLBOX_URL")

if not TOOLBOX_URL:
    logging.error(f"{LOG_PREFIX}:CONFIG - TOOLBOX_URL environment variable is not set")
    raise ValueError("TOOLBOX_URL environment variable is required")

logging.info(f"{LOG_PREFIX}:CONFIG - Toolbox URL: {TOOLBOX_URL}")

# Connect to the MCP Toolbox for Databases server
# Uses the "legal-assistant" toolset which provides search-legal-cases tool
legal_toolset = ToolboxToolset(
    server_url=TOOLBOX_URL,
    toolset_name="legal-assistant",
)
