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

"""Financial Advisor Agent - For Custom Metrics Evaluation.

This agent provides investment and portfolio advice. We use custom metrics
to evaluate both the helpfulness of responses (LLM-as-judge) and
compliance with financial regulations (computation-based).

Based on Chapter 5, Examples 5-3 and 5-4.
"""

import json
from google.adk.agents import Agent


# =============================================================================
# FINANCIAL ADVISOR TOOLS
# =============================================================================

def get_portfolio_allocation(client_id: str) -> dict:
    """Get current portfolio allocation for a client.

    Args:
        client_id: The client identifier.

    Returns:
        Current portfolio holdings and allocation.
    """
    portfolios = {
        "CLIENT-001": {
            "client_id": "CLIENT-001",
            "name": "John Doe",
            "risk_profile": "moderate",
            "max_risk_tolerance": 6,
            "holdings": [
                {"symbol": "VTI", "name": "Total Stock Market ETF", "percentage": 40, "value": 80000},
                {"symbol": "VXUS", "name": "International Stock ETF", "percentage": 20, "value": 40000},
                {"symbol": "BND", "name": "Total Bond Market ETF", "percentage": 30, "value": 60000},
                {"symbol": "VTIP", "name": "Inflation-Protected Securities", "percentage": 10, "value": 20000}
            ],
            "total_value": 200000,
            "last_rebalance": "2024-10-15"
        },
        "CLIENT-002": {
            "client_id": "CLIENT-002",
            "name": "Jane Smith",
            "risk_profile": "aggressive",
            "max_risk_tolerance": 9,
            "holdings": [
                {"symbol": "QQQ", "name": "Nasdaq 100 ETF", "percentage": 50, "value": 150000},
                {"symbol": "ARKK", "name": "Innovation ETF", "percentage": 30, "value": 90000},
                {"symbol": "SOXX", "name": "Semiconductor ETF", "percentage": 20, "value": 60000}
            ],
            "total_value": 300000,
            "last_rebalance": "2024-11-01"
        }
    }

    portfolio = portfolios.get(client_id)
    if portfolio:
        return {"found": True, "portfolio": portfolio}
    return {"found": False, "error": f"Client not found: {client_id}"}


def analyze_investment(symbol: str, investment_amount: float) -> dict:
    """Analyze a potential investment.

    Args:
        symbol: Stock or ETF symbol.
        investment_amount: Amount to invest.

    Returns:
        Investment analysis with risk assessment.
    """
    investments = {
        "VTI": {
            "symbol": "VTI",
            "name": "Vanguard Total Stock Market ETF",
            "type": "ETF",
            "risk_score": 5,
            "expense_ratio": 0.03,
            "diversification": "High - 4000+ US stocks",
            "recommendation": "Core holding for most portfolios"
        },
        "QQQ": {
            "symbol": "QQQ",
            "name": "Invesco QQQ Trust",
            "type": "ETF",
            "risk_score": 7,
            "expense_ratio": 0.20,
            "diversification": "Medium - Top 100 Nasdaq stocks",
            "recommendation": "Growth-oriented, higher volatility"
        },
        "ARKK": {
            "symbol": "ARKK",
            "name": "ARK Innovation ETF",
            "type": "ETF",
            "risk_score": 9,
            "expense_ratio": 0.75,
            "diversification": "Low - Concentrated in disruptive tech",
            "recommendation": "High risk, suitable for aggressive investors only"
        },
        "BND": {
            "symbol": "BND",
            "name": "Vanguard Total Bond Market ETF",
            "type": "ETF",
            "risk_score": 2,
            "expense_ratio": 0.03,
            "diversification": "High - Broad US bond market",
            "recommendation": "Income and stability, lower returns"
        }
    }

    investment = investments.get(symbol.upper())
    if investment:
        projected_return = {
            "conservative": investment_amount * 0.04,
            "moderate": investment_amount * 0.07,
            "optimistic": investment_amount * 0.12
        }
        return {
            "found": True,
            "analysis": investment,
            "investment_amount": investment_amount,
            "projected_annual_return": projected_return
        }
    return {"found": False, "error": f"Investment not found: {symbol}"}


def generate_recommendation(
    client_id: str,
    goal: str,
    timeline_years: int
) -> dict:
    """Generate a portfolio recommendation for a client goal.

    Args:
        client_id: The client identifier.
        goal: Investment goal (retirement, college, house, etc.).
        timeline_years: Years until goal.

    Returns:
        Portfolio recommendation with allocation.
    """
    # Get client profile
    portfolio_result = get_portfolio_allocation(client_id)
    if not portfolio_result.get("found"):
        return {"error": "Client not found"}

    client = portfolio_result["portfolio"]
    risk_profile = client["risk_profile"]

    # Generate recommendation based on goal and timeline
    if timeline_years > 20:
        # Long-term: more aggressive
        recommendation = {
            "strategy": "Growth-focused",
            "risk_score": 7,
            "allocation": [
                {"asset_class": "US Stocks", "percentage": 50, "suggested_etf": "VTI"},
                {"asset_class": "International Stocks", "percentage": 25, "suggested_etf": "VXUS"},
                {"asset_class": "Bonds", "percentage": 15, "suggested_etf": "BND"},
                {"asset_class": "Alternatives", "percentage": 10, "suggested_etf": "VNQ"}
            ]
        }
    elif timeline_years > 10:
        # Medium-term: balanced
        recommendation = {
            "strategy": "Balanced Growth",
            "risk_score": 5,
            "allocation": [
                {"asset_class": "US Stocks", "percentage": 40, "suggested_etf": "VTI"},
                {"asset_class": "International Stocks", "percentage": 20, "suggested_etf": "VXUS"},
                {"asset_class": "Bonds", "percentage": 30, "suggested_etf": "BND"},
                {"asset_class": "Cash/Short-term", "percentage": 10, "suggested_etf": "VTIP"}
            ]
        }
    else:
        # Short-term: conservative
        recommendation = {
            "strategy": "Capital Preservation",
            "risk_score": 3,
            "allocation": [
                {"asset_class": "US Stocks", "percentage": 25, "suggested_etf": "VTI"},
                {"asset_class": "Bonds", "percentage": 50, "suggested_etf": "BND"},
                {"asset_class": "Short-term Bonds", "percentage": 15, "suggested_etf": "VCSH"},
                {"asset_class": "Cash", "percentage": 10, "suggested_etf": "VMFXX"}
            ]
        }

    # Add required disclosures
    disclosures = [
        "Past performance does not guarantee future results.",
        "Investments are subject to market risk, including possible loss of principal.",
        "This is not personalized investment advice. Consult a qualified advisor.",
        "ETF expense ratios and holdings may change. Check current prospectus."
    ]

    return {
        "client_id": client_id,
        "goal": goal,
        "timeline_years": timeline_years,
        "current_risk_profile": risk_profile,
        "recommendation": recommendation,
        "disclosures": disclosures,
        "disclosure_included": True
    }


def check_regulatory_compliance(recommendation: dict) -> dict:
    """Check if a recommendation meets regulatory requirements.

    Args:
        recommendation: The investment recommendation to check.

    Returns:
        Compliance check results.
    """
    issues = []

    # Check for required disclosures
    if not recommendation.get("disclosure_included"):
        issues.append("Missing required disclosures")

    # Check concentration limits (SEC Rule: no more than 25% in single security)
    allocation = recommendation.get("recommendation", {}).get("allocation", [])
    for asset in allocation:
        if asset.get("percentage", 0) > 25:
            issues.append(f"Concentration warning: {asset['asset_class']} at {asset['percentage']}%")

    # Check risk alignment
    risk_score = recommendation.get("recommendation", {}).get("risk_score", 0)
    if risk_score > 8:
        issues.append("High risk recommendation requires additional suitability documentation")

    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "checked_at": "2025-01-14T12:00:00Z"
    }


# =============================================================================
# FINANCIAL ADVISOR AGENT
# =============================================================================

financial_advisor = Agent(
    model="gemini-2.5-flash",
    name="FinancialAdvisorAgent",
    description="Investment advisor for portfolio management and financial planning",
    instruction="""You are a licensed financial advisor helping clients with
    investment decisions and portfolio management.

    When advising clients:
    1. Always start by reviewing their current portfolio and risk profile
    2. Provide balanced recommendations based on their goals and timeline
    3. Always include required regulatory disclosures
    4. Be clear about risks and never guarantee returns
    5. Recommend diversified portfolios appropriate to their risk tolerance

    Important compliance requirements:
    - Never recommend single stocks over 25% of portfolio
    - Always include SEC-required disclosures
    - Document risk assessments for high-risk recommendations
    - Consider client's stated risk tolerance in all recommendations

    Be helpful, professional, and always act in the client's best interest.""",
    tools=[
        get_portfolio_allocation,
        analyze_investment,
        generate_recommendation,
        check_regulatory_compliance
    ]
)

# For adk web compatibility
root_agent = financial_advisor
