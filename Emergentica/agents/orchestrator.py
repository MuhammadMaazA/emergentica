"""
LangGraph Orchestrator - Multi-Agent Workflow
==============================================

This is the brain of Emergentica. It orchestrates the flow between
multiple specialized agents using LangGraph's state machine.

Workflow:
1. RouterAgent classifies severity (Haiku - fast & cheap)
2. Based on severity:
   - CRITICAL → TriageAgent (Sonnet - deep analysis)
   - STANDARD/NON_EMERGENCY → InfoAgent (Llama - cost-effective)
3. Returns structured output for dashboard

All workflow execution is traced in LangSmith for observability.
"""

from typing import TypedDict, Literal, Annotated, Dict, Any
from datetime import datetime
import time
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END
from langsmith import traceable

from agents.router_agent import get_router_agent
from agents.triage_agent import get_triage_agent
from agents.info_agent import get_info_agent
from schemas import (
    CallClassification,
    CriticalIncidentReport,
    InfoAgentResponse,
    AgentState
)
from config import config


# ============================================
# State Definition
# ============================================

class DispatchState(TypedDict):
    """
    State passed between nodes in the LangGraph workflow.
    This represents all the information flowing through the system.
    """
    
    # Input
    call_id: str
    transcript: str
    timestamp: datetime
    
    # Router output
    classification: CallClassification | None
    
    # Final outputs
    critical_report: CriticalIncidentReport | None
    info_response: InfoAgentResponse | None
    
    # Metadata
    processing_start_time: datetime | None
    processing_end_time: datetime | None
    route_taken: str | None
    errors: list[str]


# ============================================
# Node Functions
# ============================================

@traceable(name="router_node")
def router_node(state: DispatchState) -> DispatchState:
    """
    Router node: Classify call severity using Haiku.
    
    This is always the first step in the workflow.
    Fast classification determines which agent handles the call.
    """
    
    print(f"\n🔍 [ROUTER] Classifying call {state['call_id']}...")
    
    try:
        router = get_router_agent()
        classification = router.classify(state['transcript'])
        
        state['classification'] = classification
        state['route_taken'] = f"router → {classification.route_to.lower()}"
        
        print(f"   ✓ Classified as: {classification.severity}")
        print(f"   ✓ Routing to: {classification.route_to}")
        print(f"   ✓ Confidence: {classification.confidence:.2f}")
        
    except Exception as e:
        error_msg = f"Router error: {str(e)}"
        state['errors'].append(error_msg)
        print(f"   ✗ {error_msg}")
        
        # Default to standard assistance on error
        from schemas import CallClassification
        state['classification'] = CallClassification(
            severity="STANDARD_ASSISTANCE",
            confidence=0.0,
            reasoning="Error during routing - defaulting to standard",
            route_to="INFO_AGENT"
        )
    
    return state


@traceable(name="triage_node")
def triage_node(state: DispatchState) -> DispatchState:
    """
    Triage node: Deep analysis of critical emergencies using Sonnet.
    
    Only called for CRITICAL_EMERGENCY situations.
    Performs comprehensive analysis and resource allocation.
    """
    
    print(f"\n🚨 [TRIAGE] Analyzing critical emergency {state['call_id']}...")
    
    try:
        triage = get_triage_agent()
        report = triage.analyze_critical_call(
            state['transcript'],
            state['classification'].severity
        )
        
        state['critical_report'] = report
        
        print(f"   ✓ Incident Type: {report.incident_type}")
        print(f"   ✓ Threat Level: {report.details.threat_level}")
        print(f"   ✓ Processing Time: {report.processing_time_ms}ms")
        print(f"   ✓ Confidence: {report.confidence_score:.2f}")
        
    except Exception as e:
        error_msg = f"Triage error: {str(e)}"
        state['errors'].append(error_msg)
        print(f"   ✗ {error_msg}")
    
    return state


@traceable(name="info_node")
def info_node(state: DispatchState) -> DispatchState:
    """
    Info node: Handle non-critical calls using Llama.
    
    Called for STANDARD_ASSISTANCE and NON_EMERGENCY.
    Cost-effective processing for lower-priority situations.
    """
    
    print(f"\n📋 [INFO] Processing call {state['call_id']}...")
    
    try:
        info = get_info_agent()
        response = info.process_call(
            state['transcript'],
            state['classification'].severity
        )
        
        state['info_response'] = response
        
        print(f"   ✓ Call Type: {response.call_type}")
        print(f"   ✓ Recommended Action: {response.recommended_action}")
        
    except Exception as e:
        error_msg = f"Info agent error: {str(e)}"
        state['errors'].append(error_msg)
        print(f"   ✗ {error_msg}")
    
    return state


# ============================================
# Routing Logic
# ============================================

def route_after_classification(state: DispatchState) -> Literal["triage", "info"]:
    """
    Conditional routing based on classification.
    
    Returns:
        "triage" for critical emergencies
        "info" for everything else
    """
    
    if state['classification'] is None:
        # Default to info on error
        return "info"
    
    route_to = state['classification'].route_to
    
    if route_to == "TRIAGE_AGENT":
        return "triage"
    else:
        return "info"


# ============================================
# Graph Construction
# ============================================

def create_dispatch_workflow() -> StateGraph:
    """
    Create the complete LangGraph workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Create workflow
    workflow = StateGraph(DispatchState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("info", info_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "router",
        route_after_classification,
        {
            "triage": "triage",
            "info": "info"
        }
    )
    
    # Both triage and info lead to END
    workflow.add_edge("triage", END)
    workflow.add_edge("info", END)
    
    # Compile
    return workflow.compile()


# ============================================
# Main Orchestrator Class
# ============================================

class DispatchOrchestrator:
    """
    Main orchestrator for the Emergentica system.
    Manages the complete workflow from transcript to final report.
    """
    
    def __init__(self):
        """Initialize the orchestrator with LangGraph workflow."""
        self.workflow = create_dispatch_workflow()
    
    @traceable(name="process_call")
    def process_call(
        self,
        call_id: str,
        transcript: str,
        timestamp: datetime | None = None
    ) -> Dict[str, Any]:
        """
        Process a complete emergency call through the agentic workflow.
        
        Args:
            call_id: Unique identifier for the call
            transcript: Full call transcript
            timestamp: When the call was received (default: now)
        
        Returns:
            Dictionary with processing results
        """
        
        if timestamp is None:
            timestamp = datetime.now()
        
        print("=" * 80)
        print(f"🚨 DISPATCHING CALL: {call_id}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Create initial state
        initial_state: DispatchState = {
            "call_id": call_id,
            "transcript": transcript,
            "timestamp": timestamp,
            "classification": None,
            "critical_report": None,
            "info_response": None,
            "processing_start_time": datetime.now(),
            "processing_end_time": None,
            "route_taken": None,
            "errors": []
        }
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            final_state['processing_end_time'] = datetime.now()
            
        except Exception as e:
            print(f"\n❌ Workflow execution error: {e}")
            final_state = initial_state
            final_state['errors'].append(f"Workflow error: {str(e)}")
            final_state['processing_end_time'] = datetime.now()
        
        # Calculate total time
        end_time = time.time()
        total_time_ms = int((end_time - start_time) * 1000)
        
        # Format output
        result = {
            "call_id": call_id,
            "status": "ERROR" if final_state['errors'] else "COMPLETE",
            "classification": final_state['classification'],
            "critical_report": final_state['critical_report'],
            "info_response": final_state['info_response'],
            "route_taken": final_state['route_taken'],
            "total_processing_time_ms": total_time_ms,
            "errors": final_state['errors'],
            "timestamp": timestamp.isoformat()
        }
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"✅ CALL PROCESSING COMPLETE: {call_id}")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Route: {result['route_taken']}")
        print(f"Total Time: {total_time_ms}ms")
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
        print("=" * 80)
        
        return result


# Singleton instance
_orchestrator = None


def get_orchestrator() -> DispatchOrchestrator:
    """Get or create singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DispatchOrchestrator()
    return _orchestrator


# ============================================
# Testing & Demo
# ============================================

if __name__ == "__main__":
    """
    Test the complete orchestrator with sample calls.
    """
    
    print("\n" + "=" * 80)
    print("EMERGENTICA ORCHESTRATOR TEST")
    print("=" * 80)
    
    # Sample critical call
    critical_call = """
Dispatcher: 9-1-1, what's your emergency?
Caller: I'm at West High School. There's a guy with a gun.
Dispatcher: Which high school?
Caller: West High.
Dispatcher: Okay, we have the police dispatched. Can you give me a description?
Caller: I don't know. The guy is just running through the halls.
Dispatcher: Can you go somewhere where you're safe?
Caller: I'm locked in a room.
Dispatcher: Where in the building are you?
Caller: Third floor.
"""
    
    # Sample non-emergency call
    non_emergency_call = """
Dispatcher: 9-1-1, what's your emergency?
Caller: Hi, I was wondering about a car that's been parked on my street for days.
Dispatcher: Is it blocking traffic or your driveway?
Caller: No, but it looks abandoned.
Dispatcher: I can send an officer to check on it.
"""
    
    try:
        orchestrator = get_orchestrator()
        
        # Test 1: Critical Emergency
        print("\n\nTEST 1: CRITICAL EMERGENCY")
        print("-" * 80)
        result1 = orchestrator.process_call(
            call_id="TEST_CRITICAL_001",
            transcript=critical_call
        )
        
        # Test 2: Non-Emergency
        print("\n\nTEST 2: NON-EMERGENCY")
        print("-" * 80)
        result2 = orchestrator.process_call(
            call_id="TEST_NON_EMERGENCY_001",
            transcript=non_emergency_call
        )
        
        print("\n\n" + "=" * 80)
        print("✅ ALL ORCHESTRATOR TESTS PASSED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        print("\nPlease ensure:")
        print("  1. Virtual environment is activated")
        print("  2. Dependencies are installed (pip install -r requirements.txt)")
        print("  3. .env file is configured with API keys")
