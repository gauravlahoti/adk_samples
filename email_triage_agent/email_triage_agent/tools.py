"""
Custom tools for the Smart Email Triage Agent.

Provides tools for escalation detection and department routing
to help the LLM make informed triage decisions.
"""

import json
import logging
from pydantic import BaseModel, Field

# --- Logging Constants (use these keywords for filtering in Cloud Logging) ---
# Filter queries:
#   EMAIL_TRIAGE_AGENT:TOOL_CALL     - All tool invocations
#   EMAIL_TRIAGE_AGENT:TOOL_RESULT   - All tool outputs
#   EMAIL_TRIAGE_AGENT:ESCALATION    - Escalation events only
#   EMAIL_TRIAGE_AGENT:ROUTING       - Routing decisions only
LOG_PREFIX = "EMAIL_TRIAGE_AGENT"


class TriageResult(BaseModel):
    """Structured output schema for the Email Triage Agent."""

    priority: str = Field(description="Urgency level: High, Medium, or Low.")
    category: str = Field(description="Email type: Support, Sales, Spam, Internal, Feedback, or Other.")
    sentiment: str = Field(description="Emotional tone: Positive, Neutral, Negative, or Urgent.")
    suggested_action: str = Field(description="One clear action to take, max 15 words.")
    summary: str = Field(description="1-2 sentence plain-English summary of the email.")
    escalate: bool = Field(description="True if this email requires immediate human escalation.")


ESCALATION_TRIGGERS = [
    "lawsuit", "legal action", "attorney", "sue", "court", "fraud",
    "unacceptable", "furious", "threatening", "chargeback", "data breach",
]
 
ROUTING_MAP = {
    "refund": "Billing Team",
    "invoice": "Billing Team",
    "payment": "Billing Team",
    "bug": "Engineering Team",
    "crash": "Engineering Team",
    "error": "Engineering Team",
    "pricing": "Sales Team",
    "demo": "Sales Team",
    "cancel": "Retention Team",
    "complaint": "Customer Success",
    "partnership": "Business Development",
}


def detect_email_signals(email_text: str) -> dict:
    """
    Scans the email for signals that inform triage decisions, including
    legal threats, urgency indicators, and expressions of dissatisfaction.

    When to use: Call this tool first on every email to detect important signals.

    Args:
        email_text: The raw email body text.

    Returns:
        A dict with:
            - status: 'success' or 'error'
            - escalate: bool indicating if escalation is needed
            - matched_triggers: list of matched trigger words
    """
    # Log tool invocation with input
    logging.info(f"{LOG_PREFIX}:TOOL_CALL - tool=detect_email_signals | input_length={len(email_text) if email_text else 0}")
    logging.info(f"{LOG_PREFIX}:TOOL_INPUT - tool=detect_email_signals | email_preview={email_text[:200] if email_text else 'empty'}...")
    
    if not email_text or not email_text.strip():
        result = {
            "status": "error",
            "escalate": False,
            "matched_triggers": [],
            "error_message": "Empty email text provided"
        }
        logging.warning(f"{LOG_PREFIX}:TOOL_RESULT - tool=detect_email_signals | status=error | reason=empty_input")
        return result
    
    lower = email_text.lower()
    matched = [t for t in ESCALATION_TRIGGERS if t in lower]
    
    result = {
        "status": "success",
        "escalate": len(matched) > 0,
        "matched_triggers": matched,
    }
    
    # Log tool result
    logging.info(f"{LOG_PREFIX}:TOOL_RESULT - tool=detect_email_signals | result={json.dumps(result)}")
    
    # Special escalation log for easy filtering
    if matched:
        logging.warning(f"{LOG_PREFIX}:ESCALATION - triggers_found={matched} | requires_immediate_attention=true")
    
    return result


def route_to_department(email_text: str) -> dict:
    """
    Identifies the most appropriate internal department to handle this email
    based on keyword matching.

    When to use: Call after check_escalation to determine which team should handle the email.

    Args:
        email_text: The raw email body text.

    Returns:
        A dict with:
            - status: 'success' or 'error'
            - department: the team name to route to
            - matched_keyword: the keyword that triggered the routing (or None)
    """
    # Log tool invocation with input
    logging.info(f"{LOG_PREFIX}:TOOL_CALL - tool=route_to_department | input_length={len(email_text) if email_text else 0}")
    logging.info(f"{LOG_PREFIX}:TOOL_INPUT - tool=route_to_department | email_preview={email_text[:200] if email_text else 'empty'}...")
    
    if not email_text or not email_text.strip():
        result = {
            "status": "error",
            "department": "General Support",
            "matched_keyword": None,
            "error_message": "Empty email text provided"
        }
        logging.warning(f"{LOG_PREFIX}:TOOL_RESULT - tool=route_to_department | status=error | reason=empty_input")
        return result
    
    lower = email_text.lower()
    for keyword, department in ROUTING_MAP.items():
        if keyword in lower:
            result = {
                "status": "success",
                "department": department,
                "matched_keyword": keyword
            }
            # Log tool result and routing decision
            logging.info(f"{LOG_PREFIX}:TOOL_RESULT - tool=route_to_department | result={json.dumps(result)}")
            logging.info(f"{LOG_PREFIX}:ROUTING - department={department} | matched_keyword={keyword}")
            return result
    
    # Default routing when no keywords match
    result = {
        "status": "success",
        "department": "General Support",
        "matched_keyword": None
    }
    logging.info(f"{LOG_PREFIX}:TOOL_RESULT - tool=route_to_department | result={json.dumps(result)}")
    logging.info(f"{LOG_PREFIX}:ROUTING - department=General Support | matched_keyword=none | reason=no_keyword_match")
    return result


# Export tools list
TRIAGE_TOOLS = [detect_email_signals, route_to_department]
