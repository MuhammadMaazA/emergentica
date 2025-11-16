"""
Pydantic Schemas for Emergentica
================================

All structured data models used throughout the agentic system.
These schemas ensure type safety and enable structured outputs from LLMs.
"""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================
# Phase 1: Agent Schemas
# ============================================

class CallClassification(BaseModel):
    """
    Output schema for RouterAgent.
    Determines the severity level and routing decision.
    """
    
    severity: Literal["CRITICAL_EMERGENCY", "STANDARD_ASSISTANCE", "NON_EMERGENCY"] = Field(
        description="Severity level of the call"
    )
    
    confidence: float = Field(
        description="Confidence score for classification (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    reasoning: str = Field(
        description="Brief explanation for the classification"
    )
    
    route_to: Literal["TRIAGE_AGENT", "INFO_AGENT"] = Field(
        description="Which agent should handle this call"
    )


class EmotionAnalysis(BaseModel):
    """
    Output schema for emotion detection (used by TriageAgent).
    Analyzes caller's emotional state for better response.
    """
    
    primary_emotion: Literal["PANIC", "FEAR", "DISTRESS", "ANGER", "CALM", "CONFUSED"] = Field(
        description="Primary emotional state of the caller"
    )
    
    intensity: Literal["LOW", "MEDIUM", "HIGH", "EXTREME"] = Field(
        description="Intensity level of the emotion"
    )
    
    indicators: List[str] = Field(
        description="Specific phrases or patterns indicating this emotion"
    )
    
    recommended_approach: str = Field(
        description="Suggested communication approach for this emotional state"
    )


class LocationInfo(BaseModel):
    """Geographic location information."""
    
    address: Optional[str] = Field(default=None, description="Full address if available")
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")
    landmark: Optional[str] = Field(default=None, description="Nearby landmark or description")
    verified: bool = Field(default=False, description="Whether location was verified/geocoded")


class IncidentDetails(BaseModel):
    """Core details about the incident."""
    
    incident_type: str = Field(description="Type of incident (shooting, fire, medical, etc.)")
    threat_level: Literal["ACTIVE", "CONTAINED", "RESOLVED", "UNKNOWN"] = Field(
        description="Current threat status"
    )
    injuries_reported: bool = Field(description="Whether injuries have been reported")
    injury_count: Optional[int] = Field(default=None, description="Number of injured if known")
    suspect_description: Optional[str] = Field(default=None, description="Description of suspect if applicable")
    weapons_involved: bool = Field(default=False, description="Whether weapons are involved")
    bystanders_at_risk: bool = Field(default=False, description="Whether bystanders are at risk")


class ResourceRequirements(BaseModel):
    """Required emergency resources."""
    
    police: bool = Field(description="Police response needed")
    ambulance: bool = Field(description="Medical response needed")
    fire: bool = Field(description="Fire response needed")
    swat: bool = Field(default=False, description="SWAT/tactical team needed")
    negotiator: bool = Field(default=False, description="Crisis negotiator needed")
    additional_units: int = Field(default=0, description="Number of additional units needed")
    priority: Literal["IMMEDIATE", "URGENT", "STANDARD", "LOW"] = Field(
        description="Response priority level"
    )


class CriticalIncidentReport(BaseModel):
    """
    Final comprehensive output from TriageAgent.
    This is the primary data structure displayed on the dashboard.
    """
    
    # Core Classification
    severity: str = Field(description="Call severity level")
    incident_type: str = Field(description="Type of incident")
    
    # Location
    location: LocationInfo = Field(description="Location information")
    
    # Incident Details
    details: IncidentDetails = Field(description="Detailed incident information")
    
    # Emotional Context
    emotion: EmotionAnalysis = Field(description="Caller emotional analysis")
    
    # Resources
    resources: ResourceRequirements = Field(description="Required emergency resources")
    
    # Executive Summary
    executive_summary: str = Field(
        description="2-3 sentence summary for quick dispatcher review"
    )
    
    # Recommended Actions
    recommended_actions: List[str] = Field(
        description="Prioritized list of recommended actions"
    )
    
    # Critical Information
    key_facts: List[str] = Field(
        description="Critical facts extracted from the call"
    )
    
    # Metadata
    confidence_score: float = Field(
        description="Overall confidence in the analysis",
        ge=0.0,
        le=1.0
    )
    
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Time taken to process (milliseconds)"
    )
    
    dispatcher_message: str = Field(
        default="",
        description="Natural conversational response to speak to caller during critical emergency"
    )


class InfoAgentResponse(BaseModel):
    """
    Output schema for InfoAgent (handles non-critical calls).
    Simpler structure for lower-priority calls.
    """
    
    call_type: str = Field(description="Type of call")
    summary: str = Field(description="Brief summary of the call")
    location: Optional[LocationInfo] = Field(default=None, description="Location if provided")
    recommended_action: str = Field(description="Recommended action or response")
    additional_info: List[str] = Field(default_factory=list, description="Additional relevant information")
    requires_follow_up: bool = Field(default=False, description="Whether follow-up is needed")
    response: str = Field(default="", description="Conversational response to speak to caller")
    address: Optional[str] = Field(default=None, description="Street address extracted from conversation")
    postcode: Optional[str] = Field(default=None, description="Postcode extracted from conversation")
    caller_emotion: str = Field(default="CALM", description="Caller's emotional state")
    emotion_intensity: str = Field(default="LOW", description="Intensity of caller's emotion")


# ============================================
# Phase 2: Voice & Dashboard Schemas
# ============================================

class VoiceTranscript(BaseModel):
    """Real-time voice transcript from Retell AI."""
    
    call_id: str = Field(description="Unique call identifier")
    transcript: str = Field(description="Full conversation transcript")
    duration_seconds: float = Field(description="Call duration in seconds")
    timestamp: datetime = Field(description="When the call was received")
    caller_number: Optional[str] = Field(default=None, description="Caller phone number if available")


class DashboardUpdate(BaseModel):
    """Update message sent to the Streamlit dashboard."""
    
    call_id: str = Field(description="Unique call identifier")
    status: Literal["RECEIVING", "PROCESSING", "COMPLETE", "ERROR"] = Field(
        description="Current processing status"
    )
    transcript: str = Field(description="Call transcript")
    classification: Optional[CallClassification] = Field(
        default=None,
        description="Initial classification from RouterAgent"
    )
    report: Optional[CriticalIncidentReport] = Field(
        default=None,
        description="Full report from TriageAgent (if critical)"
    )
    info_response: Optional[InfoAgentResponse] = Field(
        default=None,
        description="Response from InfoAgent (if non-critical)"
    )
    timestamp: datetime = Field(description="Update timestamp")


# ============================================
# Phase 4: Benchmark Schemas
# ============================================

class BenchmarkResult(BaseModel):
    """Individual benchmark test result."""
    
    file_id: str = Field(description="Source file identifier")
    ground_truth_severity: str = Field(description="Ground truth label from preprocessing")
    predicted_severity: str = Field(description="Predicted severity from RouterAgent")
    correct: bool = Field(description="Whether prediction matches ground truth")
    routing_latency_ms: int = Field(description="Time to classify (milliseconds)")
    triage_latency_ms: Optional[int] = Field(
        default=None,
        description="Time for full triage (if critical)"
    )
    model_used: str = Field(description="Model used for routing")
    cost_usd: float = Field(description="Cost for processing this call")


class BenchmarkReport(BaseModel):
    """Final benchmark performance report."""
    
    # Accuracy Metrics
    total_calls: int = Field(description="Total calls tested")
    correct_predictions: int = Field(description="Number of correct classifications")
    routing_accuracy: float = Field(
        description="Overall routing accuracy percentage",
        ge=0.0,
        le=100.0
    )
    
    # Per-Category Accuracy
    critical_accuracy: float = Field(description="Accuracy for critical calls")
    standard_accuracy: float = Field(description="Accuracy for standard calls")
    non_emergency_accuracy: float = Field(description="Accuracy for non-emergency calls")
    
    # Latency Metrics
    avg_routing_latency_ms: float = Field(description="Average routing time")
    avg_critical_triage_time_ms: float = Field(description="Average critical call processing time")
    p95_routing_latency_ms: float = Field(description="95th percentile routing latency")
    p95_critical_triage_time_ms: float = Field(description="95th percentile triage latency")
    
    # Cost Analysis
    total_cost_usd: float = Field(description="Total cost for processing all calls")
    avg_cost_per_call_usd: float = Field(description="Average cost per call")
    cost_savings_vs_sonnet_only: float = Field(
        description="Percentage cost savings vs using Sonnet for all calls"
    )
    
    # Model Usage
    haiku_calls: int = Field(description="Calls processed by Haiku (routing)")
    sonnet_calls: int = Field(description="Calls processed by Sonnet (critical triage)")
    llama_calls: int = Field(description="Calls processed by Llama (info gathering)")
    
    # Detailed Results
    results: List[BenchmarkResult] = Field(description="Individual test results")
    
    # Metadata
    test_date: datetime = Field(description="When the benchmark was run")
    dataset_file: str = Field(description="Source dataset file")


# ============================================
# Tool Schemas
# ============================================

class GeocodingResult(BaseModel):
    """Result from geocoding API."""
    
    success: bool = Field(description="Whether geocoding was successful")
    address: Optional[str] = Field(default=None, description="Formatted address")
    latitude: Optional[float] = Field(default=None, description="Latitude")
    longitude: Optional[float] = Field(default=None, description="Longitude")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class SearchResult(BaseModel):
    """Result from public information search."""
    
    query: str = Field(description="Search query used")
    results: List[str] = Field(description="List of relevant information found")
    sources: List[str] = Field(description="Source URLs or references")
    success: bool = Field(description="Whether search was successful")


# ============================================
# Internal State Schemas (for LangGraph)
# ============================================

class AgentState(BaseModel):
    """
    Internal state passed between agents in the LangGraph workflow.
    This is the 'memory' of the agentic system.
    """
    
    # Input
    call_id: str
    transcript: str
    timestamp: datetime
    
    # Router Output
    classification: Optional[CallClassification] = None
    
    # Intermediate Processing
    location_info: Optional[LocationInfo] = None
    emotion_analysis: Optional[EmotionAnalysis] = None
    
    # Final Outputs
    critical_report: Optional[CriticalIncidentReport] = None
    info_response: Optional[InfoAgentResponse] = None
    
    # Metadata
    processing_start_time: Optional[datetime] = None
    processing_end_time: Optional[datetime] = None
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


if __name__ == "__main__":
    """
    Schema validation and example generation.
    Run this to verify all schemas are valid and see example outputs.
    """
    
    print("=" * 80)
    print("Emergentica Schema Validation")
    print("=" * 80)
    
    # Test CallClassification
    print("\n1. CallClassification (RouterAgent output):")
    classification = CallClassification(
        severity="CRITICAL_EMERGENCY",
        confidence=0.95,
        reasoning="Active shooter situation with ongoing threat",
        route_to="TRIAGE_AGENT"
    )
    print(classification.model_dump_json(indent=2))
    
    # Test EmotionAnalysis
    print("\n2. EmotionAnalysis:")
    emotion = EmotionAnalysis(
        primary_emotion="PANIC",
        intensity="EXTREME",
        indicators=["Oh my God", "screaming", "rapid speech"],
        recommended_approach="Calm, clear, directive communication"
    )
    print(emotion.model_dump_json(indent=2))
    
    # Test CriticalIncidentReport
    print("\n3. CriticalIncidentReport (TriageAgent output):")
    report = CriticalIncidentReport(
        severity="CRITICAL_EMERGENCY",
        incident_type="Active Shooter",
        location=LocationInfo(
            address="West High School, 123 Main St",
            latitude=39.1234,
            longitude=-84.5678,
            verified=True
        ),
        details=IncidentDetails(
            incident_type="Active Shooter",
            threat_level="ACTIVE",
            injuries_reported=True,
            injury_count=1,
            weapons_involved=True,
            bystanders_at_risk=True
        ),
        emotion=emotion,
        resources=ResourceRequirements(
            police=True,
            ambulance=True,
            fire=False,
            swat=True,
            priority="IMMEDIATE",
            additional_units=5
        ),
        executive_summary="Active shooter at West High School, 3rd floor. One confirmed shot fired at teacher. 22 students sheltering in room 309. Immediate SWAT response required.",
        recommended_actions=[
            "Deploy SWAT team immediately",
            "Secure all building exits",
            "Send ambulance for potential casualties",
            "Establish perimeter and evacuate adjacent areas"
        ],
        key_facts=[
            "Location: West High School, Room 316, 3rd floor",
            "Weapon: Confirmed firearm",
            "Shots fired: 1",
            "Potential victims: 1 teacher",
            "Students at risk: 22+ in building"
        ],
        confidence_score=0.95,
        processing_time_ms=1250
    )
    print(report.model_dump_json(indent=2))
    
    print("\n" + "=" * 80)
    print("✅ All schemas validated successfully!")
    print("=" * 80)
