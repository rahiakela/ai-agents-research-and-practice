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

"""Custom Metrics Evaluation Demo.

This script demonstrates both LLM-as-judge and computation-based
custom metrics for evaluating a financial advisor agent.

Based on Chapter 5, Examples 5-3 and 5-4.

Usage:
    python run_evaluation.py
"""

import asyncio
import json
import os
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Sample test cases for evaluation
TEST_CASES = [
    {
        "id": "case_001",
        "name": "Retirement portfolio recommendation",
        "query": "I'm 35 years old and want to retire at 65. What's a good portfolio allocation for my retirement savings?",
        "response": """Based on your 30-year investment timeline, I recommend a growth-focused portfolio allocation:

**Recommended Allocation:**
- US Stocks (VTI): 50% - Broad market exposure for long-term growth
- International Stocks (VXUS): 25% - Geographic diversification
- Bonds (BND): 15% - Some stability and income
- Real Estate (VNQ): 10% - Inflation hedge and diversification

**Risk Assessment:**
This allocation has a risk score of 7/10, appropriate for your long timeline. As you approach retirement, we'll gradually shift to more conservative holdings.

**Important Disclosures:**
- Past performance does not guarantee future results
- Investments are subject to market risk, including possible loss of principal
- This is general guidance; consult a qualified financial advisor for personalized advice
- Review and rebalance your portfolio annually""",
        "recommendation": {
            "risk_score": 7,
            "holdings": [
                {"symbol": "VTI", "asset_class": "US Stocks", "percentage": 50},
                {"symbol": "VXUS", "asset_class": "International Stocks", "percentage": 25},
                {"symbol": "BND", "asset_class": "Bonds", "percentage": 15},
                {"symbol": "VNQ", "asset_class": "Real Estate", "percentage": 10}
            ],
            "disclosure_included": True
        },
        "client_context": {
            "max_risk_tolerance": 8,
            "risk_profile": "moderate",
            "timeline_years": 30
        }
    },
    {
        "id": "case_002",
        "name": "Conservative investor high-risk recommendation",
        "query": "I'm retired and need income from my investments. What should I invest in?",
        "response": """For income in retirement, consider high-growth tech stocks like ARKK and QQQ for maximum returns!

**Recommended Allocation:**
- ARKK Innovation ETF: 40%
- QQQ Nasdaq 100: 35%
- Individual tech stocks: 25%

This aggressive strategy could double your money!""",
        "recommendation": {
            "risk_score": 9,
            "holdings": [
                {"symbol": "ARKK", "asset_class": "High Risk ETF", "percentage": 40},
                {"symbol": "QQQ", "asset_class": "Tech ETF", "percentage": 35},
                {"symbol": "TECH", "asset_class": "Individual Stocks", "percentage": 25}
            ],
            "disclosure_included": False
        },
        "client_context": {
            "max_risk_tolerance": 3,
            "risk_profile": "conservative",
            "timeline_years": 5
        }
    },
    {
        "id": "case_003",
        "name": "Concentrated portfolio",
        "query": "Should I put all my savings into a single stock?",
        "response": """I strongly advise against putting all your savings into a single stock. Diversification is key to managing risk.

**Why Diversification Matters:**
- Reduces impact of any single investment's poor performance
- Smooths out volatility over time
- SEC guidelines recommend no single position exceed 25% of portfolio

**Recommended Approach:**
Instead, consider a diversified portfolio:
- Broad market ETFs for equity exposure
- Bond funds for stability
- Multiple asset classes for true diversification

**Disclaimer:**
Individual stocks carry significant risk, including potential total loss. This is general information; please consult a licensed financial advisor for advice tailored to your situation.""",
        "recommendation": {
            "risk_score": 5,
            "holdings": [
                {"symbol": "VTI", "asset_class": "US Stocks", "percentage": 40},
                {"symbol": "VXUS", "asset_class": "International", "percentage": 20},
                {"symbol": "BND", "asset_class": "Bonds", "percentage": 30},
                {"symbol": "VTIP", "asset_class": "TIPS", "percentage": 10}
            ],
            "disclosure_included": True
        },
        "client_context": {
            "max_risk_tolerance": 6,
            "risk_profile": "moderate",
            "timeline_years": 15
        }
    }
]


async def run_demo():
    """Run the custom metrics evaluation demo."""
    from custom_metrics import (
        evaluate_helpfulness_llm,
        evaluate_compliance_language_llm,
        evaluate_portfolio_compliance,
        evaluate_diversification,
        evaluate_risk_appropriateness,
        run_full_evaluation
    )

    print("=" * 70)
    print("Custom Metrics Evaluation Demo")
    print("Based on Chapter 5, Examples 5-3 and 5-4")
    print("=" * 70)
    print()

    all_results = []

    for case in TEST_CASES:
        print(f"\n{'='*70}")
        print(f"Test Case: {case['name']}")
        print(f"{'='*70}")
        print(f"\nQuery: {case['query'][:80]}...")
        print(f"\nResponse preview: {case['response'][:150]}...")
        print()

        # Run full evaluation
        print("Running evaluation...")
        result = await run_full_evaluation(
            query=case["query"],
            response=case["response"],
            recommendation=case["recommendation"],
            client_context=case["client_context"]
        )

        print("\n" + "-" * 40)
        print("EVALUATION RESULTS:")
        print("-" * 40)

        # Display LLM-as-judge metrics
        print("\nLLM-as-Judge Metrics:")
        for metric_name in ["helpfulness", "compliance_language"]:
            if metric_name in result["metrics"]:
                m = result["metrics"][metric_name]
                score = m.get("score", "N/A")
                if isinstance(score, float):
                    print(f"  {metric_name}: {score:.2f}")
                else:
                    print(f"  {metric_name}: {score}")

        # Display computation-based metrics
        print("\nComputation-Based Metrics:")
        for metric_name in ["portfolio_compliance", "diversification", "risk_appropriateness"]:
            if metric_name in result["metrics"]:
                m = result["metrics"][metric_name]
                score = m.get("score", "N/A")
                if isinstance(score, float):
                    print(f"  {metric_name}: {score:.2f}")
                    if metric_name == "portfolio_compliance":
                        print(f"    Compliant: {m.get('compliant', 'N/A')}")
                        if m.get("violations"):
                            print(f"    Violations: {m['violations']}")
                    elif metric_name == "risk_appropriateness":
                        print(f"    Status: {m.get('status', 'N/A')}")
                else:
                    print(f"  {metric_name}: {score}")

        print(f"\nAGGREGATE SCORE: {result['aggregate_score']:.2f}")

        # Store result
        all_results.append({
            "case_id": case["id"],
            "case_name": case["name"],
            "aggregate_score": result["aggregate_score"],
            "metrics": result["metrics"]
        })

    # Summary
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"\nTotal cases evaluated: {len(all_results)}")

    avg_score = sum(r["aggregate_score"] for r in all_results) / len(all_results)
    print(f"Average aggregate score: {avg_score:.2f}")

    print("\nPer-case scores:")
    for r in all_results:
        status = "PASS" if r["aggregate_score"] >= 0.7 else "REVIEW"
        print(f"  [{status}] {r['case_name']}: {r['aggregate_score']:.2f}")

    # Save results
    output_file = f"custom_eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_cases": len(all_results),
                "average_score": avg_score
            },
            "results": all_results
        }, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")
    print()

    return all_results


def main():
    """Main entry point."""
    # Check for API key
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("Warning: No GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT found.")
        print("LLM-as-judge metrics will fail. Computation-based metrics will still work.")
        print("Set your API key in .env file or environment variables.")
        print()

    # Run demo
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
