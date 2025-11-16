"""
Router Agent - Fast Severity Classification  
============================================

The RouterAgent is the first agent in the pipeline. It uses Claude Haiku
(the fastest, most cost-effective model) to quickly classify call severity
and determine which downstream agent should handle the call.

Cost-Optimization Strategy:
- Uses Haiku for all initial classifications
- Only routes to expensive Sonnet for CRITICAL calls
- Routes standard/non-emergency to Llama for cost savings
"""

import sys
from pathlib import Path
import json
import re

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from langchain_core.messages import SystemMessage, HumanMessage
from holistic_ai_bedrock import get_chat_model
from schemas import CallClassification
from config import config


class RouterAgent:
    """
    Fast severity classification agent using Claude Haiku.
    """
    
    def __init__(self):
        """Initialize the RouterAgent with Claude Haiku."""
        self.llm = self._create_llm()
    
    def _create_llm(self):
        """Create LLM using official Holistic AI helper."""
        # Amazon Nova Lite - ultra-fast for real-time routing
        return get_chat_model(
            "claude-3-5-haiku",
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=300    # Short outputs for routing decisions (reduced for speed)
        )
    
    def classify(self, transcript: str) -> CallClassification:
        """
        Classify a call transcript for severity and routing.
        
        Args:
            transcript: The emergency call transcript
        
        Returns:
            CallClassification with severity and routing decision
        """
        
        system_prompt = """You are an expert 911 call router. Your job is to QUICKLY and ACCURATELY classify the severity of emergency calls.

IMPORTANT: You will receive the FULL CONVERSATION between dispatcher and caller. Review the ENTIRE conversation to understand the context. Do NOT ignore earlier messages.

SEVERITY LEVELS:

1. CRITICAL_EMERGENCY (Route to TRIAGE_AGENT)
   - Active violence (shootings, stabbings, assaults in progress)
   - Life-threatening medical emergencies
   - Major fires with people trapped
   - Active threats to public safety
   - ANY situation requiring immediate tactical response

2. STANDARD_ASSISTANCE (Route to INFO_AGENT)
   - Medical emergencies without immediate life threat
   - Property crimes without active danger
   - Accidents with minor injuries
   - Situations requiring police/fire but not SWAT/tactical

3. NON_EMERGENCY (Route to INFO_AGENT)
   - Information requests
   - Noise complaints
   - Found property
   - Non-urgent issues

KEY DECISION FACTORS:
- Is there an ACTIVE threat to life?
- Are weapons involved?
- Is the situation ONGOING or already resolved?
- How many people are at risk?

CRITICAL: Base your classification on the ENTIRE conversation, not just the last message. If the caller mentioned a fire in the first message, it's still a fire even if they're now providing their address."""

        human_prompt = f"""Analyze this 911 call conversation and classify its severity.

IMPORTANT: Below is the FULL conversation. Review ALL messages to understand the complete situation.

RETURN ONLY VALID JSON IN THIS EXACT FORMAT:
{{
  "severity": "CRITICAL_EMERGENCY or STANDARD_ASSISTANCE or NON_EMERGENCY",
  "confidence": 0.95,
  "reasoning": "Brief explanation based on full conversation",
  "route_to": "TRIAGE_AGENT or INFO_AGENT"
}}

FULL CONVERSATION:
{transcript}

Return ONLY the JSON, no markdown or explanation."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    raise ValueError(f"No JSON in response: {response_text[:200]}")
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Create CallClassification from parsed data
            return CallClassification(
                severity=data.get("severity", "STANDARD_ASSISTANCE"),
                confidence=float(data.get("confidence", 0.5)),
                reasoning=data.get("reasoning", "No reasoning provided"),
                route_to=data.get("route_to", "INFO_AGENT")
            )
        except Exception as e:
            # Fallback classification on error
            print(f"   ⚠️  Router parsing error: {e}, using fallback")
            return CallClassification(
                severity="STANDARD_ASSISTANCE",
                confidence=0.5,
                reasoning=f"Error in classification: {str(e)}",
                route_to="INFO_AGENT"
            )


# Singleton instance
_router_agent = None


def get_router_agent() -> RouterAgent:
    """Get or create singleton RouterAgent instance."""
    global _router_agent
    if _router_agent is None:
        _router_agent = RouterAgent()
    return _router_agent


if __name__ == "__main__":
    """Test the RouterAgent"""
    print("Testing RouterAgent...")
    
    test_transcript = """
    Dispatcher: 9-1-1, what's your emergency?
    Caller: I'm at West High School. There's a guy with a gun.
    Dispatcher: Which high school?
    Caller: West High.
    """
    
    agent = get_router_agent()
    result = agent.classify(test_transcript)
    print(f"\nResult: {result}")
