"""
Info Agent - Non-Critical Call Handler
=======================================

The InfoAgent handles STANDARD_ASSISTANCE and NON_EMERGENCY calls.
It uses Llama (cost-effective open source model) to provide basic
information gathering and recommendations.

Cost-Optimization Strategy:
- Uses Llama instead of expensive Claude models
- Simpler analysis for non-critical situations
- Still provides structured, useful output
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
from schemas import InfoAgentResponse, LocationInfo
from config import config
from tools import extract_location_from_transcript, validate_location


class InfoAgent:
    """
    Basic information gathering agent using Llama.
    """
    
    def __init__(self):
        """Initialize the InfoAgent with Llama."""
        self.llm = self._create_llm()
    
    def _create_llm(self):
        """Create LLM using official helper."""
        # Claude 3.5 Haiku - fast responses for real-time voice calls
        return get_chat_model(
            "claude-3-5-haiku",
            temperature=0.5,
            max_tokens=800
        )
    
    def process_call(self, transcript: str, severity: str) -> InfoAgentResponse:
        """
        Process a non-critical emergency call.
        
        Args:
            transcript: The call transcript
            severity: Severity level (STANDARD_ASSISTANCE or NON_EMERGENCY)
        
        Returns:
            InfoAgentResponse with call summary and recommendations
        """
        
        # Extract location if available
        location_text = extract_location_from_transcript(transcript)
        location = None
        
        if location_text:
            # Use .invoke() since validate_location is a StructuredTool
            location_dict = validate_location.invoke({"location_text": location_text})
            location = LocationInfo(**location_dict)
        
        system_prompt = """You are a professional 911 dispatcher handling a non-critical emergency call.

IMPORTANT: You are having a LIVE VOICE CONVERSATION. You will see the FULL conversation history.

CRITICAL RULES FOR 911 DISPATCHERS:
1. NEVER hang up on a caller - they must end the call
2. REVIEW the full conversation to see what you already know
3. ONLY ask for information you DON'T already have
4. Once you have enough info, tell them units are dispatched and ask if they want to stay on the line
5. Be calm, professional, and reassuring
6. Sound natural and conversational (this is a VOICE CALL)
7. NEVER say "goodbye", "take care", or similar ending phrases
8. ALWAYS end your response with a QUESTION to continue the conversation
9. After dispatching, ask follow-up questions: "Are you safe?", "Is anyone hurt?", "Can you describe the situation?"

911 PROTOCOL:
- If caller says they're "safe" or "okay", acknowledge it but ask a follow-up question
- After dispatching, say: "I'm dispatching [unit type] now. I'm staying on the line. Are you in a safe location right now?"
- Keep responses concise (2-3 sentences)
- Continue engaging the caller to monitor situation
- Every response must END WITH A QUESTION

Don't repeat questions already answered in the conversation history."""

        human_prompt = f"""You are speaking with someone who called 911. Review the FULL conversation and provide your next response.

IMPORTANT: Below is the COMPLETE conversation history. Review ALL previous exchanges to understand what you already know.

RETURN ONLY VALID JSON IN THIS EXACT FORMAT:
{{
  "call_type": "Medical - Non-Life-Threatening or Property Crime or Traffic Accident or Public Service or Other",
  "summary": "Clear summary based on the full conversation",
  "recommended_action": "Specific recommendation",
  "additional_info": ["detail1", "detail2"],
  "requires_followup": true,
  "response": "Natural conversational response (2-3 sentences, building on what they already told you). NEVER say 'goodbye' or end call. ALWAYS end with a QUESTION to keep conversation active (e.g., 'Are you in a safe location?' or 'Is anyone with you?')",
  "address": "Full street address if mentioned (e.g., '3 Davis Street, London')",
  "postcode": "Postcode if mentioned (e.g., 'E13 9EE')",
  "caller_emotion": "CALM or CONCERNED or ANXIOUS or PANICKED or ANGRY",
  "emotion_intensity": "LOW or MEDIUM or HIGH"
}}

SEVERITY: {severity}

FULL CONVERSATION:
{transcript}

Remember: Your 'response' will be spoken aloud. Review what they've told you and ask for the NEXT piece of info you need. Don't repeat yourself.

Return ONLY JSON, no markdown or explanation."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Extract JSON
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
            
            # Update location with address and postcode from LLM if provided
            address = data.get("address")
            postcode = data.get("postcode")
            if location and (address or postcode):
                if address:
                    location.address = address
                    location.verified = True
                if postcode and "landmark" in str(location.landmark).lower():
                    # Replace bad landmark with None
                    location.landmark = None
            elif address or postcode:
                # Create location if we got address/postcode but didn't extract earlier
                location = LocationInfo(
                    address=address,
                    verified=True if address else False,
                    landmark=None
                )
            
            # Build InfoAgentResponse
            result = InfoAgentResponse(
                call_type=data.get("call_type", "Other"),
                summary=data.get("summary", "Call processed"),
                recommended_action=data.get("recommended_action", "Standard response"),
                additional_info=data.get("additional_info", []),
                requires_followup=bool(data.get("requires_followup", False)),
                location=location,
                response=data.get("response", "I understand. Can you please provide more details?"),
                address=address,
                postcode=postcode,
                caller_emotion=data.get("caller_emotion", "CALM"),
                emotion_intensity=data.get("emotion_intensity", "LOW")
            )
            
            return result
            
        except Exception as e:
            print(f"   ⚠️  Info agent parsing error: {e}, using fallback")
            # Return fallback response
            return InfoAgentResponse(
                call_type="Other",
                summary=f"Error processing call: {str(e)}",
                recommended_action="Manual review required",
                additional_info=[f"System error: {str(e)}"],
                requires_followup=True,
                location=location
            )


# Singleton instance
_info_agent = None


def get_info_agent() -> InfoAgent:
    """Get or create singleton InfoAgent instance."""
    global _info_agent
    if _info_agent is None:
        _info_agent = InfoAgent()
    return _info_agent


if __name__ == "__main__":
    """Test the InfoAgent"""
    print("Testing InfoAgent...")
    
    test_transcript = """
    Dispatcher: 9-1-1, what's your emergency?
    Caller: Hi, I need to report a noise complaint at 123 Main Street.
    Dispatcher: What kind of noise?
    Caller: Loud music from the neighbors.
    """
    
    agent = get_info_agent()
    result = agent.process_call(test_transcript, "NON_EMERGENCY")
    print(f"\nResult: {result}")
