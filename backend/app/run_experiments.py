#!/usr/bin/env python3
"""
Opik Experiment Runner for MileSync.

This script runs evaluation experiments using Opik to:
- Test coaching response quality across different scenarios
- Benchmark goal extraction accuracy
- Track model performance over time
- Compare different prompt versions

Usage:
    python -m app.run_experiments --experiment coaching
    python -m app.run_experiments --experiment extraction
    python -m app.run_experiments --all
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.evaluation_datasets import (
    get_coaching_dataset,
    get_goal_extraction_dataset,
    get_frustration_dataset,
    get_smart_alignment_dataset,
)


def check_opik_configured() -> bool:
    """Check if Opik is configured."""
    if not settings.OPIK_API_KEY:
        print("❌ OPIK_API_KEY not configured. Set it in your .env file.")
        print("   Get your API key from: https://www.comet.com/opik")
        return False
    return True


def check_openai_configured() -> bool:
    """Check if OpenAI is configured."""
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not configured. Set it in your .env file.")
        return False
    return True


async def run_coaching_experiment() -> Dict[str, Any]:
    """
    Run coaching quality evaluation experiment.
    
    Tests AI coaching responses against expected quality criteria.
    """
    print("\n🎯 Running Coaching Quality Experiment...")
    print("=" * 50)
    
    from app.services.ai_service import generate_chat_response
    from app.services.opik_service import GoalCoachingQualityMetric
    
    dataset = get_coaching_dataset()
    metric = GoalCoachingQualityMetric()
    results = []
    
    for i, item in enumerate(dataset):
        print(f"\n[{i+1}/{len(dataset)}] Testing: {item['id']}")
        print(f"   User: {item['input']['user_message'][:50]}...")
        
        try:
            # Generate AI response
            messages = [{"role": "user", "content": item['input']['user_message']}]
            ai_response = await generate_chat_response(messages)
            
            # Evaluate response
            evaluation = metric.score(
                user_input=item['input']['user_message'],
                ai_response=ai_response
            )
            
            # Check if score is within expected range
            expected_range = item['metadata'].get('expected_score_range', [0, 1])
            in_range = expected_range[0] <= evaluation['score'] <= expected_range[1]
            
            result = {
                "id": item['id'],
                "category": item['metadata']['category'],
                "difficulty": item['metadata']['difficulty'],
                "score": evaluation['score'],
                "reason": evaluation['reason'],
                "in_expected_range": in_range,
                "response_preview": ai_response[:100] + "..."
            }
            results.append(result)
            
            status = "✅" if in_range else "⚠️"
            print(f"   {status} Score: {evaluation['score']:.2f} (expected: {expected_range})")
            print(f"   Reason: {evaluation['reason'][:60]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                "id": item['id'],
                "error": str(e)
            })
    
    # Calculate summary
    valid_results = [r for r in results if 'score' in r]
    avg_score = sum(r['score'] for r in valid_results) / len(valid_results) if valid_results else 0
    pass_rate = sum(1 for r in valid_results if r['in_expected_range']) / len(valid_results) if valid_results else 0
    
    summary = {
        "experiment": "coaching_quality",
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": len(dataset),
        "successful_tests": len(valid_results),
        "average_score": round(avg_score, 3),
        "pass_rate": round(pass_rate, 3),
        "results": results
    }
    
    print("\n" + "=" * 50)
    print(f"📊 Coaching Experiment Summary:")
    print(f"   Average Score: {avg_score:.2f}")
    print(f"   Pass Rate: {pass_rate:.1%}")
    print(f"   Tests Passed: {sum(1 for r in valid_results if r['in_expected_range'])}/{len(valid_results)}")
    
    return summary


async def run_frustration_experiment() -> Dict[str, Any]:
    """
    Run frustration detection experiment.
    
    Tests the system's ability to detect user frustration in conversations.
    """
    print("\n😤 Running Frustration Detection Experiment...")
    print("=" * 50)
    
    from app.services.opik_service import UserFrustrationDetector
    
    dataset = get_frustration_dataset()
    detector = UserFrustrationDetector()
    results = []
    
    for i, item in enumerate(dataset):
        print(f"\n[{i+1}/{len(dataset)}] Testing: {item['id']}")
        print(f"   Expected frustration: {item['expected_output']['frustration_level']}")
        
        try:
            result = detector.detect(
                user_input=item['input']['original_question'],
                previous_response=item['input']['ai_response'],
                current_reply=item['input']['user_reply']
            )
            
            expected_range = item['expected_output']['score_range']
            score = result['frustration_score']
            in_range = expected_range[0] <= score <= expected_range[1]
            
            test_result = {
                "id": item['id'],
                "expected_level": item['expected_output']['frustration_level'],
                "detected_score": score,
                "in_expected_range": in_range,
                "indicators": result.get('indicators', [])
            }
            results.append(test_result)
            
            status = "✅" if in_range else "⚠️"
            print(f"   {status} Detected: {score:.2f} (expected: {expected_range})")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({"id": item['id'], "error": str(e)})
    
    valid_results = [r for r in results if 'detected_score' in r]
    accuracy = sum(1 for r in valid_results if r['in_expected_range']) / len(valid_results) if valid_results else 0
    
    summary = {
        "experiment": "frustration_detection",
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": len(dataset),
        "accuracy": round(accuracy, 3),
        "results": results
    }
    
    print("\n" + "=" * 50)
    print(f"📊 Frustration Detection Summary:")
    print(f"   Accuracy: {accuracy:.1%}")
    
    return summary


async def run_extraction_experiment() -> Dict[str, Any]:
    """
    Run goal extraction experiment.
    
    Tests AI's ability to extract structured goals from conversations.
    """
    print("\n📝 Running Goal Extraction Experiment...")
    print("=" * 50)
    
    from app.services.ai_service import extract_goal_from_conversation
    from app.services.opik_service import GoalExtractionQualityMetric
    
    dataset = get_goal_extraction_dataset()
    metric = GoalExtractionQualityMetric()
    results = []
    
    for i, item in enumerate(dataset):
        print(f"\n[{i+1}/{len(dataset)}] Testing: {item['id']}")
        
        try:
            # Extract goal from conversation
            goal = await extract_goal_from_conversation(item['input']['conversation'])
            
            if goal:
                # Create summary of milestones
                milestones_summary = ", ".join([m.title for m in goal.milestones[:5]])
                
                # Evaluate extraction quality
                evaluation = metric.score(
                    conversation_summary=str(item['input']['conversation']),
                    goal_title=goal.title,
                    goal_description=goal.description or "",
                    goal_category=goal.category,
                    milestones_summary=milestones_summary
                )
                
                # Check expected outputs
                title_check = any(
                    kw.lower() in goal.title.lower() 
                    for kw in item['expected_output'].get('goal_title_contains', [])
                )
                category_check = goal.category == item['expected_output'].get('category', goal.category)
                milestone_count = len(goal.milestones)
                milestone_range = item['expected_output'].get('milestone_count_range', [1, 10])
                milestone_check = milestone_range[0] <= milestone_count <= milestone_range[1]
                
                result = {
                    "id": item['id'],
                    "extracted_title": goal.title,
                    "extracted_category": goal.category,
                    "milestone_count": milestone_count,
                    "quality_score": evaluation['score'],
                    "quality_reason": evaluation['reason'],
                    "title_match": title_check,
                    "category_match": category_check,
                    "milestone_count_valid": milestone_check
                }
                results.append(result)
                
                print(f"   Title: {goal.title}")
                print(f"   Category: {goal.category}")
                print(f"   Milestones: {milestone_count}")
                print(f"   Quality Score: {evaluation['score']:.2f}")
            else:
                print(f"   ❌ Failed to extract goal")
                results.append({"id": item['id'], "error": "Extraction returned None"})
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({"id": item['id'], "error": str(e)})
    
    valid_results = [r for r in results if 'quality_score' in r]
    avg_quality = sum(r['quality_score'] for r in valid_results) / len(valid_results) if valid_results else 0
    
    summary = {
        "experiment": "goal_extraction",
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": len(dataset),
        "successful_extractions": len(valid_results),
        "average_quality": round(avg_quality, 3),
        "results": results
    }
    
    print("\n" + "=" * 50)
    print(f"📊 Goal Extraction Summary:")
    print(f"   Successful Extractions: {len(valid_results)}/{len(dataset)}")
    print(f"   Average Quality: {avg_quality:.2f}")
    
    return summary


async def run_all_experiments() -> Dict[str, Any]:
    """Run all experiments and compile results."""
    print("\n🚀 Running All Experiments...")
    print("=" * 60)
    
    all_results = {
        "run_id": datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
        "model": "gpt-4o-mini",
        "experiments": {}
    }
    
    # Run each experiment
    all_results["experiments"]["coaching"] = await run_coaching_experiment()
    all_results["experiments"]["frustration"] = await run_frustration_experiment()
    all_results["experiments"]["extraction"] = await run_extraction_experiment()
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), "experiment_results")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"results_{all_results['run_id']}.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("🎉 All Experiments Complete!")
    print(f"📁 Results saved to: {output_file}")
    
    # Print overall summary
    print("\n📊 Overall Summary:")
    for exp_name, exp_data in all_results["experiments"].items():
        if "average_score" in exp_data:
            print(f"   {exp_name}: {exp_data['average_score']:.2f} avg score")
        elif "accuracy" in exp_data:
            print(f"   {exp_name}: {exp_data['accuracy']:.1%} accuracy")
        elif "average_quality" in exp_data:
            print(f"   {exp_name}: {exp_data['average_quality']:.2f} avg quality")
    
    return all_results


def log_to_opik(results: Dict[str, Any]):
    """Log experiment results to Opik."""
    try:
        from app.services.opik_service import is_opik_enabled
        
        if not is_opik_enabled():
            print("\n⚠️ Opik not configured. Results logged locally only.")
            return
        
        import opik
        
        # Log experiment run
        for exp_name, exp_data in results.get("experiments", {}).items():
            opik.track(
                name=f"experiment_{exp_name}",
                input={"experiment_type": exp_name},
                output=exp_data,
                metadata={
                    "run_id": results["run_id"],
                    "model": results["model"]
                }
            )
        
        print("\n✅ Results logged to Opik dashboard")
        
    except Exception as e:
        print(f"\n⚠️ Failed to log to Opik: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run MileSync AI Experiments")
    parser.add_argument(
        "--experiment",
        choices=["coaching", "frustration", "extraction", "all"],
        default="all",
        help="Which experiment to run"
    )
    parser.add_argument(
        "--log-to-opik",
        action="store_true",
        help="Log results to Opik dashboard"
    )
    
    args = parser.parse_args()
    
    # Check configuration
    if not check_openai_configured():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🔬 MileSync AI Experiment Runner")
    print("=" * 60)
    print(f"Model: gpt-4o-mini")
    print(f"Opik: {'Configured ✅' if settings.OPIK_API_KEY else 'Not configured ⚠️'}")
    print(f"Project: {settings.OPIK_PROJECT_NAME}")
    
    # Run experiments
    if args.experiment == "coaching":
        results = asyncio.run(run_coaching_experiment())
    elif args.experiment == "frustration":
        results = asyncio.run(run_frustration_experiment())
    elif args.experiment == "extraction":
        results = asyncio.run(run_extraction_experiment())
    else:
        results = asyncio.run(run_all_experiments())
    
    # Log to Opik if requested
    if args.log_to_opik:
        log_to_opik({"experiments": {args.experiment: results}} if args.experiment != "all" else results)


if __name__ == "__main__":
    main()
