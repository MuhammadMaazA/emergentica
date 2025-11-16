"""
Benchmark Script for Emergentica
================================

This script evaluates the system's performance on the labeled dataset:

Metrics Calculated:
1. Routing Accuracy: % of calls correctly classified
2. Average Routing Latency: Time to classify calls
3. Average Critical Triage Time: End-to-end time for critical calls
4. Cost-Efficiency: Savings vs using Sonnet for all calls

This provides the data-backed evidence needed to win Track A.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import statistics

from agents.orchestrator import get_orchestrator
from schemas import BenchmarkResult, BenchmarkReport
from config import config


# ============================================
# Cost Models (per 1M tokens)
# ============================================

COST_PER_MILLION_TOKENS = {
    "haiku_input": 0.80,
    "haiku_output": 4.00,
    "sonnet_input": 3.00,
    "sonnet_output": 15.00,
    "llama_input": 0.72,
    "llama_output": 0.88
}

# Estimated token usage per call (conservative estimates)
TOKENS_PER_CALL = {
    "router": {"input": 500, "output": 100},  # Haiku
    "triage": {"input": 1000, "output": 800},  # Sonnet
    "info": {"input": 600, "output": 300}  # Llama
}


def estimate_cost(route: str) -> float:
    """
    Estimate cost for processing a call based on route.
    
    Args:
        route: Route taken (e.g., "router → triage_agent")
    
    Returns:
        Estimated cost in USD
    """
    
    cost = 0.0
    
    # Router always runs (Haiku)
    router_tokens = TOKENS_PER_CALL["router"]
    cost += (router_tokens["input"] / 1_000_000) * COST_PER_MILLION_TOKENS["haiku_input"]
    cost += (router_tokens["output"] / 1_000_000) * COST_PER_MILLION_TOKENS["haiku_output"]
    
    # Add downstream agent cost
    if "triage" in route.lower():
        # Triage uses Haiku for emotion + Sonnet for main analysis
        # Haiku for emotion
        emotion_tokens = {"input": 400, "output": 100}
        cost += (emotion_tokens["input"] / 1_000_000) * COST_PER_MILLION_TOKENS["haiku_input"]
        cost += (emotion_tokens["output"] / 1_000_000) * COST_PER_MILLION_TOKENS["haiku_output"]
        
        # Sonnet for main triage
        triage_tokens = TOKENS_PER_CALL["triage"]
        cost += (triage_tokens["input"] / 1_000_000) * COST_PER_MILLION_TOKENS["sonnet_input"]
        cost += (triage_tokens["output"] / 1_000_000) * COST_PER_MILLION_TOKENS["sonnet_output"]
    
    elif "info" in route.lower():
        # Info uses Llama
        info_tokens = TOKENS_PER_CALL["info"]
        cost += (info_tokens["input"] / 1_000_000) * COST_PER_MILLION_TOKENS["llama_input"]
        cost += (info_tokens["output"] / 1_000_000) * COST_PER_MILLION_TOKENS["llama_output"]
    
    return cost


def estimate_sonnet_only_cost() -> float:
    """Estimate cost if using Sonnet for all calls."""
    
    tokens = {"input": 1200, "output": 800}
    cost = (tokens["input"] / 1_000_000) * COST_PER_MILLION_TOKENS["sonnet_input"]
    cost += (tokens["output"] / 1_000_000) * COST_PER_MILLION_TOKENS["sonnet_output"]
    
    return cost


# ============================================
# Benchmark Functions
# ============================================

def load_labeled_dataset(file_path: Path) -> List[Dict[str, Any]]:
    """Load the labeled JSONL dataset."""
    
    dataset = []
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))
    
    return dataset


def run_benchmark(
    dataset_path: Path,
    output_path: Path,
    limit: int = None
) -> BenchmarkReport:
    """
    Run complete benchmark on labeled dataset.
    
    Args:
        dataset_path: Path to calls_master_labeled.jsonl
        output_path: Where to save results
        limit: Optional limit on number of calls to test
    
    Returns:
        BenchmarkReport with all metrics
    """
    
    print("=" * 80)
    print("🎯 EMERGENTICA BENCHMARK - TRACK A PERFORMANCE EVALUATION")
    print("=" * 80)
    
    # Load dataset
    print(f"\n📂 Loading dataset from: {dataset_path}")
    dataset = load_labeled_dataset(dataset_path)
    
    if limit:
        dataset = dataset[:limit]
        print(f"⚠️  Limited to {limit} calls for testing")
    
    print(f"✓ Loaded {len(dataset)} labeled calls")
    
    # Initialize orchestrator
    print("\n🤖 Initializing orchestrator...")
    orchestrator = get_orchestrator()
    print("✓ Orchestrator ready")
    
    # Run benchmark
    print(f"\n🏃 Processing {len(dataset)} calls...")
    print("-" * 80)
    
    results = []
    model_counts = {"haiku": 0, "sonnet": 0, "llama": 0}
    
    for i, call in enumerate(dataset, 1):
        print(f"\n[{i}/{len(dataset)}] Processing {call['file_id']}...")
        
        # Extract ground truth
        ground_truth = call['label']['severity']
        transcript = call['transcript']
        
        # Time the processing
        start_time = time.time()
        
        try:
            # Process call
            result = orchestrator.process_call(
                call_id=call['file_id'],
                transcript=transcript
            )
            
            end_time = time.time()
            routing_latency = int((end_time - start_time) * 1000)
            
            # Extract prediction
            if result['classification']:
                predicted = result['classification'].severity
                confidence = result['classification'].confidence
            else:
                predicted = "UNKNOWN"
                confidence = 0.0
            
            # Check correctness
            correct = (predicted == ground_truth)
            
            # Calculate triage time if critical
            triage_time = None
            if predicted == "CRITICAL_EMERGENCY" and result['critical_report']:
                triage_time = result['critical_report'].processing_time_ms
            
            # Estimate cost
            route = result.get('route_taken', 'unknown')
            cost = estimate_cost(route)
            
            # Track model usage
            model_counts["haiku"] += 1  # Router always uses Haiku
            if "triage" in route.lower():
                model_counts["haiku"] += 1  # Emotion analysis
                model_counts["sonnet"] += 1
            elif "info" in route.lower():
                model_counts["llama"] += 1
            
            # Create result
            benchmark_result = BenchmarkResult(
                file_id=call['file_id'],
                ground_truth_severity=ground_truth,
                predicted_severity=predicted,
                correct=correct,
                routing_latency_ms=routing_latency,
                triage_latency_ms=triage_time,
                model_used=route,
                cost_usd=cost
            )
            
            results.append(benchmark_result)
            
            # Print result
            status = "✓" if correct else "✗"
            print(f"   {status} GT: {ground_truth} → Pred: {predicted}")
            print(f"   Latency: {routing_latency}ms | Cost: ${cost:.6f}")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            # Add failed result
            results.append(BenchmarkResult(
                file_id=call['file_id'],
                ground_truth_severity=ground_truth,
                predicted_severity="ERROR",
                correct=False,
                routing_latency_ms=0,
                model_used="error",
                cost_usd=0.0
            ))
    
    # Calculate metrics
    print("\n\n" + "=" * 80)
    print("📊 CALCULATING METRICS")
    print("=" * 80)
    
    # Overall accuracy
    correct_count = sum(1 for r in results if r.correct)
    total_count = len(results)
    overall_accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n✓ Routing Accuracy: {overall_accuracy:.2f}% ({correct_count}/{total_count})")
    
    # Per-category accuracy
    severities = ["CRITICAL_EMERGENCY", "STANDARD_ASSISTANCE", "NON_EMERGENCY"]
    category_accuracies = {}
    
    for severity in severities:
        severity_results = [r for r in results if r.ground_truth_severity == severity]
        if severity_results:
            correct = sum(1 for r in severity_results if r.correct)
            accuracy = (correct / len(severity_results)) * 100
            category_accuracies[severity] = accuracy
            print(f"✓ {severity}: {accuracy:.2f}% ({correct}/{len(severity_results)})")
        else:
            category_accuracies[severity] = 0.0
    
    # Latency metrics
    routing_latencies = [r.routing_latency_ms for r in results if r.routing_latency_ms > 0]
    avg_routing_latency = statistics.mean(routing_latencies) if routing_latencies else 0
    p95_routing_latency = statistics.quantiles(routing_latencies, n=20)[18] if len(routing_latencies) > 20 else max(routing_latencies, default=0)
    
    print(f"\n✓ Average Routing Latency: {avg_routing_latency:.0f}ms")
    print(f"✓ P95 Routing Latency: {p95_routing_latency:.0f}ms")
    
    # Critical triage time
    triage_times = [r.triage_latency_ms for r in results if r.triage_latency_ms]
    avg_triage_time = statistics.mean(triage_times) if triage_times else 0
    p95_triage_time = statistics.quantiles(triage_times, n=20)[18] if len(triage_times) > 20 else max(triage_times, default=0)
    
    if triage_times:
        print(f"✓ Average Critical Triage Time: {avg_triage_time:.0f}ms")
        print(f"✓ P95 Critical Triage Time: {p95_triage_time:.0f}ms")
    
    # Cost analysis
    total_cost = sum(r.cost_usd for r in results)
    avg_cost = total_cost / total_count if total_count > 0 else 0
    
    # Compare to Sonnet-only approach
    sonnet_only_cost = estimate_sonnet_only_cost() * total_count
    cost_savings_pct = ((sonnet_only_cost - total_cost) / sonnet_only_cost * 100) if sonnet_only_cost > 0 else 0
    
    print(f"\n✓ Total Cost (Multi-Agent): ${total_cost:.4f}")
    print(f"✓ Average Cost per Call: ${avg_cost:.6f}")
    print(f"✓ Projected Cost (Sonnet-Only): ${sonnet_only_cost:.4f}")
    print(f"✓ Cost Savings: {cost_savings_pct:.2f}%")
    
    # Model usage
    print(f"\n✓ Model Usage:")
    print(f"   Haiku calls: {model_counts['haiku']}")
    print(f"   Sonnet calls: {model_counts['sonnet']}")
    print(f"   Llama calls: {model_counts['llama']}")
    
    # Create report
    report = BenchmarkReport(
        total_calls=total_count,
        correct_predictions=correct_count,
        routing_accuracy=overall_accuracy,
        critical_accuracy=category_accuracies.get("CRITICAL_EMERGENCY", 0),
        standard_accuracy=category_accuracies.get("STANDARD_ASSISTANCE", 0),
        non_emergency_accuracy=category_accuracies.get("NON_EMERGENCY", 0),
        avg_routing_latency_ms=avg_routing_latency,
        avg_critical_triage_time_ms=avg_triage_time,
        p95_routing_latency_ms=p95_routing_latency,
        p95_critical_triage_time_ms=p95_triage_time,
        total_cost_usd=total_cost,
        avg_cost_per_call_usd=avg_cost,
        cost_savings_vs_sonnet_only=cost_savings_pct,
        haiku_calls=model_counts["haiku"],
        sonnet_calls=model_counts["sonnet"],
        llama_calls=model_counts["llama"],
        results=results,
        test_date=datetime.now(),
        dataset_file=str(dataset_path)
    )
    
    # Save report
    print(f"\n💾 Saving benchmark report to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report.model_dump(), f, indent=2, default=str)
    
    print("✓ Report saved")
    
    # Print final summary
    print("\n\n" + "=" * 80)
    print("🏆 BENCHMARK COMPLETE - TRACK A WINNING METRICS")
    print("=" * 80)
    print(f"\n📈 ROUTING ACCURACY: {overall_accuracy:.2f}%")
    print(f"⚡ AVERAGE ROUTING LATENCY: {avg_routing_latency:.0f}ms")
    print(f"🚨 AVERAGE CRITICAL TRIAGE TIME: {avg_triage_time:.0f}ms")
    print(f"💰 COST SAVINGS VS SONNET-ONLY: {cost_savings_pct:.2f}%")
    print("\n" + "=" * 80)
    
    return report


# ============================================
# Main Entry Point
# ============================================

def main():
    """Run benchmark from command line."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Emergentica Performance")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/calls_master_labeled.jsonl"),
        help="Path to labeled dataset"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmark_results.json"),
        help="Where to save results"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of calls to test"
    )
    
    args = parser.parse_args()
    
    # Check dataset exists
    if not args.dataset.exists():
        print(f"❌ Dataset not found: {args.dataset}")
        print("\nPlease run the preprocessing script first:")
        print("  python scripts/preprocess_data.py")
        return
    
    # Run benchmark
    run_benchmark(args.dataset, args.output, args.limit)


if __name__ == "__main__":
    main()
