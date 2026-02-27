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

"""A2A Client Sample - Consuming Remote Agents.

This sample demonstrates how to consume a remote A2A-compatible agent
using RemoteA2aAgent.
Based on Chapter 4, Example 4-12: Remote Agent Consumption.

Key Concepts:
- RemoteA2aAgent connects to an A2A server via its Agent Card
- Agent Card provides automatic discovery of capabilities
- Remote agents integrate seamlessly as sub_agents
- Coordinator orchestrates local and remote agents together

Theme: SmartHome Customer Support - Coordinator with Remote Billing

Prerequisites:
    Start the A2A billing server first (from 05_a2a_server):
        cd ../05_a2a_server
        uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
"""

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent


# =============================================================================
# LOCAL DIAGNOSTIC TOOLS
# =============================================================================

def check_device_status(device_id: str) -> dict:
    """Check the current status of a smart home device.

    Args:
        device_id: The device identifier.

    Returns:
        Device status information.
    """
    # Simulated device status
    devices = {
        "DEV-THERM-001": {
            "device_id": "DEV-THERM-001",
            "product": "Smart Thermostat Pro",
            "status": "online",
            "firmware": "2.3.1",
            "last_reading": {"temperature": 72, "humidity": 45},
            "alerts": ["firmware_update_available"]
        },
        "DEV-CAM-001": {
            "device_id": "DEV-CAM-001",
            "product": "Smart Security Camera",
            "status": "online",
            "firmware": "1.8.0",
            "last_recording": "2025-01-13T14:00:00Z",
            "alerts": []
        },
        "DEV-LIGHT-001": {
            "device_id": "DEV-LIGHT-001",
            "product": "Smart Light Bulb",
            "status": "offline",
            "firmware": "1.2.0",
            "last_seen": "2025-01-10T09:30:00Z",
            "alerts": ["connectivity_issue"]
        }
    }

    return devices.get(device_id, {
        "device_id": device_id,
        "status": "not_found",
        "error": f"Device {device_id} not found in system"
    })


def lookup_error_codes(error_code: str) -> dict:
    """Look up the meaning of a device error code.

    Args:
        error_code: The error code to look up.

    Returns:
        Error code details and resolution steps.
    """
    error_codes = {
        "E001": {
            "code": "E001",
            "name": "WiFi Connection Lost",
            "description": "Device cannot connect to WiFi network",
            "severity": "medium",
            "resolution": [
                "Check WiFi router is powered on",
                "Verify correct WiFi password",
                "Move device closer to router",
                "Reset device network settings"
            ]
        },
        "E002": {
            "code": "E002",
            "name": "Sensor Malfunction",
            "description": "Temperature sensor reading incorrectly",
            "severity": "high",
            "resolution": [
                "Calibrate sensor in device settings",
                "Check device placement away from heat sources",
                "If persists, request replacement under warranty"
            ]
        },
        "E003": {
            "code": "E003",
            "name": "Firmware Corruption",
            "description": "Device firmware is corrupted",
            "severity": "critical",
            "resolution": [
                "Factory reset the device",
                "Re-pair with the SmartHome app",
                "Contact support if issue persists"
            ]
        }
    }

    return error_codes.get(error_code.upper(), {
        "code": error_code,
        "name": "Unknown Error",
        "description": "Error code not found in database",
        "severity": "unknown",
        "resolution": ["Contact customer support for assistance"]
    })


def run_device_diagnostics(device_id: str) -> dict:
    """Run comprehensive diagnostics on a device.

    Args:
        device_id: The device to diagnose.

    Returns:
        Diagnostic results.
    """
    return {
        "device_id": device_id,
        "diagnostic_run": True,
        "tests": {
            "connectivity": {"status": "pass", "latency_ms": 45},
            "sensor_accuracy": {"status": "pass", "variance": 0.5},
            "power_supply": {"status": "pass", "voltage": 5.1},
            "memory_usage": {"status": "warning", "used_percent": 78},
            "firmware_integrity": {"status": "pass", "checksum_valid": True}
        },
        "overall_health": "good",
        "recommendations": [
            "Consider updating firmware to latest version",
            "Memory usage slightly high - restart recommended"
        ]
    }


# =============================================================================
# REMOTE A2A AGENT CONNECTION (Example 4-12)
# =============================================================================

# Connect to the remote billing agent via its Agent Card
# This agent is running from 05_a2a_server on port 8001
billing_agent = RemoteA2aAgent(
    name="BillingAgent",
    description="Specialist for billing inquiries, refunds, and payment issues",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)


# =============================================================================
# COORDINATOR AGENT (Example 4-12)
# =============================================================================

coordinator = Agent(
    model="gemini-2.5-flash",
    name="CustomerServiceCoordinator",
    description="Main customer service coordinator that routes requests to specialists",
    instruction="""You are the customer service coordinator for SmartHome Inc.
    You handle customer inquiries by intelligently routing to the right specialists.

    Your capabilities:
    1. Technical Support (handled locally):
       - Check device status
       - Look up error codes
       - Run device diagnostics

    2. Billing Support (handled by remote BillingAgent):
       - Billing history inquiries
       - Refund requests
       - Payment issues
       - Account credits

    Routing guidelines:
    - For technical issues (device problems, errors, diagnostics), use your local tools
    - For billing questions (charges, refunds, payments), delegate to BillingAgent
    - For mixed issues (e.g., defective device causing billing impact), handle both:
      First diagnose technically, then coordinate with billing for any adjustments

    Always be helpful and professional. Verify customer identity when needed.
    Summarize your findings clearly and explain next steps.""",
    sub_agents=[billing_agent],  # Remote agent via A2A
    tools=[
        check_device_status,
        lookup_error_codes,
        run_device_diagnostics
    ]
)

# For adk web compatibility - export as root_agent
root_agent = coordinator
