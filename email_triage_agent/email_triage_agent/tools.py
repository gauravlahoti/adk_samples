"""
Custom tools for the Smart Email Triage Agent.

Provides tools for escalation detection and department routing
to help the LLM make informed triage decisions.
"""

from pydantic import BaseModel, Field


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


def check_escalation(email_text: str) -> dict:
    """
    Scans the email for language that signals immediate human escalation is needed,
    such as legal threats or expressions of extreme dissatisfaction.

    When to use: Call this tool first on every email to detect urgent escalation triggers.

    Args:
        email_text: The raw email body text.

    Returns:
        A dict with:
            - status: 'success' or 'error'
            - escalate: bool indicating if escalation is needed
            - matched_triggers: list of matched trigger words
    """
    if not email_text or not email_text.strip():
        return {
            "status": "error",
            "escalate": False,
            "matched_triggers": [],
            "error_message": "Empty email text provided"
        }
    
    lower = email_text.lower()
    matched = [t for t in ESCALATION_TRIGGERS if t in lower]
    return {
        "status": "success",
        "escalate": len(matched) > 0,
        "matched_triggers": matched,
    }


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
    if not email_text or not email_text.strip():
        return {
            "status": "error",
            "department": "General Support",
            "matched_keyword": None,
            "error_message": "Empty email text provided"
        }
    
    lower = email_text.lower()
    for keyword, department in ROUTING_MAP.items():
        if keyword in lower:
            return {
                "status": "success",
                "department": department,
                "matched_keyword": keyword
            }
    return {
        "status": "success",
        "department": "General Support",
        "matched_keyword": None
    }


# Export tools list
TRIAGE_TOOLS = [check_escalation, route_to_department]
