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

"""MCP Agent Sample - The Language of Tools.

This sample demonstrates McpToolset for connecting to external tool servers
via the Model Context Protocol (MCP).
Based on Chapter 4, Example 4-9: MCP Tool Integration.

Key Concepts:
- McpToolset wraps MCP servers as ADK tools
- SseConnectionParams for HTTP-based MCP connections
- StdioConnectionParams for local subprocess MCP servers
- tool_name_prefix for namespacing (avoid collisions)

Theme: SmartHome Customer Support - Database-Connected Agent

Prerequisites:
    Start the MCP server first:
        python mcp_server.py
"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams


# =============================================================================
# MCP TOOLSET CONFIGURATION (Example 4-9)
# =============================================================================

# Connect to an MCP server that exposes your customer database
# The MCP server runs at localhost:8080 (start it with: python mcp_server.py)
customer_db_tools = McpToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse"  # SSE endpoint of our MCP server
    ),
    # Prefix all tool names to avoid collisions with other tools
    # Tools become: CustomerDB_lookup_customer_by_email, CustomerDB_get_order_history, etc.
    tool_filter=None  # Accept all tools from this MCP server
)


# =============================================================================
# ADDITIONAL LOCAL TOOLS
# =============================================================================

def check_warranty_status(product_name: str, purchase_date: str) -> dict:
    """Check if a product is still under warranty.

    Args:
        product_name: Name of the product.
        purchase_date: Date of purchase (YYYY-MM-DD).

    Returns:
        Warranty status information.
    """
    from datetime import datetime, timedelta

    # Parse purchase date
    try:
        purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    # Most products have 2-year warranty
    warranty_end = purchase + timedelta(days=730)
    today = datetime.now()

    is_valid = today < warranty_end
    days_remaining = (warranty_end - today).days if is_valid else 0

    return {
        "product": product_name,
        "purchase_date": purchase_date,
        "warranty_end_date": warranty_end.strftime("%Y-%m-%d"),
        "warranty_valid": is_valid,
        "days_remaining": max(0, days_remaining),
        "coverage": "Full replacement or repair" if is_valid else "Expired"
    }


def create_support_ticket(
    customer_id: str,
    issue_summary: str,
    priority: str = "medium"
) -> dict:
    """Create a support ticket for a customer issue.

    Args:
        customer_id: The customer's ID.
        issue_summary: Brief description of the issue.
        priority: Ticket priority (low, medium, high, urgent).

    Returns:
        Created ticket information.
    """
    import random
    import string
    from datetime import datetime

    ticket_id = "TKT-" + "".join(random.choices(string.digits, k=6))

    return {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue_summary": issue_summary,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "estimated_response": "24 hours" if priority in ["low", "medium"] else "4 hours"
    }


# =============================================================================
# MCP-ENABLED SUPPORT AGENT
# =============================================================================

support_agent = Agent(
    model="gemini-2.5-flash",
    name="MCPSupportAgent",
    instruction="""You are a customer support agent with access to the customer database
    via MCP tools and additional support capabilities.

    Available capabilities:
    1. Customer Database (via MCP):
       - Look up customers by email
       - View order history
       - Check registered devices
       - Search customers by name

    2. Local Support Tools:
       - Check warranty status for products
       - Create support tickets

    When helping customers:
    1. First, look up their information using their email
    2. Review their order history and registered devices
    3. Check warranty status if they have product issues
    4. Create support tickets for issues that need follow-up

    Be helpful, professional, and thorough. Always verify customer identity
    before sharing sensitive information.""",
    tools=[
        customer_db_tools,       # MCP tools from the database server
        check_warranty_status,   # Local warranty checker
        create_support_ticket    # Local ticket creation
    ]
)

# For adk web compatibility - export as root_agent
root_agent = support_agent
