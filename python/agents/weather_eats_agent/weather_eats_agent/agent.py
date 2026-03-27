import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams, StdioConnectionParams
from mcp import StdioServerParameters
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold
from weather_eats_agent.prompts import AGENT_INSTRUCTION

load_dotenv()

google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
gemini_model = os.environ.get("MODEL")
maps_mcp_url = os.environ.get("MAPS_MCP_URL")
resend_api_key = os.environ.get("RESEND_API_KEY")
sender_email = os.environ.get("SENDER_EMAIL_ADDRESS", "onboarding@resend.dev")

maps_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=maps_mcp_url,
        headers={
            "X-Goog-Api-Key": google_maps_api_key
        }
    ),
 tool_filter=['lookup_weather','search_places']
)

resend_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="/usr/local/bin/npx",
            args=["-y", "resend-mcp"],
            env={
                **os.environ,
                "RESEND_API_KEY": resend_api_key or "",
                "SENDER_EMAIL_ADDRESS": os.environ.get("SENDER_EMAIL_ADDRESS", ""),
            }
        )
    ),
    tool_filter=['send-email']
)

root_agent = LlmAgent(
    model=gemini_model,
    name='weather_eats_agent',
    description='Recommends restaurants based on live weather and location with context-aware dining suggestions.',
    instruction=AGENT_INSTRUCTION.format(sender_email=sender_email),
    tools=[maps_toolset, resend_toolset],
    generate_content_config=GenerateContentConfig(
        temperature=0.3,
        top_k=20,
        top_p=0.9,
        max_output_tokens=2000,
        safety_settings=[
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
        ]
    )
)
