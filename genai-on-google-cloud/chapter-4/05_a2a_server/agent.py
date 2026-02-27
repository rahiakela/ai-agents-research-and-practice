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

"""A2A Server Sample - Exposing Agents as Services.

This sample demonstrates how to expose an ADK agent via the A2A
(Agent-to-Agent) protocol using to_a2a().
Based on Chapter 4, Examples 4-10 and 4-11.

Key Concepts:
- to_a2a() converts an Agent to an A2A-compatible ASGI app
- Automatic Agent Card generation at /.well-known/agent-card.json
- Standard deployment via uvicorn or any ASGI server
- Agent Card describes capabilities for client discovery

Theme: SmartHome Billing Service - Finance Team's Agent

To run:
    uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
"""

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a


# =============================================================================
# BILLING AGENT TOOLS
# =============================================================================

def query_billing_history(customer_id: str, months: int = 6) -> dict:
    """Query billing history for a customer.

    Args:
        customer_id: The customer identifier.
        months: Number of months of history to retrieve (default 6).

    Returns:
        Billing history with invoices and payments.
    """
    # Simulated billing data
    invoices = [
        {
            "invoice_id": "INV-2024-001",
            "date": "2024-12-01",
            "amount": 89.99,
            "description": "Monthly Smart Home Subscription",
            "status": "paid"
        },
        {
            "invoice_id": "INV-2024-002",
            "date": "2024-11-01",
            "amount": 89.99,
            "description": "Monthly Smart Home Subscription",
            "status": "paid"
        },
        {
            "invoice_id": "INV-2024-003",
            "date": "2024-10-01",
            "amount": 89.99,
            "description": "Monthly Smart Home Subscription",
            "status": "paid"
        }
    ]

    # Check for any anomalies
    anomalies = []
    if customer_id == "CUST-001":
        anomalies.append({
            "invoice_id": "INV-2024-SPECIAL",
            "date": "2024-11-15",
            "amount": 47.00,
            "description": "Energy overage charge",
            "status": "paid",
            "flag": "potential_dispute"
        })

    return {
        "customer_id": customer_id,
        "months_retrieved": months,
        "invoices": invoices + anomalies,
        "total_billed": sum(inv["amount"] for inv in invoices + anomalies),
        "anomalies_found": len(anomalies)
    }


def calculate_refund_amount(
    invoice_id: str,
    reason: str,
    partial_percentage: float = 100.0
) -> dict:
    """Calculate the refund amount for an invoice.

    Args:
        invoice_id: The invoice to refund.
        reason: Reason for the refund.
        partial_percentage: Percentage to refund (default 100%).

    Returns:
        Calculated refund details.
    """
    # Simulated invoice lookup
    invoice_amounts = {
        "INV-2024-001": 89.99,
        "INV-2024-002": 89.99,
        "INV-2024-003": 89.99,
        "INV-2024-SPECIAL": 47.00
    }

    original_amount = invoice_amounts.get(invoice_id, 0)
    refund_amount = original_amount * (partial_percentage / 100.0)

    return {
        "invoice_id": invoice_id,
        "original_amount": original_amount,
        "refund_percentage": partial_percentage,
        "refund_amount": round(refund_amount, 2),
        "reason": reason,
        "approval_required": refund_amount > 50.0,
        "estimated_processing": "3-5 business days"
    }


def check_payment_status(invoice_id: str) -> dict:
    """Check the payment status of an invoice.

    Args:
        invoice_id: The invoice to check.

    Returns:
        Payment status details.
    """
    statuses = {
        "INV-2024-001": {"status": "paid", "paid_date": "2024-12-05", "method": "credit_card"},
        "INV-2024-002": {"status": "paid", "paid_date": "2024-11-03", "method": "bank_transfer"},
        "INV-2024-003": {"status": "paid", "paid_date": "2024-10-02", "method": "credit_card"},
        "INV-2024-SPECIAL": {"status": "paid", "paid_date": "2024-11-18", "method": "auto_charge"}
    }

    return {
        "invoice_id": invoice_id,
        **statuses.get(invoice_id, {"status": "not_found", "error": "Invoice not found"})
    }


def process_credit(customer_id: str, amount: float, reason: str) -> dict:
    """Process a credit to a customer's account.

    Args:
        customer_id: The customer to credit.
        amount: Amount to credit.
        reason: Reason for the credit.

    Returns:
        Credit processing confirmation.
    """
    import random
    import string
    from datetime import datetime

    credit_id = "CRD-" + "".join(random.choices(string.digits, k=6))

    return {
        "credit_id": credit_id,
        "customer_id": customer_id,
        "amount": amount,
        "reason": reason,
        "status": "approved" if amount <= 100 else "pending_approval",
        "applied_to_account": True,
        "processed_at": datetime.now().isoformat(),
        "next_invoice_adjustment": True
    }


def generate_invoice(customer_id: str, items: list, due_date: str) -> dict:
    """Generate a new invoice for a customer.

    Args:
        customer_id: The customer to invoice.
        items: List of items/services to invoice.
        due_date: Payment due date (YYYY-MM-DD).

    Returns:
        Generated invoice details.
    """
    import random
    import string
    from datetime import datetime

    invoice_id = "INV-" + "".join(random.choices(string.digits, k=8))

    # Calculate total
    total = sum(item.get("amount", 0) for item in items) if items else 0

    return {
        "invoice_id": invoice_id,
        "customer_id": customer_id,
        "items": items or [{"description": "Service charge", "amount": 0}],
        "subtotal": total,
        "tax": round(total * 0.08, 2),
        "total": round(total * 1.08, 2),
        "due_date": due_date,
        "status": "pending",
        "generated_at": datetime.now().isoformat()
    }


# =============================================================================
# BILLING AGENT DEFINITION (Example 4-10)
# =============================================================================

billing_agent = Agent(
    model="gemini-2.5-flash",
    name="BillingAgent",
    description="Specialist for billing inquiries, refunds, and payment processing",
    instruction="""You are a billing specialist for SmartHome Inc. You analyze charges,
    process refunds, handle billing disputes, and ensure compliance with financial policies.

    Your capabilities:
    1. Query billing history for customers
    2. Calculate refund amounts (full or partial)
    3. Check payment status on invoices
    4. Process account credits
    5. Generate new invoices

    When handling billing issues:
    1. Always review the customer's billing history first
    2. Identify any anomalies or incorrect charges
    3. Calculate appropriate refunds or credits
    4. Explain your reasoning clearly
    5. Process approved adjustments

    For refunds over $50, note that supervisor approval is required.
    Be professional, accurate, and empathetic to customer concerns.""",
    tools=[
        query_billing_history,
        calculate_refund_amount,
        check_payment_status,
        process_credit,
        generate_invoice
    ]
)


# =============================================================================
# A2A SERVER EXPOSURE (Examples 4-10 and 4-11)
# =============================================================================

# Expose this agent via A2A - generates Agent Card automatically
# The Agent Card will be available at: /.well-known/agent-card.json
a2a_app = to_a2a(billing_agent, port=8001)

# For local adk web testing (when not using A2A)
root_agent = billing_agent


# =============================================================================
# RUN INSTRUCTIONS
# =============================================================================
#
# To start the A2A server (Example 4-11):
#
#     uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
#
# Once running, verify the Agent Card:
#
#     curl http://localhost:8001/.well-known/agent-card.json
#
# The agent is now accessible to any A2A client at:
#
#     http://localhost:8001
#
# See 06_a2a_client for how to consume this agent.
