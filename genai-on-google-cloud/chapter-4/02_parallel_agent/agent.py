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

"""Parallel Agent Sample - The Independent Taskforce Pattern.

This sample demonstrates ParallelAgent for concurrent execution.
Based on Chapter 4, Example 4-6: Concurrent Information Gathering.

Key Concepts:
- ParallelAgent executes sub-agents concurrently
- Each agent writes to a distinct output_key (avoid race conditions)
- Combine with SequentialAgent for gather-then-synthesize pattern
- Significant performance benefit for independent operations

Theme: SmartHome Customer Support - Comprehensive Device Support
"""

from google.adk.agents import Agent, ParallelAgent, SequentialAgent


# =============================================================================
# SIMULATED TOOLS
# =============================================================================

def query_order_database(customer_id: str) -> dict:
    """Query the order database for customer purchase history.

    Args:
        customer_id: The customer identifier.

    Returns:
        Customer's purchase history.
    """
    return {
        "customer_id": customer_id or "CUST-12345",
        "orders": [
            {
                "order_id": "ORD-2024-001",
                "product": "Smart Thermostat Pro",
                "purchase_date": "2024-08-15",
                "price": 299.99
            },
            {
                "order_id": "ORD-2024-002",
                "product": "Smart Light Bulb (4-pack)",
                "purchase_date": "2024-09-20",
                "price": 79.99
            }
        ],
        "total_spent": 379.98,
        "loyalty_tier": "Gold"
    }


def fetch_product_manual(product_name: str) -> dict:
    """Fetch the product manual for a specific product.

    Args:
        product_name: The name of the product.

    Returns:
        Product manual content and links.
    """
    return {
        "product": product_name or "Smart Thermostat Pro",
        "manual_sections": [
            "Installation Guide",
            "WiFi Setup",
            "Temperature Programming",
            "Troubleshooting"
        ],
        "quick_start_url": "https://docs.smarthome.com/thermostat/quickstart",
        "full_manual_url": "https://docs.smarthome.com/thermostat/full"
    }


def get_troubleshooting_guides(product_type: str) -> dict:
    """Get troubleshooting guides for common issues.

    Args:
        product_type: The type of product.

    Returns:
        Troubleshooting guides and tips.
    """
    return {
        "product_type": product_type or "Thermostat",
        "common_issues": [
            {
                "issue": "WiFi Connection Problems",
                "solution": "Restart router and re-pair device"
            },
            {
                "issue": "Temperature Inaccuracy",
                "solution": "Calibrate sensor in settings menu"
            },
            {
                "issue": "Display Not Working",
                "solution": "Check power connection and reset device"
            }
        ],
        "support_phone": "1-800-SMARTHOME"
    }


def query_telemetry_service(device_id: str) -> dict:
    """Query the telemetry service for device usage data.

    Args:
        device_id: The device identifier.

    Returns:
        Device usage and telemetry data.
    """
    return {
        "device_id": device_id or "THERM-2024-001",
        "usage_hours_30d": 720,
        "avg_daily_adjustments": 4.2,
        "connectivity_uptime": "99.2%",
        "last_seen": "2025-01-13T14:30:00Z"
    }


def calculate_energy_metrics(device_id: str) -> dict:
    """Calculate energy usage metrics for a device.

    Args:
        device_id: The device identifier.

    Returns:
        Energy usage analysis.
    """
    return {
        "device_id": device_id or "THERM-2024-001",
        "monthly_energy_kwh": 145.3,
        "estimated_cost": 21.80,
        "efficiency_rating": "A",
        "vs_average_home": "-15%",
        "carbon_offset_kg": 8.2
    }


# =============================================================================
# PARALLEL AGENT WORKFLOW (Example 4-6)
# =============================================================================

# Independent information gathering agents
purchase_history_agent = Agent(
    model="gemini-2.5-flash",
    name="PurchaseHistoryAgent",
    instruction="""Fetch and summarize the customer's purchase history.

    Use query_order_database to retrieve order information.
    Provide a concise summary of their purchases and loyalty status.""",
    output_key="purchase_data",
    tools=[query_order_database]
)

manual_lookup_agent = Agent(
    model="gemini-2.5-flash",
    name="ManualLookupAgent",
    instruction="""Retrieve the product manual and relevant troubleshooting guides.

    Use fetch_product_manual and get_troubleshooting_guides to gather
    documentation that may help the customer.
    Summarize the key resources available.""",
    output_key="manual_content",
    tools=[fetch_product_manual, get_troubleshooting_guides]
)

usage_analysis_agent = Agent(
    model="gemini-2.5-flash",
    name="UsageAnalysisAgent",
    instruction="""Analyze the device's usage patterns and energy consumption.

    Use query_telemetry_service and calculate_energy_metrics to understand
    how the device is being used and its energy impact.
    Provide insights on usage patterns.""",
    output_key="usage_data",
    tools=[query_telemetry_service, calculate_energy_metrics]
)

# Execute all information gathering concurrently
info_gathering_taskforce = ParallelAgent(
    name="InformationGathering",
    sub_agents=[purchase_history_agent, manual_lookup_agent, usage_analysis_agent]
)

# A synthesis agent processes the combined results
synthesis_agent = Agent(
    model="gemini-2.5-flash",
    name="SynthesisAgent",
    instruction="""Combine information from {purchase_data}, {manual_content},
    and {usage_data} to provide comprehensive support.

    Create a unified response that:
    1. Acknowledges the customer's purchase history and loyalty status
    2. Provides relevant documentation links
    3. Shares usage insights and energy efficiency information
    4. Offers personalized recommendations based on all gathered data

    Be helpful and professional."""
)

# Complete workflow: gather in parallel, then synthesize
support_workflow = SequentialAgent(
    name="ComprehensiveSupport",
    sub_agents=[info_gathering_taskforce, synthesis_agent]
)

# For adk web compatibility - export as root_agent
root_agent = support_workflow
