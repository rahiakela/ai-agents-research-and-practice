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

"""SmartHome Support Agent - Agent Under Test.

This agent is a simplified version of the SmartHome support agent from Chapter 3.
It provides tools for device management that we'll evaluate using ADK's
evaluation framework.

Based on Chapter 5, Example 5-2: Agent Tool Usage Evaluation.
"""

from google.adk.agents import Agent


# =============================================================================
# TOOLS FOR EVALUATION
# =============================================================================

def check_device_status(device_type: str, device_id: str = None) -> dict:
    """Check the status of a smart home device.

    Args:
        device_type: Type of device (thermostat, camera, light, doorbell).
        device_id: Optional specific device ID.

    Returns:
        Device status information.
    """
    # Simulated device statuses
    devices = {
        "thermostat": {
            "device_id": "THERM-001",
            "type": "thermostat",
            "status": "online",
            "current_temp": 72,
            "target_temp": 70,
            "mode": "cooling",
            "battery": "N/A (wired)"
        },
        "camera": {
            "device_id": "CAM-001",
            "type": "camera",
            "status": "online",
            "recording": True,
            "motion_detected": False,
            "battery": "85%"
        },
        "light": {
            "device_id": "LIGHT-001",
            "type": "light",
            "status": "online",
            "power": "on",
            "brightness": 75,
            "color": "warm white"
        },
        "doorbell": {
            "device_id": "DOOR-001",
            "type": "doorbell",
            "status": "online",
            "last_ring": "2025-01-14T10:30:00Z",
            "battery": "92%"
        }
    }

    device = devices.get(device_type.lower())
    if device:
        return {"found": True, "device": device}
    return {"found": False, "error": f"Unknown device type: {device_type}"}


def set_device_setting(
    device_type: str,
    setting_name: str,
    setting_value: str
) -> dict:
    """Update a setting on a smart home device.

    Args:
        device_type: Type of device to configure.
        setting_name: Name of the setting to change.
        setting_value: New value for the setting.

    Returns:
        Confirmation of the setting change.
    """
    valid_settings = {
        "thermostat": ["target_temp", "mode", "schedule"],
        "camera": ["recording", "motion_sensitivity", "night_vision"],
        "light": ["power", "brightness", "color"],
        "doorbell": ["volume", "motion_alerts", "chime_type"]
    }

    device_settings = valid_settings.get(device_type.lower(), [])
    if setting_name not in device_settings:
        return {
            "success": False,
            "error": f"Invalid setting '{setting_name}' for {device_type}",
            "valid_settings": device_settings
        }

    return {
        "success": True,
        "device_type": device_type,
        "setting": setting_name,
        "old_value": "previous_value",
        "new_value": setting_value,
        "message": f"Successfully set {setting_name} to {setting_value}"
    }


def get_device_history(device_type: str, hours: int = 24) -> dict:
    """Get recent activity history for a device.

    Args:
        device_type: Type of device.
        hours: Number of hours of history to retrieve.

    Returns:
        Recent device activity and events.
    """
    histories = {
        "thermostat": {
            "device_type": "thermostat",
            "period_hours": hours,
            "events": [
                {"time": "2025-01-14T08:00:00Z", "event": "temperature_change", "value": "68°F → 72°F"},
                {"time": "2025-01-14T06:30:00Z", "event": "mode_change", "value": "heating → cooling"},
                {"time": "2025-01-14T00:00:00Z", "event": "schedule_activated", "value": "night_mode"}
            ],
            "avg_temp": 70.5,
            "energy_usage_kwh": 4.2
        },
        "camera": {
            "device_type": "camera",
            "period_hours": hours,
            "events": [
                {"time": "2025-01-14T10:15:00Z", "event": "motion_detected", "value": "front_yard"},
                {"time": "2025-01-14T08:45:00Z", "event": "person_detected", "value": "delivery_driver"},
                {"time": "2025-01-14T07:30:00Z", "event": "recording_started", "value": "scheduled"}
            ],
            "motion_events": 12,
            "storage_used_gb": 2.3
        }
    }

    history = histories.get(device_type.lower())
    if history:
        return {"found": True, "history": history}
    return {"found": False, "error": f"No history available for: {device_type}"}


def troubleshoot_device(device_type: str, issue_description: str) -> dict:
    """Get troubleshooting steps for a device issue.

    Args:
        device_type: Type of device with the issue.
        issue_description: Description of the problem.

    Returns:
        Troubleshooting steps and recommendations.
    """
    troubleshooting_guides = {
        "thermostat": {
            "not_cooling": [
                "Check if the mode is set to 'cooling'",
                "Verify the target temperature is below current temperature",
                "Ensure HVAC system breaker is on",
                "Check air filter - replace if dirty"
            ],
            "not_responding": [
                "Check Wi-Fi connection",
                "Power cycle the thermostat",
                "Verify the C-wire connection",
                "Factory reset if issues persist"
            ]
        },
        "camera": {
            "offline": [
                "Check Wi-Fi signal strength",
                "Power cycle the camera",
                "Verify camera is within router range",
                "Check for firmware updates"
            ],
            "poor_quality": [
                "Clean the camera lens",
                "Adjust camera position for better lighting",
                "Check bandwidth - reduce other network usage",
                "Lower video quality settings if bandwidth limited"
            ]
        }
    }

    device_guides = troubleshooting_guides.get(device_type.lower(), {})

    # Find matching issue
    for issue_key, steps in device_guides.items():
        if issue_key in issue_description.lower():
            return {
                "found": True,
                "device_type": device_type,
                "issue": issue_key,
                "steps": steps,
                "estimated_time": "5-10 minutes"
            }

    return {
        "found": False,
        "device_type": device_type,
        "message": "No specific troubleshooting guide found",
        "recommendation": "Please contact support for assistance"
    }


# =============================================================================
# SMARTHOME SUPPORT AGENT
# =============================================================================

support_agent = Agent(
    model="gemini-2.5-flash",
    name="SmartHomeSupportAgent",
    description="Customer support agent for SmartHome devices",
    instruction="""You are a helpful SmartHome customer support agent.
    You help customers with their smart home devices including thermostats,
    cameras, lights, and doorbells.

    When helping customers:
    1. First check the device status to understand the current state
    2. If there's an issue, use troubleshooting guides
    3. Help adjust settings when requested
    4. Provide device history when customers ask about recent activity

    Be concise and helpful. Always confirm actions you've taken.""",
    tools=[
        check_device_status,
        set_device_setting,
        get_device_history,
        troubleshoot_device
    ]
)

# For adk web compatibility
root_agent = support_agent
