"""
Emergentica Agents Package
==========================

This package contains all the specialized AI agents:
- RouterAgent: Fast severity classification (Haiku)
- TriageAgent: Critical incident analysis (Sonnet)
- InfoAgent: Non-critical call handling (Llama)
"""

from agents.router_agent import RouterAgent, get_router_agent
from agents.triage_agent import TriageAgent, get_triage_agent
from agents.info_agent import InfoAgent, get_info_agent

__all__ = [
    'RouterAgent',
    'TriageAgent',
    'InfoAgent',
    'get_router_agent',
    'get_triage_agent',
    'get_info_agent',
]
