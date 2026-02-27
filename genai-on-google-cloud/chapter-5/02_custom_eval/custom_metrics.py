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

"""Custom Evaluation Metrics for Financial Advisor Agent.

This module demonstrates two types of custom metrics:
1. LLM-as-Judge metrics (Example 5-3) - Using an LLM to evaluate qualitative aspects
2. Computation-based metrics (Example 5-4) - Using code to check business rules

Based on Chapter 5, Examples 5-3 and 5-4.
"""

import os
import json
from typing import Optional

# Try to import Vertex AI evaluation components
try:
    from vertexai.evaluation import PointwiseMetricPromptTemplate, PointwiseMetric, CustomMetric
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    PointwiseMetricPromptTemplate = None
    PointwiseMetric = None
    CustomMetric = None
    print("Note: vertexai not available. LLM-as-judge metrics will use fallback.")


# =============================================================================
# LLM-AS-JUDGE METRICS (Example 5-3)
# =============================================================================

# Helpfulness Metric using PointwiseMetricPromptTemplate
HELPFULNESS_PROMPT = """You are evaluating the helpfulness of a financial advisor's response.

**User Query:**
{query}

**Advisor Response:**
{response}

**Evaluation Criteria:**
A helpful financial advice response should:
1. Directly address the user's question or concern
2. Provide actionable recommendations or clear information
3. Consider the user's specific situation (risk profile, timeline, goals)
4. Be clear and understandable to non-experts
5. Include appropriate caveats about risks

**Rating Scale:**
- 1.0 = Exceptional: Fully addresses the query with actionable, personalized advice
- 0.75 = Good: Addresses the query well with useful information
- 0.5 = Adequate: Addresses the basic query but lacks depth or personalization
- 0.25 = Poor: Partially addresses the query, missing key elements
- 0.0 = Unhelpful: Fails to address the query or provides misleading information

Provide your rating as a single number (0.0, 0.25, 0.5, 0.75, or 1.0) followed by a brief justification.

Rating:"""


# =============================================================================
# VERTEX AI METRIC DEFINITIONS (Example 5-3 Pattern)
# =============================================================================
# These follow the exact pattern from Chapter 5, Example 5-3

if VERTEX_AVAILABLE:
    # Create the prompt template using criteria dict pattern (Example 5-3)
    helpfulness_prompt_template = PointwiseMetricPromptTemplate(
        criteria={
            "Helpfulness": (
                "Evaluate whether the financial advisor's response is genuinely helpful. Consider:\n"
                "  - Does it directly address the user's question or need?\n"
                "  - Is the information accurate and actionable?\n"
                "  - Does it consider the user's specific situation (risk profile, timeline, goals)?\n"
                "  - Is the response clear and understandable to non-experts?\n"
                "  - Does it include appropriate caveats about risks?"
            )
        },
        rating_rubric={
            "1": "Very helpful - fully addresses the user's needs with actionable advice",
            "0.5": "Somewhat helpful - partially addresses needs but lacks depth or specificity",
            "0": "Not helpful - misses user's needs or provides incorrect/misleading information"
        },
        input_variables=["prompt", "response"],
    )

    # Wrap in PointwiseMetric for use with EvalTask (Example 5-3)
    helpfulness_metric = PointwiseMetric(
        metric="helpfulness",
        metric_prompt_template=helpfulness_prompt_template,
    )


async def evaluate_helpfulness_llm(
    query: str,
    response: str,
    model: str = "gemini-2.5-flash"
) -> dict:
    """Evaluate response helpfulness using LLM-as-judge.

    This is a standalone implementation that can be used without Vertex AI.

    Args:
        query: The user's original query.
        response: The agent's response to evaluate.
        model: The model to use for evaluation.

    Returns:
        Evaluation result with score and reasoning.
    """
    import google.generativeai as genai

    # Configure the API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

    # Format the evaluation prompt
    evaluation_prompt = HELPFULNESS_PROMPT.format(query=query, response=response)

    try:
        # Call the model for evaluation
        model_instance = genai.GenerativeModel(model)
        result = model_instance.generate_content(evaluation_prompt)
        evaluation_text = result.text

        # Parse the rating from the response
        # Look for a number at the start of the response
        score = 0.5  # Default
        for possible_score in ["1.0", "0.75", "0.5", "0.25", "0.0"]:
            if possible_score in evaluation_text[:20]:
                score = float(possible_score)
                break

        return {
            "metric": "helpfulness",
            "score": score,
            "reasoning": evaluation_text,
            "method": "llm_as_judge"
        }

    except Exception as e:
        return {
            "metric": "helpfulness",
            "score": None,
            "error": str(e),
            "method": "llm_as_judge"
        }


# Compliance Language Metric
COMPLIANCE_LANGUAGE_PROMPT = """You are evaluating whether a financial advisor's response includes appropriate compliance language.

**Advisor Response:**
{response}

**Required Compliance Elements:**
1. Risk disclaimers (mentioning that investments can lose value)
2. No guarantee of returns (avoiding phrases like "guaranteed" or "certain")
3. Recommendation to consult qualified advisors
4. Disclosure that past performance doesn't predict future results

**Rating Scale:**
- 1.0 = All required compliance elements present
- 0.75 = Most elements present (3 of 4)
- 0.5 = Some elements present (2 of 4)
- 0.25 = Few elements present (1 of 4)
- 0.0 = No compliance elements present

Provide your rating as a single number followed by a list of present/missing elements.

Rating:"""


async def evaluate_compliance_language_llm(
    response: str,
    model: str = "gemini-2.5-flash"
) -> dict:
    """Evaluate response for compliance language using LLM-as-judge.

    Args:
        response: The agent's response to evaluate.
        model: The model to use for evaluation.

    Returns:
        Evaluation result with score and findings.
    """
    import google.generativeai as genai

    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)

    evaluation_prompt = COMPLIANCE_LANGUAGE_PROMPT.format(response=response)

    try:
        model_instance = genai.GenerativeModel(model)
        result = model_instance.generate_content(evaluation_prompt)
        evaluation_text = result.text

        score = 0.5
        for possible_score in ["1.0", "0.75", "0.5", "0.25", "0.0"]:
            if possible_score in evaluation_text[:20]:
                score = float(possible_score)
                break

        return {
            "metric": "compliance_language",
            "score": score,
            "reasoning": evaluation_text,
            "method": "llm_as_judge"
        }

    except Exception as e:
        return {
            "metric": "compliance_language",
            "score": None,
            "error": str(e),
            "method": "llm_as_judge"
        }


# =============================================================================
# COMPUTATION-BASED METRICS (Example 5-4)
# =============================================================================

def evaluate_portfolio_compliance(
    recommendation: dict,
    client_context: dict
) -> dict:
    """Check if portfolio recommendation meets compliance rules.

    This is a computation-based metric that checks hard business rules
    without using an LLM. It's deterministic and auditable.

    Based on Example 5-4: Custom computation-based metric.

    Args:
        recommendation: The portfolio recommendation to evaluate.
            Expected structure:
            {
                "risk_score": int,
                "holdings": [{"symbol": str, "percentage": float}, ...],
                "disclosure_included": bool
            }
        client_context: Client information for suitability checks.
            Expected structure:
            {
                "max_risk_tolerance": int,
                "investment_experience": str
            }

    Returns:
        Compliance evaluation with score and violations.
    """
    violations = []
    warnings = []

    # 1. Check risk score constraints
    risk_score = recommendation.get("risk_score", 0)
    max_tolerance = client_context.get("max_risk_tolerance", 7)

    if risk_score > max_tolerance:
        violations.append(
            f"Risk score ({risk_score}) exceeds client's max tolerance ({max_tolerance})"
        )

    # 2. Check concentration limits (SEC Rule: no single position > 25%)
    holdings = recommendation.get("holdings", [])
    for holding in holdings:
        percentage = holding.get("percentage", 0)
        symbol = holding.get("symbol", "Unknown")

        if percentage > 25:
            violations.append(
                f"Concentration limit exceeded: {symbol} at {percentage}% (max 25%)"
            )
        elif percentage > 20:
            warnings.append(
                f"Near concentration limit: {symbol} at {percentage}%"
            )

    # 3. Check required disclosures
    if not recommendation.get("disclosure_included", False):
        violations.append("Missing required SEC disclosure statements")

    # 4. Check for prohibited investments (example: penny stocks for conservative investors)
    if client_context.get("risk_profile") == "conservative":
        for holding in holdings:
            symbol = holding.get("symbol", "")
            if symbol in ["ARKK", "MEME", "SPAC"]:  # High-risk examples
                violations.append(
                    f"High-risk investment {symbol} unsuitable for conservative investor"
                )

    # 5. Check total allocation equals 100%
    total_allocation = sum(h.get("percentage", 0) for h in holdings)
    if abs(total_allocation - 100) > 0.1:  # Allow small rounding errors
        warnings.append(
            f"Total allocation is {total_allocation}%, should be 100%"
        )

    # Calculate compliance score
    if violations:
        score = 0.0
    elif warnings:
        score = 0.75
    else:
        score = 1.0

    return {
        "metric": "portfolio_compliance",
        "score": score,
        "compliant": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "method": "computation_based"
    }


def evaluate_diversification(holdings: list) -> dict:
    """Evaluate portfolio diversification quality.

    Computation-based metric that checks diversification rules.

    Args:
        holdings: List of holdings with asset_class and percentage.

    Returns:
        Diversification score and analysis.
    """
    if not holdings:
        return {
            "metric": "diversification",
            "score": 0.0,
            "analysis": "No holdings provided",
            "method": "computation_based"
        }

    # Count asset classes
    asset_classes = set()
    max_single_position = 0

    for holding in holdings:
        asset_class = holding.get("asset_class", holding.get("symbol", "Unknown"))
        asset_classes.add(asset_class)
        percentage = holding.get("percentage", 0)
        max_single_position = max(max_single_position, percentage)

    num_asset_classes = len(asset_classes)
    num_holdings = len(holdings)

    # Scoring rules
    # - More asset classes = better diversification
    # - Lower max position = better diversification
    # - More holdings = better diversification

    asset_class_score = min(num_asset_classes / 4, 1.0)  # 4+ classes is ideal
    concentration_score = max(0, 1 - (max_single_position - 25) / 75)  # Penalize > 25%
    holdings_score = min(num_holdings / 5, 1.0)  # 5+ holdings is ideal

    overall_score = (asset_class_score + concentration_score + holdings_score) / 3

    return {
        "metric": "diversification",
        "score": round(overall_score, 2),
        "analysis": {
            "num_asset_classes": num_asset_classes,
            "num_holdings": num_holdings,
            "max_single_position": max_single_position,
            "asset_class_score": round(asset_class_score, 2),
            "concentration_score": round(concentration_score, 2),
            "holdings_score": round(holdings_score, 2)
        },
        "method": "computation_based"
    }


def evaluate_risk_appropriateness(
    recommendation_risk: int,
    client_risk_profile: str,
    investment_timeline: int
) -> dict:
    """Evaluate if risk level is appropriate for client and timeline.

    Args:
        recommendation_risk: Risk score of the recommendation (1-10).
        client_risk_profile: Client's risk profile (conservative, moderate, aggressive).
        investment_timeline: Years until investment goal.

    Returns:
        Risk appropriateness score and reasoning.
    """
    # Map risk profiles to acceptable ranges
    risk_ranges = {
        "conservative": (1, 4),
        "moderate": (3, 7),
        "aggressive": (5, 10)
    }

    min_risk, max_risk = risk_ranges.get(client_risk_profile, (1, 10))

    # Adjust for timeline
    if investment_timeline < 5:
        # Short timeline: reduce acceptable risk
        max_risk = min(max_risk, 5)
    elif investment_timeline > 20:
        # Long timeline: can accept more risk
        min_risk = max(1, min_risk - 1)

    # Check if recommendation is within range
    if min_risk <= recommendation_risk <= max_risk:
        score = 1.0
        status = "appropriate"
    elif recommendation_risk < min_risk:
        score = 0.75
        status = "too_conservative"
    else:
        # Too risky
        overage = recommendation_risk - max_risk
        score = max(0, 1 - (overage * 0.25))
        status = "too_aggressive"

    return {
        "metric": "risk_appropriateness",
        "score": round(score, 2),
        "status": status,
        "recommendation_risk": recommendation_risk,
        "acceptable_range": f"{min_risk}-{max_risk}",
        "client_profile": client_risk_profile,
        "timeline_years": investment_timeline,
        "method": "computation_based"
    }


# =============================================================================
# COMBINED EVALUATION
# =============================================================================

async def run_full_evaluation(
    query: str,
    response: str,
    recommendation: Optional[dict] = None,
    client_context: Optional[dict] = None
) -> dict:
    """Run all custom metrics on a response.

    Args:
        query: The user's query.
        response: The agent's response.
        recommendation: Optional structured recommendation data.
        client_context: Optional client context for compliance checks.

    Returns:
        Combined evaluation results from all metrics.
    """
    results = {}

    # LLM-as-judge metrics
    results["helpfulness"] = await evaluate_helpfulness_llm(query, response)
    results["compliance_language"] = await evaluate_compliance_language_llm(response)

    # Computation-based metrics (if data available)
    if recommendation and client_context:
        results["portfolio_compliance"] = evaluate_portfolio_compliance(
            recommendation, client_context
        )

        if "holdings" in recommendation:
            results["diversification"] = evaluate_diversification(
                recommendation["holdings"]
            )

        if "risk_score" in recommendation:
            results["risk_appropriateness"] = evaluate_risk_appropriateness(
                recommendation["risk_score"],
                client_context.get("risk_profile", "moderate"),
                client_context.get("timeline_years", 10)
            )

    # Calculate aggregate score
    scores = [r.get("score", 0) for r in results.values() if r.get("score") is not None]
    aggregate_score = sum(scores) / len(scores) if scores else 0

    return {
        "aggregate_score": round(aggregate_score, 2),
        "metrics": results
    }
