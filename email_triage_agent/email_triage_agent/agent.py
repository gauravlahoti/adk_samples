"""
Smart Email Triage Agent - Main Agent Definition

An intelligent email triage agent that acts as an automated first-pass
triage layer for business inboxes. Classifies, prioritizes, and routes
emails with consistent, instant judgment.

Built with Google Agent Development Kit (ADK) and powered by Gemini.
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold

from email_triage_agent.prompts import AGENT_INSTRUCTION
from email_triage_agent.tools import detect_email_signals, route_to_department

# Load environment variables
load_dotenv()

# Configuration from environment
gemini_model = os.environ.get("MODEL", "gemini-2.5-flash")

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
