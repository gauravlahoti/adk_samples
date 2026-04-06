"""
Customer Service Multi-Agent System
A coordinator routes requests to billing and technical specialists.
Reference: https://google.github.io/adk-docs/agents/multi-agents
"""
from google.adk.agents import LlmAgent
# Specialist 1: Billing
billing_agent = LlmAgent(
model='gemini-2.5-flash',
name='billing_specialist',
description='Handles billing and payment questions',
instruction="""
You are a billing specialist.
Help customers with:
- Payment processing
- Refunds
- Billing inquiries
- Invoice questions
Be clear about policies and timelines.
"""
)
# Specialist 2: Technical Support
technical_agent = LlmAgent(
model='gemini-2.5-flash',
name='technical_specialist',
description='Handles technical issues and troubleshooting',
instruction="""
You are a technical support specialist.
Help customers with:
- Login problems
- App crashes
- Feature troubleshooting
- Configuration help
Ask clarifying questions to diagnose issues.
"""
)
# Coordinator
root_agent = LlmAgent(
model='gemini-2.5-flash',
name='customer_service_coordinator',
description='Routes customer requests to specialists',
instruction="""
You are a customer service coordinator.
Route requests to the right specialist:
- Billing/payment issues → billing_specialist
- Technical problems → technical_specialist
- Simple general questions → answer directly
Be friendly and helpful.
""",
sub_agents=[billing_agent, technical_agent]
)