"""
Triage Agent - Critical Incident Analysis
==========================================

The TriageAgent handles CRITICAL_EMERGENCY calls. It uses Claude Sonnet
(most capable model) to perform deep analysis including:
- Emotion detection
- Detailed incident assessment
- Resource requirement calculation
- Actionable recommendations

Only invoked for critical calls to optimize costs while maintaining
high quality analysis where it matters most.
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
from schemas import (
    CriticalIncidentReport, 
    EmotionAnalysis, 
    LocationInfo, 
    IncidentDetails, 
    ResourceRequirements
)
from config import config
from tools import extract_location_from_transcript, validate_location
from datetime import datetime


class TriageAgent:
    """
    Deep analysis agent for critical emergencies using Claude Sonnet.
    """
    
    def __init__(self):
        """Initialize the TriageAgent with Claude Sonnet."""
        self.llm = self._create_llm()
        self.emotion_llm = self._create_emotion_llm()
    
    def _create_llm(self):
        """Create LLM for main analysis using official helper."""
        # Claude 3.5 Haiku - fast responses for real-time voice calls
        return get_chat_model(
            "claude-3-5-haiku",
            temperature=0.3,
            max_tokens=1500
        )
    
    def _create_emotion_llm(self):
        """Create emotion analysis LLM using Haiku for speed."""
        # Use Haiku for emotion analysis (sub-task)
        return get_chat_model(
            "claude-3-5-haiku",
            temperature=0.2,
            max_tokens=500
        )
    
    def analyze_critical_call(self, transcript: str, severity: str = "CRITICAL_EMERGENCY") -> CriticalIncidentReport:
        """
        Perform deep analysis of a critical emergency call.
        
        Args:
            transcript: The emergency call transcript
            severity: Severity level (default: CRITICAL_EMERGENCY)
        
        Returns:
            CriticalIncidentReport with detailed analysis
        """
        
        # Step 1: Emotion analysis
        emotion = self._analyze_emotion(transcript)
        
        # Step 2: Extract and enrich location
        location_text = extract_location_from_transcript(transcript)
        location = None
        
        if location_text:
            try:
                location_dict = validate_location.invoke({"location_text": location_text})
                location = LocationInfo(**location_dict)
            except Exception as e:
                print(f"   ⚠️  Location validation failed: {e}")
                location = LocationInfo(address=location_text, verified=False)
        else:
            location = LocationInfo(verified=False)
        
        # Step 3: Deep incident analysis
        system_prompt = """You are a professional 911 dispatcher handling a CRITICAL emergency.

IMPORTANT: You are having a LIVE VOICE CONVERSATION. You will see the FULL conversation history between you and the caller.

Your role:
1. REVIEW the full conversation to understand what you already know
2. ONLY ask for information you DON'T already have
3. Be calm, professional, and reassuring
4. DO NOT promise help is "on the way" until you have confirmed their location
5. Build on previous responses - this is an ongoing CONVERSATION
6. NEVER say goodbye, hang up, or end the call - ALWAYS stay on the line

CRITICAL RULES:
- If the emergency type is already mentioned, DON'T ask again
- If location was provided, DON'T ask again
- Ask ONE focused question at a time
- Keep responses SHORT (2-3 sentences for voice)
- NEVER end with "goodbye", "take care", or similar phrases
- ALWAYS end your response with a QUESTION to keep the conversation going
- After dispatching, ask follow-up questions: "Are you safe?", "Is anyone with you?", "What do you see?"

**CRITICAL: DETECT AND HANDLE USER CONFUSION**
- Continue engaging even after dispatching units

Your analysis must be:
1. RAPID - Lives are at stake
2. PRECISE - Every detail matters
3. ACTIONABLE - Provide clear next steps

Focus on:
- Threat assessment
- Resource requirements
- Tactical recommendations
- Public safety concerns"""

        human_prompt = f"""Analyze this CRITICAL emergency call conversation and provide structured analysis.

IMPORTANT: Below is the FULL CONVERSATION. Review ALL exchanges to understand the complete situation. Do NOT repeat questions already answered.

You are speaking to someone in a critical emergency situation. Your response will be spoken out loud to them.

RETURN ONLY VALID JSON IN THIS EXACT FORMAT:
{{
  "incident_type": "ACTIVE_SHOOTER or MEDICAL_CRITICAL or FIRE_MAJOR or VIOLENT_CRIME or OTHER_CRITICAL",
  "executive_summary": "Brief tactical summary for quick dispatcher review",
  "key_facts": ["fact1", "fact2", "fact3"],
  "recommended_actions": ["action1", "action2"],
  "dispatcher_message": "Natural, calm, reassuring response to speak to caller (2-3 sentences. NEVER say 'goodbye' or end call. ALWAYS end with a QUESTION to keep conversation going. If user seems confused about location question, give EXAMPLES like 'I need your street address, like 123 Main Street, or the building name. What can you see around you?' DO NOT repeat same question more than twice.)",
  "incident_details": {{
    "incident_type": "shooting",
    "threat_level": "ACTIVE or CONTAINED or RESOLVED or UNKNOWN (IMPORTANT: Use ONLY these exact values, NOT 'URGENT')",
    "injuries_reported": true,
    "injury_count": 2,
    "suspect_description": "Description if available",
    "weapons_involved": true,
    "bystanders_at_risk": true
  }},
  "resources": {{
    "police": true,
    "ambulance": true,
    "fire": false,
    "swat": false,
    "negotiator": false,
    "additional_units": 5,
    "priority": "IMMEDIATE or URGENT or STANDARD or LOW"
  }},
  "confidence_score": 0.95
}}

FULL CONVERSATION:
{transcript}

DETECTED EMOTION: {emotion.primary_emotion if emotion else 'Unknown'}

IMPORTANT FOR dispatcher_message:
- This will be read aloud to the caller
- Review what's already been discussed in the conversation
- If you DON'T have their location yet, ask for it calmly
- If you DO have their location, acknowledge help is coming
- If they told you the emergency already, don't ask again
- Be calm, professional, reassuring
- 2-3 sentences maximum

Return ONLY the JSON, no markdown or explanation."""

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
            
            # Build nested objects
            incident_details_data = data.get("incident_details", {})
            incident_details = IncidentDetails(
                incident_type=incident_details_data.get("incident_type", "unknown"),
                threat_level=incident_details_data.get("threat_level", "UNKNOWN"),
                injuries_reported=incident_details_data.get("injuries_reported", False),
                injury_count=incident_details_data.get("injury_count"),
                suspect_description=incident_details_data.get("suspect_description"),
                weapons_involved=incident_details_data.get("weapons_involved", False),
                bystanders_at_risk=incident_details_data.get("bystanders_at_risk", False)
            )
            
            resources_data = data.get("resources", {})
            resources = ResourceRequirements(
                police=resources_data.get("police", True),
                ambulance=resources_data.get("ambulance", False),
                fire=resources_data.get("fire", False),
                swat=resources_data.get("swat", False),
                negotiator=resources_data.get("negotiator", False),
                additional_units=resources_data.get("additional_units", 0),
                priority=resources_data.get("priority", "IMMEDIATE")
            )
            
            return CriticalIncidentReport(
                severity="CRITICAL_EMERGENCY",
                incident_type=data.get("incident_type", "OTHER_CRITICAL"),
                location=location,
                details=incident_details,
                emotion=emotion,
                resources=resources,
                executive_summary=data.get("executive_summary", "Critical incident"),
                recommended_actions=data.get("recommended_actions", []),
                key_facts=data.get("key_facts", []),
                confidence_score=float(data.get("confidence_score", 0.8)),
                dispatcher_message=data.get("dispatcher_message", "Help is on the way to your location. I'm staying on the line with you. Can you describe what you see around you right now?")
            )
            
        except Exception as e:
            print(f"   ⚠️  Triage parsing error: {e}, using fallback")
            # Return fallback report
            return CriticalIncidentReport(
                severity="CRITICAL_EMERGENCY",
                incident_type="OTHER_CRITICAL",
                location=location,
                details=IncidentDetails(
                    incident_type="unknown",
                    threat_level="UNKNOWN",
                    injuries_reported=False,
                    weapons_involved=False,
                    bystanders_at_risk=False
                ),
                emotion=emotion,
                resources=ResourceRequirements(
                    police=True,
                    ambulance=True,
                    fire=False,
                    swat=False,
                    negotiator=False,
                    additional_units=2,
                    priority="IMMEDIATE"
                ),
                executive_summary=f"Error in analysis: {str(e)}",
                recommended_actions=["Manual review required"],
                dispatcher_message="I understand this is an emergency. All available units are being dispatched to your location. I'm staying on the line with you - can you tell me if you're in a safe spot right now?",
                key_facts=["Analysis error occurred"],
                confidence_score=0.0
            )
    
    def _analyze_emotion(self, transcript: str) -> EmotionAnalysis:
        """Analyze caller emotion using Haiku."""
        
        system_prompt = """You are an emotion analysis expert for emergency calls.

Detect:
- Primary emotion (PANIC, FEAR, DISTRESS, CALM, ANGER, CONFUSED)
- Emotion intensity (LOW, MEDIUM, HIGH, EXTREME)
- Specific indicators
- Recommended approach"""

        human_prompt = f"""Analyze the caller's emotional state.

RETURN ONLY VALID JSON:
{{
  "primary_emotion": "PANIC or FEAR or DISTRESS or CALM or ANGER or CONFUSED",
  "intensity": "LOW or MEDIUM or HIGH or EXTREME",
  "indicators": ["indicator1", "indicator2"],
  "recommended_approach": "Suggested communication approach"
}}

TRANSCRIPT:
{transcript}

Return ONLY JSON."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.emotion_llm.invoke(messages)
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
                    raise ValueError("No JSON in emotion response")
            
            data = json.loads(json_str)
            
            return EmotionAnalysis(
                primary_emotion=data.get("primary_emotion", "CALM"),
                intensity=data.get("intensity", "MEDIUM"),
                indicators=data.get("indicators", []),
                recommended_approach=data.get("recommended_approach", "Standard 911 protocol")
            )
            
        except Exception as e:
            print(f"   ⚠️  Emotion analysis error: {e}, using fallback")
            return EmotionAnalysis(
                primary_emotion="CALM",
                intensity="MEDIUM",
                indicators=[],
                recommended_approach="Standard 911 protocol"
            )


# Singleton instance
_triage_agent = None


def get_triage_agent() -> TriageAgent:
    """Get or create singleton TriageAgent instance."""
    global _triage_agent
    if _triage_agent is None:
        _triage_agent = TriageAgent()
    return _triage_agent


if __name__ == "__main__":
    """Test the TriageAgent"""
    print("Testing TriageAgent...")
    
    test_transcript = """
    Dispatcher: 9-1-1, what's your emergency?
    Caller: I'm at West High School. There's a guy with a gun.
    Dispatcher: Which high school?
    Caller: West High. He's shooting!
    """
    
    agent = get_triage_agent()
    result = agent.analyze_critical_call(test_transcript)
    print(f"\nResult: {result}")
