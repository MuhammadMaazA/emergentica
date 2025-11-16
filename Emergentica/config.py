"""
Configuration loader for Emergentica system.
Loads and validates all required environment variables.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration from environment variables."""
    
    # Holistic AI / AWS Bedrock
    HOLISTIC_AI_TEAM_ID: str = os.getenv("HOLISTIC_AI_TEAM_ID", "")
    HOLISTIC_AI_API_TOKEN: str = os.getenv("HOLISTIC_AI_API_TOKEN", "")
    
    # LangSmith
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "emergentica-hackathon")
    LANGSMITH_TRACING: str = os.getenv("LANGSMITH_TRACING", "true")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Retell AI
    RETELL_API_KEY: str = os.getenv("RETELL_API_KEY", "")
    RETELL_AGENT_ID: str = os.getenv("RETELL_AGENT_ID", "")
    RETELL_PHONE_NUMBER: str = os.getenv("RETELL_PHONE_NUMBER", "")  # Your Retell phone number for outbound calls
    
    # Geocoding
    GEOCODE_API_KEY: str = os.getenv("GEOCODE_API_KEY", "")
    
    # Valyu (optional)
    VALYU_API_KEY: Optional[str] = os.getenv("VALYU_API_KEY")
    
    # Server settings
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    @classmethod
    def validate_required(cls) -> bool:
        """Validate that all required environment variables are set."""
        required = [
            ("HOLISTIC_AI_TEAM_ID", cls.HOLISTIC_AI_TEAM_ID),
            ("HOLISTIC_AI_API_TOKEN", cls.HOLISTIC_AI_API_TOKEN),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            print(f"⚠️  Missing required environment variables: {', '.join(missing)}")
            print("Please update your .env file with the required values.")
            return False
        
        return True
    
    @classmethod
    def validate_voice_pipeline(cls) -> bool:
        """Validate voice pipeline configuration (Twilio + Retell)."""
        required = [
            ("TWILIO_ACCOUNT_SID", cls.TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", cls.TWILIO_AUTH_TOKEN),
            ("TWILIO_PHONE_NUMBER", cls.TWILIO_PHONE_NUMBER),
            ("RETELL_API_KEY", cls.RETELL_API_KEY),
            ("RETELL_AGENT_ID", cls.RETELL_AGENT_ID),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            print(f"⚠️  Voice pipeline not configured. Missing: {', '.join(missing)}")
            return False
        
        return True


# Create singleton instance
config = Config()


if __name__ == "__main__":
    print("=" * 60)
    print("Emergentica Configuration Validation")
    print("=" * 60)
    
    print("\n✓ Core API (Holistic AI Bedrock):")
    if config.validate_required():
        print(f"  Team ID: {config.HOLISTIC_AI_TEAM_ID}")
        print(f"  Token: {'*' * 20}...{config.HOLISTIC_AI_API_TOKEN[-4:]}")
    
    print("\n✓ LangSmith (Observability):")
    if config.LANGSMITH_API_KEY:
        print(f"  Project: {config.LANGSMITH_PROJECT}")
        print(f"  Tracing: {config.LANGSMITH_TRACING}")
    else:
        print("  ⚠️  Not configured (optional)")
    
    print("\n✓ Voice Pipeline:")
    if config.validate_voice_pipeline():
        print(f"  Twilio Number: {config.TWILIO_PHONE_NUMBER}")
        print(f"  Retell Agent: {config.RETELL_AGENT_ID}")
    else:
        print("  ⚠️  Not configured (required for Phase 2)")
    
    print("\n✓ Tools:")
    if config.GEOCODE_API_KEY:
        print(f"  Geocoding: Configured")
    else:
        print("  Geocoding: ⚠️  Not configured")
    
    if config.VALYU_API_KEY:
        print(f"  Valyu: Configured")
    else:
        print("  Valyu: ⚠️  Not configured (optional)")
    
    print("\n" + "=" * 60)
