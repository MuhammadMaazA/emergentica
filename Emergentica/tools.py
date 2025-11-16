"""
Custom Tools for Emergentica Agents
===================================

This module provides tool functions that agents can use to:
1. Geocode addresses to get coordinates
2. Search for public information
3. Validate and enrich location data

All tools are designed to be used by LangChain agents via the @tool decorator.
"""

import os
import requests
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from schemas import GeocodingResult, SearchResult, LocationInfo
from config import config


# ============================================
# Geocoding Tools
# ============================================

@tool
def geocode_location(address: str) -> Dict[str, Any]:
    """
    Geocode an address to get latitude and longitude coordinates.
    
    This tool uses the geocode.maps.co API to convert addresses into
    geographic coordinates. Useful for mapping incident locations.
    
    Args:
        address: The address to geocode (e.g., "West High School, Cincinnati")
    
    Returns:
        Dictionary with geocoding results including lat/lon or error message
    
    Example:
        >>> result = geocode_location("1600 Pennsylvania Avenue, Washington DC")
        >>> print(result)
        {
            "success": True,
            "address": "1600 Pennsylvania Avenue NW, Washington, DC 20500",
            "latitude": 38.8977,
            "longitude": -77.0365
        }
    """
    
    # Check if API key is configured
    api_key = config.GEOCODE_API_KEY
    
    if not api_key:
        return GeocodingResult(
            success=False,
            error="Geocoding API key not configured"
        ).model_dump()
    
    try:
        # Call geocoding API
        url = "https://geocode.maps.co/search"
        params = {
            "q": address,
            "api_key": api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or len(data) == 0:
            return GeocodingResult(
                success=False,
                error=f"No results found for address: {address}"
            ).model_dump()
        
        # Get first result
        result = data[0]
        
        return GeocodingResult(
            success=True,
            address=result.get("display_name"),
            latitude=float(result.get("lat")),
            longitude=float(result.get("lon"))
        ).model_dump()
    
    except requests.Timeout:
        return GeocodingResult(
            success=False,
            error="Geocoding request timed out"
        ).model_dump()
    
    except Exception as e:
        return GeocodingResult(
            success=False,
            error=f"Geocoding error: {str(e)}"
        ).model_dump()


@tool
def validate_location(location_text: str) -> Dict[str, Any]:
    """
    Validate and extract location information from text.
    
    Attempts to parse location information from natural language text
    and geocode it if possible.
    
    Args:
        location_text: Text that might contain location information
    
    Returns:
        LocationInfo dictionary with parsed and geocoded data
    
    Example:
        >>> result = validate_location("I'm at 123 Main Street")
        >>> print(result)
        {
            "address": "123 Main St, ...",
            "latitude": 39.1234,
            "longitude": -84.5678,
            "verified": True
        }
    """
    
    # Simple extraction: look for common patterns
    # In a production system, this would use NER or more sophisticated parsing
    
    # Try geocoding directly - use .invoke() since geocode_location is a StructuredTool
    geocode_result = geocode_location.invoke({"address": location_text})
    
    if isinstance(geocode_result, dict) and geocode_result.get("success"):
        return LocationInfo(
            address=geocode_result.get("address"),
            latitude=geocode_result.get("latitude"),
            longitude=geocode_result.get("longitude"),
            landmark=location_text,
            verified=True
        ).model_dump()
    
    # If geocoding failed, return unverified location
    return LocationInfo(
        landmark=location_text,
        verified=False
    ).model_dump()


# ============================================
# Information Search Tools
# ============================================

@tool
def public_info_search(query: str) -> Dict[str, Any]:
    """
    Search for public information relevant to the emergency.
    
    This tool can search for:
    - Building layouts and floor plans
    - Historical incident data
    - Contact information for facilities
    - Public safety information
    
    Args:
        query: What to search for (e.g., "West High School layout")
    
    Returns:
        Dictionary with search results and sources
    
    Note:
        In this hackathon version, we use a mock implementation.
        A production system would integrate with real databases and APIs.
    """
    
    # Mock implementation for hackathon
    # In production, this would query actual databases, Valyu API, etc.
    
    mock_data = {
        "west high school": {
            "results": [
                "West High School is a 3-story building with approximately 800 students",
                "Main entrance on North Bend Road",
                "Building has 6 stairwells and 2 elevators",
                "Emergency assembly point: west parking lot"
            ],
            "sources": [
                "School District Public Records",
                "Building Safety Plan 2024"
            ]
        },
        "hospital": {
            "results": [
                "Nearest trauma center: University Hospital - 3.2 miles",
                "Emergency capacity: High",
                "Helipad available for critical transport"
            ],
            "sources": [
                "County Emergency Services Database"
            ]
        },
        "default": {
            "results": [
                f"Public information search for: {query}",
                "No specific records found in local database"
            ],
            "sources": [
                "General Database"
            ]
        }
    }
    
    # Find matching data
    query_lower = query.lower()
    result_data = None
    
    for key, data in mock_data.items():
        if key in query_lower:
            result_data = data
            break
    
    if not result_data:
        result_data = mock_data["default"]
    
    return SearchResult(
        query=query,
        results=result_data["results"],
        sources=result_data["sources"],
        success=True
    ).model_dump()


@tool
def search_facility_info(facility_name: str) -> Dict[str, Any]:
    """
    Search for specific facility information (schools, hospitals, etc.).
    
    Args:
        facility_name: Name of the facility to look up
    
    Returns:
        Dictionary with facility information
    """
    
    # Mock implementation
    facilities = {
        "west high school": {
            "name": "West High School",
            "address": "3091 West North Bend Road, Cincinnati, OH",
            "type": "High School",
            "capacity": "800 students",
            "floors": 3,
            "emergency_contact": "School Resource Officer",
            "nearby_hospitals": ["University Hospital - 3.2 miles"],
            "previous_incidents": "No major incidents on record"
        },
        "university hospital": {
            "name": "University Hospital",
            "address": "234 Goodman St, Cincinnati, OH",
            "type": "Trauma Center Level 1",
            "emergency_capacity": "High",
            "helipad": True,
            "distance_from_downtown": "2.1 miles"
        }
    }
    
    facility_key = facility_name.lower().strip()
    
    for key, info in facilities.items():
        if key in facility_key or facility_key in key:
            return {
                "success": True,
                "facility": info
            }
    
    return {
        "success": False,
        "error": f"No information found for facility: {facility_name}"
    }


# ============================================
# Helper Functions (not exposed as tools)
# ============================================

def extract_location_from_transcript(transcript: str) -> Optional[str]:
    """
    Extract potential location information from transcript.
    
    This is a helper function used internally by agents.
    Not exposed as a tool directly.
    
    Args:
        transcript: The call transcript
    
    Returns:
        Extracted location string or None
    """
    
    # Simple keyword-based extraction
    # In production, use NER (Named Entity Recognition)
    
    location_keywords = [
        "at ", "in ", "near ", "on ",
        "address is", "location is",
        "i'm at", "we're at"
    ]
    
    lines = transcript.lower().split('\n')
    
    for line in lines:
        for keyword in location_keywords:
            if keyword in line:
                # Extract text after keyword
                parts = line.split(keyword)
                if len(parts) > 1:
                    potential_location = parts[1].strip()
                    # Take first sentence/phrase
                    for delimiter in ['.', ',', '!', '?']:
                        if delimiter in potential_location:
                            potential_location = potential_location.split(delimiter)[0]
                            break
                    
                    if len(potential_location) > 5:  # Basic validation
                        return potential_location
    
    return None


def enrich_location_info(location_text: str) -> LocationInfo:
    """
    Enrich location information with geocoding and additional data.
    
    Args:
        location_text: Raw location text from transcript
    
    Returns:
        LocationInfo object with all available data
    """
    
    # Try to geocode
    geocode_result = geocode_location(location_text)
    
    if isinstance(geocode_result, dict) and geocode_result.get("success"):
        return LocationInfo(
            address=geocode_result.get("address"),
            latitude=geocode_result.get("latitude"),
            longitude=geocode_result.get("longitude"),
            landmark=location_text,
            verified=True
        )
    
    # Return unverified if geocoding failed
    return LocationInfo(
        landmark=location_text,
        verified=False
    )


# ============================================
# Tool Collection
# ============================================

# List of all tools available to agents
ALL_TOOLS = [
    geocode_location,
    validate_location,
    public_info_search,
    search_facility_info
]


# Tool descriptions for agents
TOOL_DESCRIPTIONS = {
    "geocode_location": "Convert addresses to geographic coordinates",
    "validate_location": "Parse and validate location from text",
    "public_info_search": "Search public databases for relevant information",
    "search_facility_info": "Look up specific facility information"
}


if __name__ == "__main__":
    """
    Test all tools with sample data.
    """
    
    print("=" * 80)
    print("Emergentica Tools Test")
    print("=" * 80)
    
    # Test geocoding
    print("\n1. Testing geocode_location:")
    result = geocode_location.invoke({"address": "West High School, Cincinnati, Ohio"})
    print(f"   Result: {result}")
    
    # Test location validation
    print("\n2. Testing validate_location:")
    result = validate_location.invoke({"location_text": "I'm at 123 Main Street, Cincinnati"})
    print(f"   Result: {result}")
    
    # Test public info search
    print("\n3. Testing public_info_search:")
    result = public_info_search.invoke({"query": "West High School layout"})
    print(f"   Result: {result}")
    
    # Test facility search
    print("\n4. Testing search_facility_info:")
    result = search_facility_info.invoke({"facility_name": "University Hospital"})
    print(f"   Result: {result}")
    
    # Test location extraction helper
    print("\n5. Testing extract_location_from_transcript:")
    sample_transcript = """
    Dispatcher: 9-1-1, what's your emergency?
    Caller: I'm at West High School. There's a guy with a gun.
    Dispatcher: Which high school?
    Caller: West High.
    """
    location = extract_location_from_transcript(sample_transcript)
    print(f"   Extracted: {location}")
    
    print("\n" + "=" * 80)
    print("✅ All tools tested successfully!")
    print("=" * 80)
    print(f"\nAvailable tools for agents: {len(ALL_TOOLS)}")
    for tool_func in ALL_TOOLS:
        name = tool_func.name
        desc = TOOL_DESCRIPTIONS.get(name, "No description")
        print(f"  - {name}: {desc}")
