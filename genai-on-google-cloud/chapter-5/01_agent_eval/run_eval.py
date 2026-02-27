#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Programmatic Agent Evaluation Script.

This script demonstrates how to programmatically evaluate an ADK agent
using the evaluation framework. It loads test cases, runs the agent,
and computes tool usage and trajectory metrics.

Based on Chapter 5, Example 5-2: Agent Tool Usage Evaluation.

Usage:
    python run_eval.py

Alternative (using ADK CLI):
    adk eval . eval_set.json
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_eval_set(eval_set_path: str) -> dict:
    """Load evaluation set from JSON file."""
    with open(eval_set_path, "r") as f:
        return json.load(f)


def compute_tool_metrics(expected_calls: list, actual_calls: list) -> dict:
    """Compute tool usage metrics by comparing expected vs actual tool calls.

    Metrics computed:
    - tool_call_valid: Are all tool calls syntactically valid?
    - tool_name_match: Did the agent call the correct tools?
    - tool_parameter_key_match: Are parameter names correct?
    - tool_parameter_kv_match: Are parameter names AND values correct?

    Args:
        expected_calls: List of expected tool calls with names and args.
        actual_calls: List of actual tool calls made by the agent.

    Returns:
        Dictionary of computed metrics.
    """
    if not expected_calls:
        return {
            "tool_call_valid": 1.0,
            "tool_name_match": 1.0,
            "tool_parameter_key_match": 1.0,
            "tool_parameter_kv_match": 1.0
        }

    if not actual_calls:
        return {
            "tool_call_valid": 0.0,
            "tool_name_match": 0.0,
            "tool_parameter_key_match": 0.0,
            "tool_parameter_kv_match": 0.0
        }

    # Tool name matching
    expected_names = [c["tool_name"] for c in expected_calls]
    actual_names = [c.get("tool_name", c.get("name", "")) for c in actual_calls]

    name_matches = sum(1 for name in expected_names if name in actual_names)
    tool_name_match = name_matches / len(expected_names)

    # Parameter matching (for tools that matched)
    param_key_scores = []
    param_kv_scores = []

    for expected in expected_calls:
        exp_name = expected["tool_name"]
        exp_args = expected.get("args", {})

        # Find matching actual call
        matching_actual = None
        for actual in actual_calls:
            act_name = actual.get("tool_name", actual.get("name", ""))
            if act_name == exp_name:
                matching_actual = actual
                break

        if matching_actual:
            act_args = matching_actual.get("args", {})

            # Key match: proportion of expected keys that are present
            if exp_args:
                key_matches = sum(1 for k in exp_args if k in act_args)
                param_key_scores.append(key_matches / len(exp_args))

                # Key-value match: proportion of expected key-value pairs that match
                kv_matches = sum(
                    1 for k, v in exp_args.items()
                    if k in act_args and str(act_args[k]).lower() == str(v).lower()
                )
                param_kv_scores.append(kv_matches / len(exp_args))
            else:
                param_key_scores.append(1.0)
                param_kv_scores.append(1.0)
        else:
            param_key_scores.append(0.0)
            param_kv_scores.append(0.0)

    return {
        "tool_call_valid": 1.0,  # Assume valid if we got this far
        "tool_name_match": tool_name_match,
        "tool_parameter_key_match": sum(param_key_scores) / len(param_key_scores) if param_key_scores else 0.0,
        "tool_parameter_kv_match": sum(param_kv_scores) / len(param_kv_scores) if param_kv_scores else 0.0
    }


def compute_trajectory_metrics(expected_calls: list, actual_calls: list) -> dict:
    """Compute trajectory metrics for agent action sequences.

    Metrics computed:
    - trajectory_exact_match: Does sequence exactly match golden path?
    - trajectory_in_order_match: Correct sequence with possible extras?
    - trajectory_any_order_match: Required actions in any order?
    - trajectory_precision: Necessary actions / total actions
    - trajectory_recall: Required actions completed / required actions

    Args:
        expected_calls: Expected sequence of tool calls.
        actual_calls: Actual sequence of tool calls.

    Returns:
        Dictionary of trajectory metrics.
    """
    if not expected_calls:
        return {
            "trajectory_exact_match": 1.0,
            "trajectory_in_order_match": 1.0,
            "trajectory_any_order_match": 1.0,
            "trajectory_precision": 1.0,
            "trajectory_recall": 1.0
        }

    if not actual_calls:
        return {
            "trajectory_exact_match": 0.0,
            "trajectory_in_order_match": 0.0,
            "trajectory_any_order_match": 0.0,
            "trajectory_precision": 0.0,
            "trajectory_recall": 0.0
        }

    expected_names = [c["tool_name"] for c in expected_calls]
    actual_names = [c.get("tool_name", c.get("name", "")) for c in actual_calls]

    # Exact match: sequences are identical
    trajectory_exact_match = 1.0 if expected_names == actual_names else 0.0

    # In-order match: expected sequence appears in order within actual
    in_order = True
    exp_idx = 0
    for act_name in actual_names:
        if exp_idx < len(expected_names) and act_name == expected_names[exp_idx]:
            exp_idx += 1
    trajectory_in_order_match = 1.0 if exp_idx == len(expected_names) else 0.0

    # Any-order match: all expected tools appear regardless of order
    any_order = all(name in actual_names for name in expected_names)
    trajectory_any_order_match = 1.0 if any_order else 0.0

    # Precision: necessary actions / total actions taken
    necessary_count = sum(1 for name in actual_names if name in expected_names)
    trajectory_precision = necessary_count / len(actual_names) if actual_names else 0.0

    # Recall: required actions completed / required actions
    completed_count = sum(1 for name in expected_names if name in actual_names)
    trajectory_recall = completed_count / len(expected_names) if expected_names else 0.0

    return {
        "trajectory_exact_match": trajectory_exact_match,
        "trajectory_in_order_match": trajectory_in_order_match,
        "trajectory_any_order_match": trajectory_any_order_match,
        "trajectory_precision": trajectory_precision,
        "trajectory_recall": trajectory_recall
    }


async def run_single_case(agent, case: dict) -> dict:
    """Run evaluation for a single test case.

    Args:
        agent: The agent to evaluate.
        case: The evaluation case with user input and expected outputs.

    Returns:
        Evaluation results including metrics and responses.
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    # Create a runner for this evaluation
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="eval_runner",
        session_service=session_service
    )

    # Get the user query
    conversation = case.get("conversation", [])
    if not conversation:
        return {"error": "No conversation in case"}

    invocation = conversation[0]
    user_content = invocation.get("user_content", {})
    parts = user_content.get("parts", [])
    user_query = parts[0].get("text", "") if parts else ""

    # Run the agent
    session = await session_service.create_session(
        app_name="eval_runner",
        user_id="eval_user"
    )

    actual_tool_calls = []
    agent_response = ""

    async for event in runner.run_async(
        user_id="eval_user",
        session_id=session.id,
        new_message=user_query
    ):
        # Collect tool calls
        if hasattr(event, "tool_calls") and event.tool_calls:
            for tc in event.tool_calls:
                actual_tool_calls.append({
                    "tool_name": tc.name if hasattr(tc, "name") else str(tc),
                    "args": tc.args if hasattr(tc, "args") else {}
                })

        # Collect final response
        if hasattr(event, "content") and event.content:
            if hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        agent_response += part.text

    # Get expected tool calls
    expected_calls = invocation.get("expected_tool_calls", [])

    # Compute metrics
    tool_metrics = compute_tool_metrics(expected_calls, actual_tool_calls)
    trajectory_metrics = compute_trajectory_metrics(expected_calls, actual_tool_calls)

    # Check response contains expected keywords
    expected_contains = invocation.get("expected_response_contains", [])
    response_matches = sum(
        1 for keyword in expected_contains
        if keyword.lower() in agent_response.lower()
    )
    response_match_score = response_matches / len(expected_contains) if expected_contains else 1.0

    return {
        "eval_case_id": case["eval_case_id"],
        "name": case.get("name", ""),
        "user_query": user_query,
        "agent_response": agent_response[:500],  # Truncate for display
        "expected_tool_calls": expected_calls,
        "actual_tool_calls": actual_tool_calls,
        "metrics": {
            **tool_metrics,
            **trajectory_metrics,
            "response_keyword_match": response_match_score
        }
    }


async def run_evaluation(eval_set_path: str = "eval_set.json"):
    """Run full evaluation suite.

    Args:
        eval_set_path: Path to the evaluation set JSON file.
    """
    print("=" * 70)
    print("SmartHome Support Agent Evaluation")
    print("=" * 70)
    print()

    # Load evaluation set
    eval_set = load_eval_set(eval_set_path)
    print(f"Evaluation Set: {eval_set.get('name', eval_set['eval_set_id'])}")
    print(f"Description: {eval_set.get('description', 'N/A')}")
    print(f"Number of test cases: {len(eval_set['eval_cases'])}")
    print()

    # Import agent
    from agent import support_agent

    # Run each evaluation case
    results = []
    for i, case in enumerate(eval_set["eval_cases"], 1):
        print(f"Running case {i}/{len(eval_set['eval_cases'])}: {case.get('name', case['eval_case_id'])}")

        try:
            result = await run_single_case(support_agent, case)
            results.append(result)
            print(f"  Complete")
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                "eval_case_id": case["eval_case_id"],
                "error": str(e)
            })

    print()
    print("=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    print()

    # Compute aggregate metrics
    all_metrics = {}
    successful_results = [r for r in results if "metrics" in r]

    if successful_results:
        metric_keys = successful_results[0]["metrics"].keys()
        for key in metric_keys:
            values = [r["metrics"][key] for r in successful_results]
            all_metrics[key] = sum(values) / len(values)

        # Print summary
        print("AGGREGATE METRICS:")
        print("-" * 40)
        print("\nTool Usage Metrics:")
        for key in ["tool_call_valid", "tool_name_match", "tool_parameter_key_match", "tool_parameter_kv_match"]:
            if key in all_metrics:
                print(f"  {key}: {all_metrics[key]:.2%}")

        print("\nTrajectory Metrics:")
        for key in ["trajectory_exact_match", "trajectory_in_order_match", "trajectory_any_order_match",
                    "trajectory_precision", "trajectory_recall"]:
            if key in all_metrics:
                print(f"  {key}: {all_metrics[key]:.2%}")

        print("\nResponse Quality:")
        if "response_keyword_match" in all_metrics:
            print(f"  response_keyword_match: {all_metrics['response_keyword_match']:.2%}")

        print()
        print("-" * 40)
        print("INDIVIDUAL CASE RESULTS:")
        print("-" * 40)

        for result in results:
            print(f"\nCase: {result.get('name', result['eval_case_id'])}")
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            else:
                print(f"  Query: {result['user_query'][:60]}...")
                print(f"  Tool Name Match: {result['metrics']['tool_name_match']:.2%}")
                print(f"  Trajectory Recall: {result['metrics']['trajectory_recall']:.2%}")

    # Save results to file
    output_file = f"eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "eval_set_id": eval_set["eval_set_id"],
            "timestamp": datetime.now().isoformat(),
            "aggregate_metrics": all_metrics,
            "individual_results": results
        }, f, indent=2)

    print()
    print(f"Results saved to: {output_file}")
    print()

    return results


def main():
    """Main entry point."""
    # Check for API key
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("Warning: No GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT found.")
        print("Set your API key in .env file or environment variables.")
        print()

    # Run evaluation
    asyncio.run(run_evaluation())


if __name__ == "__main__":
    main()
