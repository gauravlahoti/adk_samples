import os
import logging
import google.cloud.logging
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from typing import Optional
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold
from weather_eats_agent.prompts import AGENT_INSTRUCTION

# --- Setup Cloud Logging ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# --- Logging Constants (use these keywords for filtering in Cloud Logging) ---
# Filter queries:
#   WEATHER_EATS_AGENT:STARTUP     - Agent initialization
#   WEATHER_EATS_AGENT:CONFIG      - Configuration details
#   WEATHER_EATS_AGENT:INPUT       - User prompts
#   WEATHER_EATS_AGENT:OUTPUT      - Agent responses
#   WEATHER_EATS_AGENT:SUMMARY     - Request/response summary
#   WEATHER_EATS_AGENT:TOOL_CALL   - MCP tool invocations
LOG_PREFIX = "WEATHER_EATS_AGENT"

logging.info(f"{LOG_PREFIX}:STARTUP - Weather Eats Agent initializing...")

load_dotenv()

google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
gemini_model = os.environ.get("MODEL")
maps_mcp_url = os.environ.get("MAPS_MCP_URL")
resend_api_key = os.environ.get("RESEND_API_KEY")
resend_mcp_url = os.environ.get("RESEND_MCP_URL")
sender_email = os.environ.get("SENDER_EMAIL_ADDRESS", "onboarding@resend.dev")

logging.info(f"{LOG_PREFIX}:CONFIG - model={gemini_model} | maps_mcp_url={maps_mcp_url} | resend_mcp_url={resend_mcp_url}")


# --- Agent Callbacks for Input/Output Logging ---

def before_agent_callback(callback_context: CallbackContext) -> Optional[dict]:
    """
    Called before the agent processes a request.
    Logs the user's input prompt.
    """
    user_message = callback_context.user_content
    session_id = callback_context.state.get("session_id", "unknown")
    
    # Extract text from user content
    if hasattr(user_message, 'parts'):
        prompt_text = " ".join([p.text for p in user_message.parts if hasattr(p, 'text')])
    else:
        prompt_text = str(user_message)
    
    logging.info(f"{LOG_PREFIX}:INPUT - session={session_id} | prompt={prompt_text[:500]}")
    
    # Store in state for correlation
    callback_context.state["current_prompt"] = prompt_text
    
    return None  # Continue with normal processing


def after_agent_callback(callback_context: CallbackContext) -> Optional[LlmResponse]:
    """
    Called after the agent generates a response.
    Logs the final agent response.
    """
    session_id = callback_context.state.get("session_id", "unknown")
    prompt = callback_context.state.get("current_prompt", "unknown")
    
    # Get the agent's response from the context
    if hasattr(callback_context, 'agent_response') and callback_context.agent_response:
        response_text = str(callback_context.agent_response)
    else:
        response_text = "(response captured in event stream)"
    
    logging.info(f"{LOG_PREFIX}:OUTPUT - session={session_id} | response={response_text[:500]}")
    
    # Log summary for easy correlation
    logging.info(f"{LOG_PREFIX}:SUMMARY - session={session_id} | input_length={len(prompt)} | output_length={len(response_text)}")
    
    return None  # Continue with normal response

# Google Maps MCP (HTTP transport) - provides weather lookup and places search
maps_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=maps_mcp_url,  
        headers={
            "X-Goog-Api-Key": google_maps_api_key  
        }
    ),
    tool_filter=['lookup_weather', 'search_places']  # Only expose these tools to the agent
)

# Resend MCP (HTTP transport) - provides email sending capability
resend_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=resend_mcp_url,
        headers={
            "Authorization": f"Bearer {resend_api_key}"
        }
    ),
    tool_filter=['send-email']
)

logging.info(f"{LOG_PREFIX}:CONFIG - Using Resend MCP via HTTP: {resend_mcp_url}")

root_agent = LlmAgent(
    model=gemini_model,
    name='weather_eats_agent',
    description='Recommends restaurants based on live weather and location with context-aware dining suggestions.',
    instruction=AGENT_INSTRUCTION.format(sender_email=sender_email),
    tools=[maps_toolset,resend_toolset],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
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
