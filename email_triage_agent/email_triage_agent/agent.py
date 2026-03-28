"""
Smart Email Triage Agent - Main Agent Definition

An intelligent email triage agent that acts as an automated first-pass
triage layer for business inboxes. Classifies, prioritizes, and routes
emails with consistent, instant judgment.

Built with Google Agent Development Kit (ADK) and powered by Gemini.
"""

import os
import json
import logging
import google.cloud.logging
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from typing import Optional

# --- Setup Cloud Logging ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

# --- Logging Constants (use these keywords for filtering) ---
LOG_PREFIX = "EMAIL_TRIAGE_AGENT"

logging.info(f"{LOG_PREFIX}:STARTUP - Email Triage Agent initializing...")
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold

from email_triage_agent.prompts import AGENT_INSTRUCTION
from email_triage_agent.tools import detect_email_signals, route_to_department

# Load environment variables
load_dotenv()

# Configuration from environment
gemini_model = os.environ.get("MODEL", "gemini-2.5-flash")
logging.info(f"{LOG_PREFIX}:CONFIG - model={gemini_model}")


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

# Create the root agent
root_agent = LlmAgent(
    model=gemini_model,
    name="smart_email_triage_agent",
    description="""
    Smart Email Triage Agent - An intelligent first-pass triage layer for business inboxes.
    
    Capabilities:
    - Classifies emails: Support, Sales, Spam, Internal, Feedback, Other
    - Scores priority: High, Medium, Low
    - Analyzes sentiment: Positive, Neutral, Negative, Urgent
    - Detects escalation risk for immediate human attention
    - Provides suggested actions and concise summaries
    
    Returns structured TriageResult for emails with: priority, category, sentiment, suggested_action, summary, escalate.
    Handles greetings and questions conversationally.
    """,
    instruction=AGENT_INSTRUCTION,
    tools=[detect_email_signals, route_to_department],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    generate_content_config=GenerateContentConfig(
        temperature=0.2,  # Lower temperature for consistent, reliable triage
        top_k=20,
        top_p=0.9,
        max_output_tokens=2000,
        safety_settings=[
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
        ]
    )
)
