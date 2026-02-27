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

"""Self-Contained MCP Server - Customer Database.

This MCP server simulates a customer database for the MCP Agent sample.
It exposes tools for looking up customer information and order history
via the Model Context Protocol (MCP).

Run this server before starting the ADK agent:
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
from starlette.responses import Response
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
        "member_since": "2022-03-15"
    },
    "jane@example.com": {
        "id": "CUST-002",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "555-0102",
        "status": "active",
        "loyalty_tier": "Platinum",
        "member_since": "2020-08-22"
    },
    "bob@example.com": {
        "id": "CUST-003",
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "phone": "555-0103",
        "status": "inactive",
        "loyalty_tier": "Silver",
        "member_since": "2023-01-10"
    }
}

ORDERS_DB = {
    "CUST-001": [
        {
            "order_id": "ORD-2024-001",
            "date": "2024-08-15",
            "product": "Smart Thermostat Pro",
            "quantity": 1,
            "total": 299.99,
            "status": "delivered"
        },
        {
            "order_id": "ORD-2024-005",
            "date": "2024-11-20",
            "product": "Smart Light Bulb (4-pack)",
            "quantity": 2,
            "total": 159.98,
            "status": "delivered"
        }
    ],
    "CUST-002": [
        {
            "order_id": "ORD-2024-002",
            "date": "2024-06-10",
            "product": "Smart Security Camera",
            "quantity": 3,
            "total": 449.97,
            "status": "delivered"
        },
        {
            "order_id": "ORD-2024-008",
            "date": "2024-12-01",
            "product": "Smart Doorbell Pro",
            "quantity": 1,
            "total": 199.99,
            "status": "processing"
        }
    ],
    "CUST-003": [
        {
            "order_id": "ORD-2023-015",
            "date": "2023-09-05",
            "product": "Smart Plug (2-pack)",
            "quantity": 1,
            "total": 49.99,
            "status": "delivered"
        }
    ]
}

DEVICES_DB = {
    "CUST-001": [
        {
            "device_id": "DEV-THERM-001",
            "product": "Smart Thermostat Pro",
            "registered": "2024-08-20",
            "firmware": "2.3.1",
            "status": "online",
            "last_seen": "2025-01-13T14:30:00Z"
        }
    ],
    "CUST-002": [
        {
            "device_id": "DEV-CAM-001",
            "product": "Smart Security Camera",
            "registered": "2024-06-15",
            "firmware": "1.8.0",
            "status": "online",
            "last_seen": "2025-01-13T14:25:00Z"
        },
        {
            "device_id": "DEV-CAM-002",
            "product": "Smart Security Camera",
            "registered": "2024-06-15",
            "firmware": "1.8.0",
            "status": "offline",
            "last_seen": "2025-01-10T09:00:00Z"
        }
    ]
}


# =============================================================================
# MCP SERVER SETUP
# =============================================================================

# Create MCP server
mcp_server = Server("customer-database-server")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="lookup_customer_by_email",
            description="Look up customer information by email address. Returns customer profile including name, status, and loyalty tier.",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Customer's email address"
                    }
                },
                "required": ["email"]
            }
        ),
        Tool(
            name="get_order_history",
            description="Get the order history for a customer by their customer ID. Returns list of past orders with products and totals.",
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
        ),
        Tool(
            name="get_registered_devices",
            description="Get all devices registered to a customer. Returns device details including firmware version and online status.",
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
        ),
        Tool(
            name="search_customers",
            description="Search for customers by name (partial match). Returns matching customer profiles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_query": {
                        "type": "string",
                        "description": "Name or partial name to search for"
                    }
                },
                "required": ["name_query"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "lookup_customer_by_email":
        email = arguments.get("email", "").lower()
        customer = CUSTOMERS_DB.get(email)
        if customer:
            result = {"found": True, "customer": customer}
        else:
            result = {"found": False, "error": f"No customer found with email: {email}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_order_history":
        customer_id = arguments.get("customer_id", "")
        orders = ORDERS_DB.get(customer_id, [])
        total_spent = sum(order["total"] for order in orders)
        result = {
            "customer_id": customer_id,
            "order_count": len(orders),
            "total_spent": total_spent,
            "orders": orders
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_registered_devices":
        customer_id = arguments.get("customer_id", "")
        devices = DEVICES_DB.get(customer_id, [])
        result = {
            "customer_id": customer_id,
            "device_count": len(devices),
            "devices": devices
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "search_customers":
        name_query = arguments.get("name_query", "").lower()
        matches = [
            customer for customer in CUSTOMERS_DB.values()
            if name_query in customer["name"].lower()
        ]
        result = {
            "query": name_query,
            "matches_found": len(matches),
            "customers": matches
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
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
    print("MCP Customer Database Server")
    print("=" * 60)
    print()
    print("Starting server on http://localhost:8080")
    print()
    print("Available tools:")
    print("  - lookup_customer_by_email: Find customer by email")
    print("  - get_order_history: Get customer's order history")
    print("  - get_registered_devices: Get customer's devices")
    print("  - search_customers: Search customers by name")
    print()
    print("Sample customers in database:")
    for email, customer in CUSTOMERS_DB.items():
        print(f"  - {customer['name']} ({email})")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    uvicorn.run(app, host="localhost", port=8080)
