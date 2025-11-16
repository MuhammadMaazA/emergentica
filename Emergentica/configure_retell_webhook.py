"""
Configure Retell AI Agent Webhook via API
==========================================

Use this script if you can't find webhook settings in the Retell dashboard UI.
This will update your existing agent with the webhook URL.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RETELL_API_KEY = os.getenv("RETELL_API_KEY")
RETELL_AGENT_ID = os.getenv("RETELL_AGENT_ID")

def update_agent_webhook(ngrok_url):
    """
    Update Retell agent with webhook URL.
    
    Args:
        ngrok_url: Your ngrok HTTPS URL (e.g., https://abc123.ngrok-free.app)
    """
    
    # Construct webhook URL
    webhook_url = f"{ngrok_url}/webhook/retell/live"
    
    # API endpoint
    url = f"https://api.retellai.com/update-agent/{RETELL_AGENT_ID}"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Payload
    payload = {
        "response_engine": {
            "type": "retell-llm",
            "llm_websocket_url": webhook_url
        },
        "voice_id": "11labs-Adrian",  # Professional male voice
        "voice_temperature": 1.0,
        "voice_speed": 1.0,
        "responsiveness": 1.0,
        "interruption_sensitivity": 0.5,
        "enable_backchannel": True,
        "backchannel_frequency": 0.9,
        "ambient_sound": "office",
        "language": "en-US",
        "boosted_keywords": ["emergency", "police", "ambulance", "fire", "shooting", "accident"],
        "opt_out_sensitive_data_storage": False
    }
    
    print("=" * 80)
    print("UPDATING RETELL AGENT WEBHOOK")
    print("=" * 80)
    print(f"Agent ID: {RETELL_AGENT_ID}")
    print(f"Webhook URL: {webhook_url}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        print("✅ SUCCESS! Agent webhook updated.")
        print(f"\nResponse: {response.json()}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def get_agent_info():
    """Get current agent configuration."""
    
    url = f"https://api.retellai.com/get-agent/{RETELL_AGENT_ID}"
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}"
    }
    
    print("=" * 80)
    print("CURRENT AGENT CONFIGURATION")
    print("=" * 80)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        import json
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    print("\n🎙️ RETELL AI AGENT WEBHOOK CONFIGURATOR\n")
    
    # Check if credentials are set
    if not RETELL_API_KEY or not RETELL_AGENT_ID:
        print("❌ ERROR: Missing RETELL_API_KEY or RETELL_AGENT_ID in .env file")
        exit(1)
    
    # Menu
    print("What would you like to do?")
    print("1. View current agent configuration")
    print("2. Update webhook URL")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        get_agent_info()
    
    elif choice == "2":
        ngrok_url = input("\nEnter your ngrok HTTPS URL (e.g., https://abc123.ngrok-free.app): ").strip()
        
        if not ngrok_url.startswith("https://"):
            print("❌ ERROR: URL must start with https://")
            exit(1)
        
        # Remove trailing slash
        ngrok_url = ngrok_url.rstrip("/")
        
        # Confirm
        print(f"\n⚠️  This will update agent {RETELL_AGENT_ID}")
        print(f"   Webhook URL: {ngrok_url}/webhook/retell/live")
        confirm = input("   Continue? (y/n): ").strip().lower()
        
        if confirm == "y":
            update_agent_webhook(ngrok_url)
        else:
            print("Cancelled.")
    
    else:
        print("Exiting...")
