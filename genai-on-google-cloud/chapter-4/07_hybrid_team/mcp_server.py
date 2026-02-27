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

"""MCP Server for Hybrid Team Sample - Customer Database.

This MCP server provides customer database access for the hybrid team sample.
It exposes tools for customer lookup and device/usage history.

Run this server before starting the hybrid agent:
    python mcp_server.py

The server will start on http://localhost:8080
"""

import json
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import uvicorn


# =============================================================================
# SIMULATED DATABASE
# =============================================================================

CUSTOMERS_DB = {
    "john@example.com": {
        "id": "CUST-001",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0101",
        "status": "active",
        "loyalty_tier": "Gold",
        "member_since": "2022-03-15",
        "devices": ["DEV-THERM-001"],
        "support_notes": "Experienced user, prefers technical details"
    },
    "jane@example.com": {
        "id": "CUST-002",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "555-0102",
        "status": "active",
        "loyalty_tier": "Platinum",
        "member_since": "2020-08-22",
        "devices": ["DEV-CAM-001", "DEV-CAM-002", "DEV-DOORBELL-001"],
        "support_notes": "High-value customer, prioritize satisfaction"
    }
}

DEVICE_USAGE_DB = {
    "DEV-THERM-001": {
        "device_id": "DEV-THERM-001",
        "product": "Smart Thermostat Pro",
        "owner": "CUST-001",
        "installed": "2024-08-20",
        "usage_30d": {
            "hours_active": 720,
            "avg_daily_adjustments": 4.2,
            "energy_kwh": 145.3,
            "estimated_cost": 21.80
        },
        "anomalies": [
            {
                "date": "2024-11-10",
                "type": "sensor_malfunction",
                "description": "Temperature sensor reading 5°F high",
                "impact": "HVAC over-cooling, increased energy use",
                "estimated_excess_cost": 47.00
            }
        ]
    },
    "DEV-CAM-001": {
        "device_id": "DEV-CAM-001",
        "product": "Smart Security Camera",
        "owner": "CUST-002",
        "installed": "2024-06-15",
        "usage_30d": {
            "hours_recording": 480,
            "motion_events": 156,
            "cloud_storage_gb": 12.3
        },
        "anomalies": []
    }
}


# =============================================================================
# MCP SERVER SETUP
# =============================================================================

mcp_server = Server("customer-database-hybrid")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="lookup_customer",
            description="Look up customer information by email or customer ID. Returns full customer profile including devices and support notes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Customer email or ID (e.g., john@example.com or CUST-001)"
                    }
                },
                "required": ["identifier"]
            }
        ),
        Tool(
            name="get_device_usage_history",
            description="Get detailed usage history and any anomalies for a device. Includes energy consumption, usage patterns, and detected issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID (e.g., DEV-THERM-001)"
                    }
                },
                "required": ["device_id"]
            }
        ),
        Tool(
            name="get_customer_devices",
            description="List all devices registered to a customer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (e.g., CUST-001)"
                    }
                },
                "required": ["customer_id"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "lookup_customer":
        identifier = arguments.get("identifier", "")
        # Try email first
        customer = CUSTOMERS_DB.get(identifier.lower())
        if not customer:
            # Try matching by ID
            for c in CUSTOMERS_DB.values():
                if c["id"] == identifier.upper():
                    customer = c
                    break
        if customer:
            result = {"found": True, "customer": customer}
        else:
            result = {"found": False, "error": f"Customer not found: {identifier}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_device_usage_history":
        device_id = arguments.get("device_id", "").upper()
        usage = DEVICE_USAGE_DB.get(device_id)
        if usage:
            result = {"found": True, "device_usage": usage}
        else:
            result = {"found": False, "error": f"Device not found: {device_id}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_customer_devices":
        customer_id = arguments.get("customer_id", "").upper()
        devices = []
        for device_id, device in DEVICE_USAGE_DB.items():
            if device.get("owner") == customer_id:
                devices.append({
                    "device_id": device_id,
                    "product": device["product"],
                    "installed": device["installed"]
                })
        result = {
            "customer_id": customer_id,
            "device_count": len(devices),
            "devices": devices
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


# =============================================================================
# SSE TRANSPORT SETUP
# =============================================================================

sse_transport = SseServerTransport("/sse")


async def handle_sse(request):
    """Handle SSE connection for MCP."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


# Create Starlette app with SSE endpoint at /sse
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/", app=sse_transport.get_sse_app()),
    ],
)


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Customer Database Server (Hybrid Team)")
    print("=" * 60)
    print()
    print("Starting server on http://localhost:8080")
    print()
    print("Available tools:")
    print("  - lookup_customer: Find customer by email/ID")
    print("  - get_device_usage_history: Get device usage and anomalies")
    print("  - get_customer_devices: List customer's devices")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    uvicorn.run(app, host="localhost", port=8080)
