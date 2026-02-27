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
Multi-Agent - Tools vs Subagents Decision Framework

This agent demonstrates the hybrid architecture pattern from Examples 3-5 and 3-7,
where a root agent has BOTH tools for simple tasks AND sub-agents for complex workflows.

Key concepts:
- When to use tools vs sub-agents
- Creating agent hierarchies with sub_agents=[]
- Hybrid architecture: root agent with tools AND subagents
- Agent delegation and handoff

Decision Framework:
- Use TOOLS for: deterministic operations, API calls, calculations
- Use SUB-AGENTS for: complex reasoning, multi-step workflows, specialized knowledge

Theme: SmartHome Customer Support (consistent with Chapter 3)
"""

import random
from datetime import datetime, timedelta
from google.adk.agents import Agent


# =============================================================================
# TOOLS FOR ROOT AGENT (Simple operations)
# =============================================================================

def look_up_order(order_id: str) -> dict:
    """Retrieves order information from our database.

    Args:
        order_id: The customer's order number

    Returns:
        Order details including status, items, and tracking info
    """
    orders = {
        "ORD-12345": {
            "order_id": "ORD-12345",
            "status": "shipped",
            "items": [
                {"name": "SmartHome Doorbell Pro", "quantity": 1, "price": 199.99}
            ],
            "total": 199.99,
            "tracking_number": "1Z999AA10123456784",
            "carrier": "UPS",
            "order_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        },
        "ORD-12346": {
            "order_id": "ORD-12346",
            "status": "delivered",
            "items": [
                {"name": "Smart Thermostat", "quantity": 1, "price": 149.99}
            ],
            "total": 149.99,
            "delivered_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "order_date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        }
    }

    if order_id in orders:
        return orders[order_id]

    return {"error": f"Order {order_id} not found"}


def check_shipping_status(tracking_number: str) -> dict:
    """Check the current shipping status for a package.

    Args:
        tracking_number: The carrier tracking number

    Returns:
        Current shipping status and location
    """
    # Simulated tracking data
    return {
        "tracking_number": tracking_number,
        "status": "in_transit",
        "current_location": "Distribution Center - San Jose, CA",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "carrier": "UPS"
    }


# =============================================================================
# RETURNS SPECIALIST SUB-AGENT (Example 3-5)
# Complex workflow requiring specialized handling
# =============================================================================

def check_return_eligibility(order_id: str, reason: str) -> dict:
    """Check if an order is eligible for return.

    Args:
        order_id: The order number to check
        reason: Reason for the return request

    Returns:
        Eligibility status and policy details
    """
    # Simulate policy check - deterministic rules
    valid_reasons = ["defective", "wrong_item", "not_as_described", "changed_mind"]
    reason_key = reason.lower().replace(" ", "_")

    # Orders are eligible within 30 days
    is_eligible = True
    return_window_days = 30

    return {
        "order_id": order_id,
        "eligible": is_eligible,
        "reason": reason,
        "return_window_days": return_window_days,
        "policy": "Full refund for defective items, 15% restocking fee for change of mind",
        "next_step": "Calculate refund amount" if is_eligible else "Contact support for exceptions"
    }


def calculate_refund_amount(order_id: str, reason: str) -> dict:
    """Calculate the refund amount based on return reason and policy.

    Args:
        order_id: The order number
        reason: Reason for the return

    Returns:
        Refund calculation details
    """
    # Simulated order lookup and calculation
    order_totals = {
        "ORD-12345": 199.99,
        "ORD-12346": 149.99
    }

    original_amount = order_totals.get(order_id, 100.00)

    # Apply policy rules
    if reason.lower() in ["defective", "wrong_item", "not_as_described"]:
        refund_amount = original_amount
        restocking_fee = 0
    else:
        restocking_fee = round(original_amount * 0.15, 2)
        refund_amount = round(original_amount - restocking_fee, 2)

    return {
        "order_id": order_id,
        "original_amount": original_amount,
        "restocking_fee": restocking_fee,
        "refund_amount": refund_amount,
        "refund_method": "Original payment method",
        "processing_time": "3-5 business days"
    }


def create_return_label(order_id: str, customer_address: str) -> dict:
    """Generate a prepaid return shipping label.

    Args:
        order_id: The order number for the return
        customer_address: Customer's return address

    Returns:
        Return label details and instructions
    """
    label_number = f"RET{random.randint(100000, 999999)}"

    return {
        "order_id": order_id,
        "return_label_number": label_number,
        "carrier": "UPS",
        "label_url": f"https://smarthome.example.com/returns/{label_number}/label.pdf",
        "drop_off_locations": "Any UPS Store or authorized drop-off point",
        "instructions": [
            "Print the return label",
            "Pack item securely in original packaging if available",
            "Attach label to outside of package",
            "Drop off at any UPS location",
            "Keep receipt as proof of shipment"
        ],
        "valid_until": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    }


# Example 3-5: Returns specialist sub-agent
returns_agent = Agent(
    name="ReturnsSpecialist",
    model="gemini-2.5-flash",
    description="Specialist for handling product returns and refunds",
    instruction="""You are a returns specialist. Guide customers through the return process
with empathy and clear policy explanations.

Your workflow:
1. Check return eligibility using the order ID and return reason
2. Calculate the refund amount based on the policy
3. Generate a return shipping label for the customer

Be understanding about customer frustrations with products, while clearly
explaining our return policies. Always provide the full refund breakdown
so customers know exactly what to expect.""",
    tools=[check_return_eligibility, calculate_refund_amount, create_return_label]
)


# =============================================================================
# Example 3-7: HYBRID ARCHITECTURE
# Root agent with BOTH tools AND sub-agents
# =============================================================================

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products.

You have direct tools for simple queries:
- look_up_order: Quick order status checks
- check_shipping_status: Package tracking

For complex return workflows, delegate to the ReturnsSpecialist who can:
- Check return eligibility
- Calculate refund amounts
- Generate return labels

Guidelines:
1. Handle simple order/shipping questions directly with your tools
2. For returns and refunds, hand off to ReturnsSpecialist
3. Be friendly and helpful throughout
4. Always confirm the customer's issue is resolved before ending""",
    tools=[look_up_order, check_shipping_status],  # Simple tools for common tasks
    sub_agents=[returns_agent]  # Specialist for complex workflows
)
