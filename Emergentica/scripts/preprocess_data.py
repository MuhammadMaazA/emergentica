"""
Data Preprocessing Script for Emergentica
=========================================

This script processes raw 911 call transcripts and enriches them with:
1. Severity labels (CRITICAL_EMERGENCY, STANDARD_ASSISTANCE, NON_EMERGENCY)
2. AI-generated summaries
3. Structured metadata

Uses Claude 3.5 Sonnet via AWS Bedrock to ensure high-quality ground truth labels
for benchmarking in Phase 4.

Usage:
    python scripts/preprocess_data.py --input ../processed/processed --output data/calls_master_labeled.jsonl
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import argparse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))  # Add scripts dir for holistic_ai_bedrock

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from holistic_ai_bedrock import get_chat_model  # Use official helper

# Load environment
load_dotenv()


class CallLabel(BaseModel):
    """Structured output for call labeling."""
    
    severity: str = Field(
        description="Severity level: CRITICAL_EMERGENCY, STANDARD_ASSISTANCE, or NON_EMERGENCY"
    )
    summary: str = Field(
        description="Brief 2-3 sentence summary of the call"
    )
    key_details: List[str] = Field(
        description="List of critical details (location, injuries, threat level, etc.)"
    )
    emotional_state: str = Field(
        description="Caller's emotional state: PANIC, DISTRESSED, CALM, or CONFUSED"
    )
    requires_immediate_action: bool = Field(
        description="Whether the situation requires immediate emergency response"
    )
    confidence: float = Field(
        description="Confidence score for the severity classification (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


def load_conversation(file_path: Path) -> Dict[str, Any]:
    """Load a conversation from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def conversation_to_text(messages: List[Dict[str, str]]) -> str:
    """Convert conversation messages to readable transcript."""
    transcript_parts = []
    
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        
        if role == 'assistant':
            speaker = "Dispatcher"
        elif role == 'user':
            speaker = "Caller"
        else:
            speaker = role.capitalize()
        
        transcript_parts.append(f"{speaker}: {content}")
    
    return "\n".join(transcript_parts)


def create_labeling_llm():
    """Create LLM using official Holistic AI Bedrock helper."""
    
    # Use the official helper function from tutorials
    # This handles all the API complexity correctly
    llm = get_chat_model(
        "claude-3-5-sonnet",
        temperature=0.3,  # Lower temperature for consistent labeling
        max_tokens=1000
    )
    
    return llm


def label_call(llm, transcript: str, file_name: str) -> CallLabel:
    """
    Label a single call using Claude 3.5 Sonnet.
    
    Args:
        llm: HolisticAIBedrockChat instance
        transcript: The call transcript  
        file_name: Name of the source file (for logging)
    
    Returns:
        CallLabel with severity, summary, and metadata
    """
    
    system_prompt = """You are an expert 911 call analyst. Analyze emergency call transcripts and provide structured assessments.

SEVERITY LEVELS:
- CRITICAL_EMERGENCY: Life-threatening (active shooters, severe injuries, fires, violent crimes in progress)
- STANDARD_ASSISTANCE: Urgent but not life-threatening (medical issues, property crimes, minor accidents)
- NON_EMERGENCY: Information requests, non-urgent issues, false alarms"""

    user_prompt = f"""Analyze this 911 call transcript and return ONLY valid JSON in this exact format:

{{
  "severity": "CRITICAL_EMERGENCY or STANDARD_ASSISTANCE or NON_EMERGENCY",
  "summary": "Brief 2-3 sentence summary",
  "key_details": ["detail1", "detail2", "detail3"],
  "emotional_state": "PANIC or CALM or DISTRESSED or ANGRY or CONFUSED",
  "requires_immediate_action": true,
  "confidence": 0.95
}}

TRANSCRIPT:
{transcript}

Return ONLY the JSON object, no markdown or explanation."""

    try:
        # Use LangChain message format
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Invoke the LLM
        response = llm.invoke(messages)
        response_text = response.content
        
        # Extract JSON from response text
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError(f"No JSON in response: {response_text[:200]}")
        
        # Parse JSON to pure Python dict
        data = json.loads(json_str)
        
        # Create CallLabel from primitives only
        label = CallLabel(
            severity=str(data.get("severity", "STANDARD_ASSISTANCE")),
            summary=str(data.get("summary", "No summary available")),
            key_details=[str(x) for x in data.get("key_details", [])],
            emotional_state=str(data.get("emotional_state", "UNKNOWN")),
            requires_immediate_action=bool(data.get("requires_immediate_action", False)),
            confidence=float(data.get("confidence", 0.5))
        )
        
        print(f"  ✓ Labeled: {file_name} → {label.severity} (confidence: {label.confidence:.2f})")
        return label
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        if "--debug" in sys.argv:
            print(f"  ✗ Error labeling {file_name}: {error_msg}")
            print(f"     Full traceback: {traceback.format_exc()}")
        else:
            print(f"  ✗ Error labeling {file_name}: {error_msg}")
        
        # Return default label on error
        return CallLabel(
            severity="STANDARD_ASSISTANCE",
            summary="Error processing call - manual review required",
            key_details=["Processing error occurred"],
            emotional_state="UNKNOWN",
            requires_immediate_action=False,
            confidence=0.0
        )


def process_dataset(input_dir: Path, output_file: Path, limit: int = None):
    """
    Process all JSON files in the input directory and create labeled dataset.
    
    Args:
        input_dir: Directory containing raw JSON call files
        output_file: Path to output JSONL file
        limit: Optional limit on number of files to process (for testing)
    """
    
    print("=" * 80)
    print("Emergentica Data Preprocessing")
    print("=" * 80)
    print(f"\nInput directory: {input_dir}")
    print(f"Output file: {output_file}")
    
    # Get all JSON files
    json_files = sorted(input_dir.glob("*.json"))
    
    if limit:
        json_files = json_files[:limit]
        print(f"⚠️  Processing limited to {limit} files for testing")
    
    print(f"\nFound {len(json_files)} files to process")
    
    # Create LLM using official helper
    print("\n📡 Initializing Claude 3.5 Sonnet...")
    try:
        llm = create_labeling_llm()
        print("✓ LLM initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize LLM: {e}")
        print("\nPlease check your .env file and ensure:")
        print("  - HOLISTIC_AI_TEAM_ID is set")
        print("  - HOLISTIC_AI_API_TOKEN is set")
        sys.exit(1)
    
    # Process each file
    print(f"\n🏷️  Labeling calls...")
    print("-" * 80)
    
    labeled_calls = []
    stats = {
        "CRITICAL_EMERGENCY": 0,
        "STANDARD_ASSISTANCE": 0,
        "NON_EMERGENCY": 0,
        "errors": 0
    }
    
    for i, file_path in enumerate(json_files, 1):
        print(f"\n[{i}/{len(json_files)}] Processing {file_path.name}...")
        
        try:
            # Load conversation
            data = load_conversation(file_path)
            messages = data.get("messages", [])
            
            if not messages:
                print(f"  ⚠️  No messages found in {file_path.name}")
                continue
            
            # Convert to transcript
            transcript = conversation_to_text(messages)
            
            # Label the call
            label = label_call(llm, transcript, file_path.name)
            
            # Create labeled entry with explicit dict conversion
            labeled_entry = {
                "file_id": file_path.stem,  # e.g., "text_0"
                "transcript": transcript,
                "messages": messages,
                "label": {
                    "severity": str(label.severity),
                    "summary": str(label.summary),
                    "key_details": list(label.key_details),
                    "emotional_state": str(label.emotional_state),
                    "requires_immediate_action": bool(label.requires_immediate_action),
                    "confidence": float(label.confidence)
                },
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "source_file": str(file_path.name),
                    "message_count": len(messages)
                }
            }
            
            labeled_calls.append(labeled_entry)
            
            # Update stats
            stats[label.severity] = stats.get(label.severity, 0) + 1
            
        except Exception as e:
            print(f"  ✗ Error processing {file_path.name}: {e}")
            stats["errors"] += 1
    
    # Save to JSONL
    print(f"\n💾 Saving labeled dataset...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Custom JSON encoder to handle any remaining circular refs
    def clean_for_json(obj):
        """Recursively clean object for JSON serialization."""
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [clean_for_json(item) for item in obj]
        else:
            # Convert unknown types to string
            return str(obj)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in labeled_calls:
            # Clean entry to remove any circular references
            clean_entry = clean_for_json(entry)
            f.write(json.dumps(clean_entry, ensure_ascii=False) + '\n')
    
    print(f"✓ Saved {len(labeled_calls)} labeled calls to {output_file}")
    
    # Print statistics
    print("\n" + "=" * 80)
    print("Processing Complete!")
    print("=" * 80)
    print(f"\nDataset Statistics:")
    print(f"  Total processed: {len(labeled_calls)}")
    print(f"  CRITICAL_EMERGENCY: {stats['CRITICAL_EMERGENCY']}")
    print(f"  STANDARD_ASSISTANCE: {stats['STANDARD_ASSISTANCE']}")
    print(f"  NON_EMERGENCY: {stats['NON_EMERGENCY']}")
    print(f"  Errors: {stats['errors']}")
    
    # Calculate distribution
    total = len(labeled_calls)
    if total > 0:
        print(f"\nDistribution:")
        for severity in ["CRITICAL_EMERGENCY", "STANDARD_ASSISTANCE", "NON_EMERGENCY"]:
            count = stats[severity]
            percentage = (count / total) * 100
            print(f"  {severity}: {percentage:.1f}%")
    
    print(f"\n✅ Dataset ready for benchmarking!")
    print(f"📊 Use this file in Phase 4 for performance evaluation")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Preprocess 911 call data for Emergentica")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../processed/processed"),
        help="Input directory containing JSON call files"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/calls_master_labeled.jsonl"),
        help="Output JSONL file for labeled dataset"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files to process (for testing)"
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not args.input.exists():
        print(f"✗ Input directory not found: {args.input}")
        print("\nPlease provide the correct path to the processed/ directory")
        sys.exit(1)
    
    # Process dataset
    process_dataset(args.input, args.output, args.limit)


if __name__ == "__main__":
    main()
