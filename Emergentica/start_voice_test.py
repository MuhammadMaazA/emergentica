"""
Quick Start Script for Live Voice Testing
==========================================

This script helps you start all required services for live voice testing:
1. Validates environment variables
2. Provides setup instructions
3. Generates ready-to-use commands

Run: py start_voice_test.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import webbrowser

# Load environment variables
load_dotenv()

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_env_var(name, required=True):
    """Check if environment variable is set."""
    value = os.getenv(name)
    if value:
        # Mask sensitive values
        if 'KEY' in name or 'TOKEN' in name or 'SECRET' in name:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print_success(f"{name}: {masked}")
        else:
            print_success(f"{name}: {value}")
        return True
    else:
        if required:
            print_error(f"{name}: NOT SET (REQUIRED)")
        else:
            print_warning(f"{name}: NOT SET (OPTIONAL)")
        return not required

def validate_environment():
    """Validate all required environment variables."""
    print_header("VALIDATING ENVIRONMENT")
    
    all_valid = True
    
    print(f"\n{Colors.BOLD}Holistic AI / AWS Bedrock:{Colors.END}")
    all_valid &= check_env_var("HOLISTIC_AI_TEAM_ID")
    all_valid &= check_env_var("HOLISTIC_AI_API_TOKEN")
    
    print(f"\n{Colors.BOLD}Twilio:{Colors.END}")
    all_valid &= check_env_var("TWILIO_ACCOUNT_SID")
    all_valid &= check_env_var("TWILIO_AUTH_TOKEN")
    all_valid &= check_env_var("TWILIO_PHONE_NUMBER")
    
    print(f"\n{Colors.BOLD}Retell AI:{Colors.END}")
    all_valid &= check_env_var("RETELL_API_KEY")
    all_valid &= check_env_var("RETELL_AGENT_ID")
    
    print(f"\n{Colors.BOLD}LangSmith (Observability):{Colors.END}")
    check_env_var("LANGSMITH_API_KEY", required=False)
    
    print(f"\n{Colors.BOLD}Geocoding API:{Colors.END}")
    check_env_var("GEOCODE_API_KEY", required=False)
    
    return all_valid

def check_ngrok():
    """Check if ngrok is installed."""
    print_header("CHECKING NGROK")
    
    try:
        import subprocess
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"ngrok is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print_error("ngrok is NOT installed")
    print_info("Install from: https://ngrok.com/download")
    print_info("Or with Chocolatey: choco install ngrok")
    return False

def generate_commands():
    """Generate ready-to-use commands."""
    print_header("COMMANDS TO RUN")
    
    print(f"{Colors.BOLD}Open 3 separate PowerShell terminals and run:{Colors.END}\n")
    
    print(f"{Colors.CYAN}TERMINAL 1 - FastAPI Server:{Colors.END}")
    print(f"{Colors.YELLOW}cd \"{Path.cwd()}\"{Colors.END}")
    print(f"{Colors.YELLOW}.\\venv\\Scripts\\activate{Colors.END}")
    print(f"{Colors.YELLOW}py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000{Colors.END}\n")
    
    print(f"{Colors.CYAN}TERMINAL 2 - ngrok (Expose to Internet):{Colors.END}")
    print(f"{Colors.YELLOW}ngrok http 8000{Colors.END}")
    print_info("Copy the HTTPS forwarding URL (e.g., https://abcd-1234.ngrok-free.app)")
    print("")
    
    print(f"{Colors.CYAN}TERMINAL 3 - Streamlit Dashboard:{Colors.END}")
    print(f"{Colors.YELLOW}cd \"{Path.cwd()}\"{Colors.END}")
    print(f"{Colors.YELLOW}.\\venv\\Scripts\\activate{Colors.END}")
    print(f"{Colors.YELLOW}streamlit run dashboard.py{Colors.END}\n")

def display_setup_instructions():
    """Display Retell and Twilio setup instructions."""
    print_header("RETELL AI CONFIGURATION")
    
    agent_id = os.getenv("RETELL_AGENT_ID", "YOUR_AGENT_ID")
    
    print(f"{Colors.BOLD}After starting ngrok, configure Retell AI agent:{Colors.END}\n")
    print(f"1. Go to: {Colors.CYAN}https://app.retellai.com/dashboard{Colors.END}")
    print(f"2. Find agent: {Colors.YELLOW}{agent_id}{Colors.END}")
    print(f"3. Set webhook URL to: {Colors.GREEN}https://YOUR-NGROK-URL/webhook/retell/live{Colors.END}")
    print(f"4. Set webhook method to: {Colors.GREEN}POST{Colors.END}")
    print(f"5. Save the agent\n")
    
    print_header("TWILIO CONFIGURATION")
    
    phone = os.getenv("TWILIO_PHONE_NUMBER", "YOUR_PHONE_NUMBER")
    
    print(f"{Colors.BOLD}Configure Twilio to forward calls to Retell AI:{Colors.END}\n")
    print(f"1. Go to: {Colors.CYAN}https://console.twilio.com/us1/develop/phone-numbers/manage/incoming{Colors.END}")
    print(f"2. Click your number: {Colors.YELLOW}{phone}{Colors.END}")
    print(f"3. Under 'A CALL COMES IN':")
    print(f"   - Set to: {Colors.GREEN}Webhook{Colors.END}")
    print(f"   - URL: {Colors.GREEN}https://api.retellai.com/v1/call/twilio{Colors.END}")
    print(f"   - Method: {Colors.GREEN}POST{Colors.END}")
    print(f"4. Save the configuration\n")

def display_test_scenarios():
    """Display test scenarios."""
    print_header("TEST SCENARIOS")
    
    phone = os.getenv("TWILIO_PHONE_NUMBER", "YOUR_PHONE_NUMBER")
    
    print(f"{Colors.BOLD}Call: {Colors.CYAN}{phone}{Colors.END}\n")
    
    print(f"{Colors.GREEN}Test 1 - Non-Emergency:{Colors.END}")
    print(f"Say: \"Hi, I need to report a noise complaint at 123 Main Street.\"\n")
    
    print(f"{Colors.YELLOW}Test 2 - Standard Assistance:{Colors.END}")
    print(f"Say: \"There's a car accident on Highway 101. No injuries.\"\n")
    
    print(f"{Colors.RED}Test 3 - Critical Emergency:{Colors.END}")
    print(f"Say: \"There's a shooting at West High School!\"\n")

def open_documentation():
    """Ask if user wants to open full documentation."""
    print_header("DOCUMENTATION")
    
    guide_path = Path("VOICE_TESTING_GUIDE.md")
    
    if guide_path.exists():
        print(f"Full testing guide available at: {Colors.CYAN}{guide_path.absolute()}{Colors.END}\n")
        response = input(f"Open full guide in browser? (y/n): ").lower().strip()
        if response == 'y':
            webbrowser.open(guide_path.absolute().as_uri())
            print_success("Guide opened in browser")
    else:
        print_warning("Full guide not found. Run setup first.")

def main():
    """Main execution."""
    print_header("🎙️ EMERGENTICA - LIVE VOICE TESTING SETUP")
    
    print(f"{Colors.BOLD}This script will help you set up live voice testing.{Colors.END}\n")
    
    # Validate environment
    env_valid = validate_environment()
    
    if not env_valid:
        print_error("\nSome required environment variables are missing!")
        print_info("Check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    # Check ngrok
    ngrok_installed = check_ngrok()
    
    # Generate commands
    generate_commands()
    
    # Setup instructions
    display_setup_instructions()
    
    # Test scenarios
    display_test_scenarios()
    
    # Quick reference
    print_header("QUICK REFERENCE")
    print(f"FastAPI:          {Colors.CYAN}http://localhost:8000{Colors.END}")
    print(f"API Docs:         {Colors.CYAN}http://localhost:8000/docs{Colors.END}")
    print(f"Health Check:     {Colors.CYAN}http://localhost:8000/health{Colors.END}")
    print(f"Dashboard:        {Colors.CYAN}http://localhost:8501{Colors.END}")
    print(f"ngrok Inspector:  {Colors.CYAN}http://localhost:4040{Colors.END}")
    print(f"Twilio Console:   {Colors.CYAN}https://console.twilio.com{Colors.END}")
    print(f"Retell Dashboard: {Colors.CYAN}https://app.retellai.com{Colors.END}\n")
    
    # Open documentation
    open_documentation()
    
    print_header("READY TO START!")
    print(f"\n{Colors.BOLD}{Colors.GREEN}Follow the commands above to start testing!{Colors.END}\n")
    
    if not ngrok_installed:
        print_warning("Remember to install ngrok before proceeding!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
