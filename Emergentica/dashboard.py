"""
Streamlit Dashboard for Emergentica
===================================

Real-time dispatcher interface showing:
- Live call transcripts
- Severity classification
- Critical incident reports
- Recommended actions
- Resource allocation

The dashboard polls latest_call.json for updates and displays
processed emergency call information in a clear, actionable format.
"""

import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd


# ============================================
# Configuration
# ============================================

st.set_page_config(
    page_title="Emergentica - Emergency Dispatcher Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .critical-alert {
        background-color: #ff4444;
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    
    .standard-alert {
        background-color: #ff9800;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
    }
    
    .non-emergency-alert {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 6px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .action-item {
        background-color: #e3f2fd;
        padding: 10px;
        border-left: 4px solid #2196F3;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# Data Loading
# ============================================

def load_latest_call() -> Optional[Dict[str, Any]]:
    """Load the latest call data from JSON file."""
    
    data_file = Path("data/latest_call.json")
    
    if not data_file.exists():
        return None
    
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading call data: {e}")
        return None


# ============================================
# Display Components
# ============================================

def display_header():
    """Display dashboard header."""
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🚨 Emergentica - Emergency Dispatcher Dashboard")
    
    with col2:
        st.metric("Status", "🟢 ONLINE", delta=None)
    
    with col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric("Time", current_time)


def display_severity_alert(severity: str):
    """Display severity-based alert banner."""
    
    if severity == "CRITICAL_EMERGENCY":
        st.markdown(
            '<div class="critical-alert">🚨 CRITICAL EMERGENCY 🚨</div>',
            unsafe_allow_html=True
        )
    elif severity == "STANDARD_ASSISTANCE":
        st.markdown(
            '<div class="standard-alert">⚠️ STANDARD ASSISTANCE REQUIRED</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="non-emergency-alert">ℹ️ NON-EMERGENCY</div>',
            unsafe_allow_html=True
        )


def display_critical_report(report: Dict[str, Any]):
    """Display detailed critical incident report."""
    
    st.header("📋 Critical Incident Report")
    
    # Executive Summary
    st.markdown("### 📝 Executive Summary")
    st.info(report.get('executive_summary', 'No summary available'))
    
    # Key columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Incident Details
        st.markdown("### 🎯 Incident Details")
        details = report.get('details', {})
        
        st.markdown(f"**Type:** {report.get('incident_type', 'Unknown')}")
        st.markdown(f"**Threat Level:** {details.get('threat_level', 'Unknown')}")
        st.markdown(f"**Injuries Reported:** {'Yes ⚠️' if details.get('injuries_reported') else 'No ✅'}")
        
        if details.get('injury_count'):
            st.markdown(f"**Injury Count:** {details.get('injury_count')}")
        
        st.markdown(f"**Weapons Involved:** {'Yes 🔫' if details.get('weapons_involved') else 'No ✅'}")
        st.markdown(f"**Bystanders at Risk:** {'Yes ⚠️' if details.get('bystanders_at_risk') else 'No ✅'}")
        
        # Location
        st.markdown("### 📍 Location")
        location = report.get('location', {})
        
        loc_col1, loc_col2 = st.columns(2)
        
        with loc_col1:
            if location.get('address'):
                st.markdown(f"**Address:** {location['address']}")
            
            if location.get('postcode'):
                st.markdown(f"**Postcode:** {location['postcode']}")
        
        with loc_col2:
            landmark = location.get('landmark')
            if landmark and not any(word in str(landmark).lower() for word in ['suspicious', 'unknown', 'none', 'n/a']):
                st.markdown(f"**Landmark:** {landmark}")
            
            if location.get('verified'):
                st.success("✅ Verified")
            else:
                st.warning("⚠️ Unverified")
    
    with col2:
        # Emotional State with emoji
        st.markdown("### � Caller Emotional State")
        emotion = report.get('emotion', {})
        
        primary_emotion = emotion.get('primary_emotion', 'Unknown')
        intensity = emotion.get('intensity', 'Unknown')
        
        # Map emotions to emojis for critical calls
        emotion_emojis = {
            'PANICKED': '😱',
            'TERRIFIED': '😨',
            'SCARED': '😰',
            'DISTRESSED': '😢',
            'ANXIOUS': '😟',
            'CALM': '😌',
            'CONFUSED': '😕'
        }
        
        emoji = emotion_emojis.get(primary_emotion.upper(), '😐')
        
        st.markdown(f"**{emoji} {primary_emotion.upper()}** - *{intensity} Intensity*")
        st.markdown(f"**Approach:** {emotion.get('recommended_approach', 'Standard protocol')}")
        
        # Resource Requirements
        st.markdown("### 🚓 Units Dispatched")
        resources = report.get('resources', {})
        
        required_services = []
        if resources.get('police'):
            required_services.append("👮 Police")
        if resources.get('ambulance'):
            required_services.append("🚑 Ambulance")
        if resources.get('fire'):
            required_services.append("🚒 Fire")
        if resources.get('swat'):
            required_services.append("🎯 SWAT")
        if resources.get('negotiator'):
            required_services.append("🗣️ Negotiator")
        
        for service in required_services:
            st.markdown(service)
        
        priority = resources.get('priority', 'STANDARD')
        st.markdown(f"**Priority:** {priority}")
        
        if resources.get('additional_units', 0) > 0:
            st.markdown(f"**Additional Units:** {resources['additional_units']}")
    
    # Recommended Actions
    st.markdown("### ✅ Recommended Actions")
    actions = report.get('recommended_actions', [])
    
    for i, action in enumerate(actions, 1):
        st.markdown(f"**{i}.** {action}")
    
    # Key Facts
    st.markdown("### 🔑 Key Facts")
    key_facts = report.get('key_facts', [])
    
    for fact in key_facts:
        st.markdown(f"• {fact}")
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence = report.get('confidence_score', 0)
        st.metric("Confidence", f"{confidence:.1%}")
    
    with col2:
        processing_time = report.get('processing_time_ms', 0)
        st.metric("Processing Time", f"{processing_time}ms")
    
    with col3:
        st.metric("Model", "Claude Haiku")


def display_info_response(response: Dict[str, Any]):
    """Display info agent response for non-critical calls."""
    
    st.header("📋 Call Information")
    
    # Top row: Call Details and Caller Emotion
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📞 Call Details")
        st.markdown(f"**Type:** {response.get('call_type', 'Unknown')}")
        st.markdown(f"**Summary:** {response.get('summary', 'No summary available')}")
    
    with col2:
        # Caller Emotion Display
        st.markdown("### 😊 Caller Emotional State")
        
        caller_emotion = response.get('caller_emotion', 'CALM')
        emotion_intensity = response.get('emotion_intensity', 'LOW')
        
        # Map emotions to emojis
        emotion_emojis = {
            'PANICKED': '😱',
            'SCARED': '😰',
            'CONCERNED': '😟',
            'ANXIOUS': '😨',
            'CALM': '😌',
            'CONFUSED': '😕',
            'ANGRY': '😠',
            'DISTRESSED': '😢'
        }
        
        emoji = emotion_emojis.get(caller_emotion.upper(), '😐')
        
        st.markdown(f"**{emoji} {caller_emotion.upper()}** - *{emotion_intensity} Intensity*")
    
    # Location Section - FIXED with address + postcode
    st.markdown("### 📍 Location")
    location = response.get('location')
    
    if location:
        loc_col1, loc_col2, loc_col3 = st.columns(3)
        
        with loc_col1:
            address = location.get('address')
            if address:
                st.markdown(f"**Address:** {address}")
            else:
                st.markdown("**Address:** Not provided")
        
        with loc_col2:
            postcode = location.get('postcode')
            if postcode:
                st.markdown(f"**Postcode:** {postcode}")
            else:
                st.markdown("**Postcode:** Not provided")
        
        with loc_col3:
            landmark = location.get('landmark')
            # Only show landmark if it's valid (not garbage like "looks suspicious")
            if landmark and not any(word in str(landmark).lower() for word in ['suspicious', 'unknown', 'none', 'n/a']):
                st.markdown(f"**Landmark:** {landmark}")
            
            if location.get('verified'):
                st.success("✅ Verified")
            else:
                st.warning("⚠️ Unverified")
    
    # Units Dispatched Section - CHANGED from "Recommended Action"
    st.markdown("### 🚓 Units Dispatched")
    
    dispatch_col1, dispatch_col2 = st.columns([2, 1])
    
    with dispatch_col1:
        recommended_action = response.get('recommended_action', 'Standard response protocol')
        
        # Add icons based on action content
        if 'police' in recommended_action.lower():
            st.info(f"👮 {recommended_action}")
        elif 'ambulance' in recommended_action.lower() or 'medical' in recommended_action.lower():
            st.info(f"🚑 {recommended_action}")
        elif 'fire' in recommended_action.lower():
            st.info(f"🚒 {recommended_action}")
        else:
            st.info(f"📋 {recommended_action}")
    
    with dispatch_col2:
        # Dispatch timestamp
        timestamp = response.get('timestamp') or datetime.now().isoformat()
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            st.markdown(f"**Dispatched:** {dt.strftime('%H:%M:%S')}")
        except:
            st.markdown(f"**Dispatched:** Now")
        
        if response.get('requires_follow_up'):
            st.warning("⚠️ Follow-up Required")
    
    # Additional Info
    additional_info = response.get('additional_info', [])
    if additional_info:
        st.markdown("### 📌 Additional Information")
        for info in additional_info:
            # Don't show postcode here if it's already in location
            if not (location and location.get('postcode') and 'postcode' in info.lower()):
                st.markdown(f"• {info}")


def display_transcript(transcript: str):
    """Display call transcript."""
    
    with st.expander("📄 View Full Transcript", expanded=False):
        st.text_area(
            "Transcript",
            value=transcript,
            height=300,
            disabled=True
        )


def display_metadata(call_data: Dict[str, Any]):
    """Display call metadata."""
    
    st.sidebar.header("📊 Call Metadata")
    
    st.sidebar.write(f"**Call ID:** {call_data.get('call_id', 'Unknown')}")
    st.sidebar.write(f"**Status:** {call_data.get('status', 'Unknown')}")
    
    timestamp = call_data.get('timestamp')
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            st.sidebar.write(f"**Time:** {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            st.sidebar.write(f"**Time:** {timestamp}")
    
    # Processing Info
    if call_data.get('processing_time_ms'):
        st.sidebar.write(f"**Processing Time:** {call_data['processing_time_ms']}ms")
    
    if call_data.get('route_taken'):
        st.sidebar.write(f"**Route:** {call_data['route_taken']}")
    
    # Classification details
    classification = call_data.get('classification')
    if classification:
        st.sidebar.subheader("🔍 Classification")
        st.sidebar.write(f"**Severity:** {classification.get('severity', 'Unknown')}")
        st.sidebar.write(f"**Confidence:** {classification.get('confidence', 0):.1%}")
        
        with st.sidebar.expander("Reasoning"):
            st.write(classification.get('reasoning', 'No reasoning available'))


# ============================================
# Main Dashboard
# ============================================

def main():
    """Main dashboard application."""
    
    # Header
    display_header()
    
    st.markdown("---")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider(
            "Refresh interval (seconds)",
            min_value=1,
            max_value=10,
            value=2
        )
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Load latest call data
    call_data = load_latest_call()
    
    if call_data is None:
        st.info("👂 Waiting for incoming calls...")
        st.markdown("""
        ### System Ready
        
        The Emergentica system is online and ready to process emergency calls.
        
        **To test:**
        1. Call the configured Twilio number, OR
        2. Send a test webhook to the FastAPI server, OR
        3. Run the benchmark script to process historical calls
        
        This dashboard will automatically update when calls are received.
        """)
    else:
        # Display metadata in sidebar
        display_metadata(call_data)
        
        # Get classification
        classification = call_data.get('classification', {})
        severity = classification.get('severity', 'UNKNOWN')
        
        # Display severity alert
        display_severity_alert(severity)
        
        # Display appropriate report based on severity
        if severity == "CRITICAL_EMERGENCY":
            critical_report = call_data.get('critical_report')
            if critical_report:
                display_critical_report(critical_report)
            else:
                st.error("Critical report data not available")
        else:
            info_response = call_data.get('info_response')
            if info_response:
                display_info_response(info_response)
            else:
                st.warning("Call information not available")
        
        # Display transcript
        transcript = call_data.get('transcript', '')
        if transcript:
            display_transcript(transcript)
        
        # Errors if any
        errors = call_data.get('errors', [])
        if errors:
            st.error("⚠️ Processing Errors:")
            for error in errors:
                st.write(f"• {error}")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    main()
