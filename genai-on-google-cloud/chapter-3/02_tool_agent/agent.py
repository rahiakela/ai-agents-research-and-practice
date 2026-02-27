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

"""
Tool Agent - Adding Intelligence Through Tools

This agent demonstrates how to extend agent capabilities with custom tools,
matching Example 3-3 from Chapter 3.

Tools are Python functions that the agent can call to perform actions or
retrieve information that isn't available in its training data.

Key concepts:
- Function tools with docstrings (ADK uses these for tool descriptions)
- Type hints for parameter validation
- Return types for structured responses
- Tool execution flow and visibility in ADK web

Theme: SmartHome Customer Support (consistent with Chapter 3)
"""

import random
from datetime import datetime, timedelta
from google.adk.agents import Agent


# Example 3-3: Order lookup tool
def look_up_order(order_id: str) -> dict:
    """Retrieves order information from our database.

    Args:
        order_id: The customer's order number

    Returns:
        Order details including status, items, and tracking info
    """
    # Simulated order data - in production, query your database
    orders = {
        "ORD-12345": {
            "order_id": "ORD-12345",
            "status": "shipped",
            "items": [
                {"name": "SmartHome Doorbell Pro", "quantity": 1, "price": 199.99},
                {"name": "Smart Thermostat", "quantity": 1, "price": 149.99}
            ],
            "total": 349.98,
            "tracking_number": "1Z999AA10123456784",
            "carrier": "UPS",
            "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "order_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        },
        "ORD-12346": {
            "order_id": "ORD-12346",
            "status": "processing",
            "items": [
                {"name": "Smart Light Bulb 4-Pack", "quantity": 2, "price": 49.99}
            ],
            "total": 99.98,
            "tracking_number": None,
            "carrier": None,
            "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "order_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        },
        "ORD-12347": {
            "order_id": "ORD-12347",
            "status": "delivered",
            "items": [
                {"name": "Smart Lock", "quantity": 1, "price": 249.99}
            ],
            "total": 249.99,
            "tracking_number": "1Z999AA10123456785",
            "carrier": "UPS",
            "estimated_delivery": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "delivered_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "order_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        }
    }

    if order_id in orders:
        return orders[order_id]

    return {
        "error": f"Order {order_id} not found. Please verify the order number.",
        "suggestion": "Order numbers start with 'ORD-' followed by 5 digits."
    }


def check_warranty_status(product_id: str) -> dict:
    """Check the warranty status for a SmartHome product.

    Args:
        product_id: The product serial number or ID

    Returns:
        Warranty information including coverage dates and status
    """
    # Simulated warranty data
    warranties = {
        "SH-DOORBELL-001": {
            "product_id": "SH-DOORBELL-001",
            "product_name": "SmartHome Doorbell Pro",
            "warranty_status": "active",
            "purchase_date": "2024-06-15",
            "warranty_expires": "2026-06-15",
            "coverage_type": "Full replacement",
            "days_remaining": 540
        },
        "SH-THERMO-002": {
            "product_id": "SH-THERMO-002",
            "product_name": "Smart Thermostat",
            "warranty_status": "active",
            "purchase_date": "2024-08-01",
            "warranty_expires": "2026-08-01",
            "coverage_type": "Full replacement",
            "days_remaining": 607
        },
        "SH-LOCK-003": {
            "product_id": "SH-LOCK-003",
            "product_name": "Smart Lock",
            "warranty_status": "expired",
            "purchase_date": "2022-01-15",
            "warranty_expires": "2024-01-15",
            "coverage_type": "None - warranty expired",
            "days_remaining": 0
        }
    }

    if product_id in warranties:
        return warranties[product_id]

    return {
        "error": f"Product {product_id} not found in warranty database.",
        "suggestion": "Please provide the serial number found on your device."
    }


def get_product_info(product_name: str) -> dict:
    """Get detailed information about a SmartHome product.

    Args:
        product_name: The name or type of product to look up

    Returns:
        Product details including features, price, and availability
    """
    products = {
        "doorbell": {
            "name": "SmartHome Doorbell Pro",
            "price": 199.99,
            "in_stock": True,
            "features": [
                "1080p HD video",
                "Two-way audio",
                "Night vision",
                "Motion detection",
                "Mobile app alerts"
            ],
            "warranty": "2 years",
            "installation": "DIY or professional available"
        },
        "thermostat": {
            "name": "Smart Thermostat",
            "price": 149.99,
            "in_stock": True,
            "features": [
                "Learning temperature preferences",
                "Energy usage reports",
                "Remote control via app",
                "Works with voice assistants",
                "Geofencing support"
            ],
            "warranty": "2 years",
            "installation": "Professional recommended"
        },
        "lock": {
            "name": "Smart Lock",
            "price": 249.99,
            "in_stock": False,
            "restock_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "features": [
                "Keyless entry",
                "Remote lock/unlock",
                "Guest access codes",
                "Auto-lock feature",
                "Activity log"
            ],
            "warranty": "2 years",
            "installation": "DIY friendly"
        }
    }

    # Search by keyword
    product_name_lower = product_name.lower()
    for key, product in products.items():
        if key in product_name_lower or product_name_lower in product["name"].lower():
            return product

    return {
        "error": f"Product '{product_name}' not found.",
        "available_products": ["SmartHome Doorbell Pro", "Smart Thermostat", "Smart Lock"]
    }


# Example 3-3: Agent with tools
root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products.

Your capabilities:
- Look up order status and tracking information
- Check product warranty status
- Provide product information and specifications

When helping customers:
1. Use the appropriate tool to get accurate information
2. Present information clearly and helpfully
3. Offer to help with related questions

Be friendly, professional, and thorough in your responses.""",
    tools=[look_up_order, check_warranty_status, get_product_info]
)
