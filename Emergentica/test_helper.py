"""
Test Helper Script for Emergentica
==================================

Quick testing utilities to validate the system end-to-end.
"""

import json
import requests
from pathlib import Path
from datetime import datetime


# Sample test transcripts
TEST_TRANSCRIPTS = {
    "critical": """Dispatcher: 9-1-1, what's your emergency?
Caller: I'm at West High School. There's a guy with a gun.
Dispatcher: Which high school?
Caller: West High.
Dispatcher: Okay, we have the police dispatched. Can you give me a description?
Caller: I don't know. The guy is just running through the halls.
Dispatcher: Can you go somewhere where you're safe?
Caller: I'm locked in a room on the third floor.
Caller: Oh, my God. I hear shots!""",

    "standard": """Dispatcher: 9-1-1, what's your emergency?
Caller: Yes, I'd like to report a car accident at the intersection of Main and 5th.
Dispatcher: Is anyone injured?
Caller: No, it's just a fender bender. Both cars are drivable but we need an officer for insurance.
Dispatcher: Okay, I'll send an officer to file a report.
Caller: Thank you.""",

    "non_emergency": """Dispatcher: 9-1-1, what's your emergency?
Caller: Hi, there's a car parked in front of my driveway for the past two days.
Dispatcher: Is it blocking you from getting out?
Caller: No, but it's very close and it's been there a while.
Dispatcher: I can send an officer to check on it when one is available.
Caller: Okay, thank you."""
}


def test_api_health(base_url: str = "http://localhost:8000"):
    """Test API health endpoint."""
    
    print("\n" + "=" * 60)
    print("🏥 Testing API Health")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ API Status: {data.get('status')}")
        print(f"   Timestamp: {data.get('timestamp')}")
        return True
    
    except requests.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Start it with: python main.py")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_api_status(base_url: str = "http://localhost:8000"):
    """Test API status endpoint."""
    
    print("\n" + "=" * 60)
    print("📊 Testing API Status")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status: {data.get('status')}")
        print(f"   Orchestrator Available: {data.get('orchestrator_available')}")
        
        print("\n   Configuration:")
        config = data.get('configuration', {})
        for key, value in config.items():
            status = "✓" if value else "✗"
            print(f"   {status} {key}: {value}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def send_test_call(
    transcript_type: str = "critical",
    endpoint: str = "live",
    base_url: str = "http://localhost:8000"
):
    """
    Send a test call to the API.
    
    Args:
        transcript_type: Type of call (critical, standard, non_emergency)
        endpoint: Which endpoint to use (mock, live)
        base_url: API base URL
    """
    
    print("\n" + "=" * 60)
    print(f"📞 Sending Test Call: {transcript_type.upper()}")
    print("=" * 60)
    
    # Get transcript
    transcript = TEST_TRANSCRIPTS.get(transcript_type)
    if not transcript:
        print(f"❌ Unknown transcript type: {transcript_type}")
        return False
    
    # Prepare payload
    payload = {
        "call_id": f"TEST_{transcript_type.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "transcript": transcript,
        "duration": 30.0,
        "event_type": "transcript_update"
    }
    
    # Determine endpoint
    if endpoint == "live":
        url = f"{base_url}/webhook/retell/live"
    else:
        url = f"{base_url}/webhook/retell"
    
    print(f"\n📤 Sending to: {url}")
    print(f"   Call ID: {payload['call_id']}")
    print(f"   Transcript length: {len(transcript)} chars")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✅ Call processed successfully!")
        print(f"   Response: {data.get('response_text', 'N/A')[:100]}...")
        print(f"\n💾 Check data/latest_call.json for full results")
        print(f"🖥️  View on dashboard: http://localhost:8501")
        
        return True
    
    except requests.Timeout:
        print("❌ Request timed out (may still be processing)")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_latest_call():
    """Check the latest call data file."""
    
    print("\n" + "=" * 60)
    print("📂 Checking Latest Call Data")
    print("=" * 60)
    
    data_file = Path("data/latest_call.json")
    
    if not data_file.exists():
        print("⚠️  No call data found yet")
        print("   Send a test call first")
        return False
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Latest Call Data Found")
        print(f"   Call ID: {data.get('call_id')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Timestamp: {data.get('timestamp')}")
        
        if data.get('classification'):
            print(f"\n   Classification:")
            print(f"   Severity: {data['classification'].get('severity')}")
            print(f"   Confidence: {data['classification'].get('confidence', 0):.2f}")
        
        if data.get('processing_time_ms'):
            print(f"\n   Processing Time: {data['processing_time_ms']}ms")
        
        return True
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def run_full_test():
    """Run complete end-to-end test."""
    
    print("\n" + "=" * 80)
    print("🚀 EMERGENTICA FULL SYSTEM TEST")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # 1. Check API health
    if not test_api_health(base_url):
        print("\n❌ API not running. Start with: python main.py")
        return
    
    # 2. Check API status
    test_api_status(base_url)
    
    # 3. Send test calls
    print("\n\n" + "=" * 80)
    print("📞 SENDING TEST CALLS")
    print("=" * 80)
    
    for call_type in ["critical", "standard", "non_emergency"]:
        send_test_call(call_type, endpoint="live", base_url=base_url)
        print("\n" + "-" * 60)
    
    # 4. Check latest result
    check_latest_call()
    
    # Final summary
    print("\n\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Open dashboard: http://localhost:8501")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Check data/latest_call.json for details")
    print("4. Run benchmark: python benchmark.py --limit 10")
    print("\n" + "=" * 80)


# ============================================
# CLI Interface
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Emergentica Test Helper")
    parser.add_argument(
        "--action",
        choices=["health", "status", "call", "check", "full"],
        default="full",
        help="Action to perform"
    )
    parser.add_argument(
        "--type",
        choices=["critical", "standard", "non_emergency"],
        default="critical",
        help="Type of test call to send"
    )
    parser.add_argument(
        "--endpoint",
        choices=["mock", "live"],
        default="live",
        help="Which webhook endpoint to use"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL"
    )
    
    args = parser.parse_args()
    
    if args.action == "health":
        test_api_health(args.url)
    
    elif args.action == "status":
        test_api_status(args.url)
    
    elif args.action == "call":
        send_test_call(args.type, args.endpoint, args.url)
    
    elif args.action == "check":
        check_latest_call()
    
    elif args.action == "full":
        run_full_test()
