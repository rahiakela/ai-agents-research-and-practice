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

"""Hybrid Team Sample - Local + Remote + MCP Combined.

This sample demonstrates combining all three agent types:
- Local agents with specialized tools
- Remote A2A agents for cross-service communication
- MCP tools for external system access

Based on Chapter 4, Examples 4-13 and 4-14: Hybrid Agent Team.

Key Concepts:
- Local agents handle domain-specific tasks
- Remote agents (A2A) handle cross-boundary concerns
- MCP provides access to external databases/systems
- Coordinator synthesizes all specialist outputs

Theme: SmartHome Complete Customer Support System

Prerequisites:
    1. Start the MCP server:
        python mcp_server.py  # Runs on port 8080

    2. Start the A2A billing server (from 05_a2a_server):
        cd ../05_a2a_server
        uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
"""

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams


# =============================================================================
# LOCAL TECHNICAL DIAGNOSTIC TOOLS
# =============================================================================

def check_device_diagnostics(device_id: str) -> dict:
    """Run comprehensive diagnostics on a device.

    Args:
        device_id: The device identifier.

    Returns:
        Diagnostic results with test outcomes.
    """
    diagnostics = {
        "DEV-THERM-001": {
            "device_id": "DEV-THERM-001",
            "product": "Smart Thermostat Pro",
            "diagnostics_run": True,
            "tests": {
                "connectivity": {"status": "pass", "latency_ms": 45},
                "temperature_sensor": {"status": "fail", "reading": 77, "expected": 72, "variance": 5},
                "humidity_sensor": {"status": "pass", "reading": 45},
                "power_supply": {"status": "pass", "voltage": 5.1},
                "firmware": {"status": "warning", "version": "2.3.1", "latest": "2.4.0"}
            },
            "overall_status": "degraded",
            "primary_issue": "Temperature sensor malfunction - reading 5°F high",
            "warranty_relevant": True
        }
    }

    return diagnostics.get(device_id, {
        "device_id": device_id,
        "diagnostics_run": False,
        "error": f"Device {device_id} not found"
    })


def analyze_error_patterns(device_id: str, days: int = 30) -> dict:
    """Analyze error patterns for a device over time.

    Args:
        device_id: The device identifier.
        days: Number of days to analyze.

    Returns:
        Error pattern analysis.
    """
    patterns = {
        "DEV-THERM-001": {
            "device_id": device_id,
            "analysis_period_days": days,
            "error_count": 15,
            "error_patterns": [
                {
                    "pattern": "temperature_spike",
                    "frequency": "daily",
                    "first_seen": "2024-11-10",
                    "likely_cause": "defective temperature sensor"
                }
            ],
            "impact_assessment": {
                "hvac_overcycling": True,
                "estimated_excess_runtime_hours": 45,
                "estimated_excess_energy_kwh": 38.5,
                "estimated_excess_cost": 47.00
            },
            "recommendation": "Replace device under warranty - sensor defect confirmed"
        }
    }

    return patterns.get(device_id, {
        "device_id": device_id,
        "error_count": 0,
        "error_patterns": [],
        "recommendation": "No significant errors detected"
    })


def lookup_known_issues(product_type: str) -> dict:
    """Look up known issues for a product type.

    Args:
        product_type: Type of product (e.g., "thermostat", "camera").

    Returns:
        Known issues and their resolutions.
    """
    known_issues = {
        "thermostat": [
            {
                "issue_id": "ISSUE-2024-001",
                "title": "Temperature sensor drift in firmware 2.3.x",
                "affected_versions": ["2.3.0", "2.3.1"],
                "symptoms": ["Inaccurate temperature readings", "HVAC overcycling"],
                "resolution": "Firmware 2.4.0 fixes this issue; replacement available for severe cases",
                "warranty_covered": True
            }
        ],
        "camera": [
            {
                "issue_id": "ISSUE-2024-002",
                "title": "Night vision flickering",
                "affected_versions": ["1.7.x"],
                "symptoms": ["Intermittent night vision", "Recording gaps"],
                "resolution": "Update to firmware 1.8.0",
                "warranty_covered": False
            }
        ]
    }

    return {
        "product_type": product_type,
        "known_issues": known_issues.get(product_type.lower(), []),
        "issues_found": len(known_issues.get(product_type.lower(), []))
    }


# =============================================================================
# LOCAL TECHNICAL AGENT (Example 4-13)
# =============================================================================

technical_agent = Agent(
    model="gemini-2.5-flash",
    name="TechnicalAgent",
    description="Diagnoses technical issues with smart home devices",
    instruction="""You are a technical diagnostics specialist for SmartHome devices.

    Your capabilities:
    1. Run device diagnostics
    2. Analyze error patterns over time
    3. Look up known issues for product types

    When diagnosing issues:
    1. Run comprehensive diagnostics on the device
    2. Analyze error patterns to understand the problem scope
    3. Check for known issues that match the symptoms
    4. Determine if the issue is warranty-relevant
    5. Estimate any cost impact from the malfunction

    Provide clear technical findings that can inform billing decisions.""",
    output_key="technical_diagnosis",
    tools=[
        check_device_diagnostics,
        analyze_error_patterns,
        lookup_known_issues
    ]
)


# =============================================================================
# REMOTE A2A BILLING AGENT (Example 4-13)
# =============================================================================

# Connect to the billing agent from 05_a2a_server
billing_agent = RemoteA2aAgent(
    name="BillingAgent",
    description="Handles billing inquiries, refunds, and payment processing",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)


# =============================================================================
# MCP CUSTOMER DATABASE TOOLS (Example 4-13)
# =============================================================================

# Connect to MCP server for customer database access
customer_db = McpToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse"
    ),
    tool_filter=None  # Accept all tools from this MCP server
)


# =============================================================================
# HYBRID COORDINATOR (Example 4-13 and 4-14)
# =============================================================================

coordinator = Agent(
    model="gemini-2.5-flash",
    name="CustomerServiceCoordinator",
    description="Main coordinator that orchestrates local, remote, and MCP resources",
    instruction="""You are the customer service coordinator for SmartHome Inc.
    You have access to multiple specialist resources:

    1. LOCAL - TechnicalAgent:
       - Device diagnostics
       - Error pattern analysis
       - Known issue lookup

    2. REMOTE - BillingAgent (via A2A):
       - Billing history queries
       - Refund calculations
       - Credit processing

    3. MCP - CustomerDatabase:
       - Customer lookup
       - Device usage history
       - Device registration info

    For a comprehensive support request (like a device defect causing billing impact):

    Step 1: Use MCP tools to look up the customer and their device usage
    Step 2: Delegate to TechnicalAgent to diagnose the device issue
    Step 3: If diagnosis reveals a problem affecting billing, delegate to
            BillingAgent to analyze charges and process credits

    SYNTHESIS (Example 4-14):
    After gathering all information, provide a unified response that:
    - Summarizes the technical diagnosis
    - Explains the billing impact
    - Describes the resolution (replacement, credit, etc.)
    - Lists next steps for the customer

    Be professional, empathetic, and thorough.""",
    sub_agents=[technical_agent, billing_agent],
    tools=[customer_db]
)


# For adk web compatibility - export as root_agent
root_agent = coordinator


# =============================================================================
# EXPECTED OUTPUT (Example 4-14)
# =============================================================================
#
# For a query like: "My smart thermostat is showing a wiring error, and I think
# it might have overcharged my last bill."
#
# Expected synthesized response:
#
# Based on my analysis:
#
# **Technical:** Your thermostat has a defective temperature sensor causing
# incorrect readings. This is a known issue (ISSUE-2024-001) covered under
# warranty, and I've initiated a replacement order.
#
# **Billing:** The sensor defect caused your HVAC system to run inefficiently,
# resulting in approximately $47 in excess energy costs over the past month.
# I've applied a $50 credit to your account to cover this impact.
#
# **Next Steps:**
# - Your replacement thermostat will arrive in 2-3 business days
# - Free installation is included
# - The $50 credit will appear on your next statement
#
# Is there anything else I can help you with?
