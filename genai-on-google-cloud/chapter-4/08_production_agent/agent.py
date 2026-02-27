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

"""Production Agent Sample - Enterprise-Ready Patterns.

This sample demonstrates production concerns for agent systems:
- Security schemes in Agent Cards (Example 4-15)
- A2A extensions (Examples 4-16, 4-17)
- Distributed tracing (Examples 4-18, 4-19, 4-20)
- Agent versioning (Examples 4-21, 4-22)

Based on Chapter 4, Examples 4-15 to 4-22: Production Realities.

Key Concepts:
- Security: OAuth2, API keys, scopes
- Extensions: Custom capabilities activation
- Tracing: Distributed trace propagation via W3C headers
- Versioning: Semantic versioning of Agent Cards

Theme: SmartHome Enterprise Billing Service
"""

import logging
import os
from datetime import datetime
from typing import Optional

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a


# =============================================================================
# LOGGING WITH TRACE CONTEXT (Examples 4-18, 4-19, 4-20)
# =============================================================================

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("billing_agent")


def get_trace_context() -> dict:
    """Extract trace context from environment/headers.

    In production, this would extract from incoming request headers:
    - traceparent: W3C Trace Context header
    - tracestate: Additional vendor-specific trace data

    Returns:
        Trace context dictionary.
    """
    # Simulated trace context (in production, extract from request headers)
    return {
        "trace_id": os.environ.get("TRACE_ID", "4bf92f3577b34da6a3ce929d0e0e4736"),
        "span_id": os.environ.get("SPAN_ID", "00f067aa0ba902b7"),
        "trace_flags": "01"  # Sampled
    }


def log_with_trace(level: str, message: str, **kwargs):
    """Log with trace context for distributed tracing (Example 4-20).

    Args:
        level: Log level (info, warning, error).
        message: Log message.
        **kwargs: Additional context.
    """
    trace = get_trace_context()
    log_entry = {
        "message": message,
        "trace_id": trace["trace_id"],
        "span_id": trace["span_id"],
        **kwargs
    }

    log_func = getattr(logger, level, logger.info)
    log_func(f"[trace:{trace['trace_id'][:8]}] {message} | context={kwargs}")


# =============================================================================
# BILLING AGENT TOOLS WITH AUDIT LOGGING
# =============================================================================

def query_billing_history(
    customer_id: str,
    months: int = 6,
    include_disputes: bool = False
) -> dict:
    """Query billing history with audit logging.

    Args:
        customer_id: The customer identifier.
        months: Number of months of history.
        include_disputes: Whether to include dispute records.

    Returns:
        Billing history data.
    """
    log_with_trace(
        "info",
        "Querying billing history",
        customer_id=customer_id,
        months=months,
        include_disputes=include_disputes
    )

    invoices = [
        {"invoice_id": "INV-2024-001", "amount": 89.99, "status": "paid"},
        {"invoice_id": "INV-2024-002", "amount": 89.99, "status": "paid"},
        {"invoice_id": "INV-2024-003", "amount": 136.99, "status": "paid", "disputed": True}
    ]

    if not include_disputes:
        invoices = [inv for inv in invoices if not inv.get("disputed")]

    log_with_trace(
        "info",
        "Billing history retrieved",
        customer_id=customer_id,
        invoice_count=len(invoices)
    )

    return {
        "customer_id": customer_id,
        "months": months,
        "invoices": invoices,
        "total_billed": sum(inv["amount"] for inv in invoices)
    }


def process_refund(
    invoice_id: str,
    reason: str,
    approved_by: Optional[str] = None
) -> dict:
    """Process a full refund with audit trail.

    Args:
        invoice_id: Invoice to refund.
        reason: Reason for refund.
        approved_by: Approver for large refunds.

    Returns:
        Refund confirmation.
    """
    log_with_trace(
        "info",
        "Processing refund",
        invoice_id=invoice_id,
        reason=reason,
        approved_by=approved_by
    )

    refund_id = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    result = {
        "refund_id": refund_id,
        "invoice_id": invoice_id,
        "amount": 89.99,
        "reason": reason,
        "status": "processed",
        "processed_at": datetime.now().isoformat(),
        "audit_trail": {
            "action": "refund_processed",
            "actor": "BillingAgent",
            "approved_by": approved_by,
            "timestamp": datetime.now().isoformat()
        }
    }

    log_with_trace(
        "info",
        "Refund processed successfully",
        refund_id=refund_id,
        invoice_id=invoice_id,
        amount=result["amount"]
    )

    return result


def process_partial_refund(
    invoice_id: str,
    percentage: float,
    reason: str
) -> dict:
    """Process a partial refund (v2 capability).

    Args:
        invoice_id: Invoice to partially refund.
        percentage: Percentage to refund (0-100).
        reason: Reason for partial refund.

    Returns:
        Partial refund confirmation.
    """
    log_with_trace(
        "info",
        "Processing partial refund",
        invoice_id=invoice_id,
        percentage=percentage,
        reason=reason
    )

    original_amount = 89.99
    refund_amount = round(original_amount * (percentage / 100), 2)
    refund_id = f"PREF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    result = {
        "refund_id": refund_id,
        "invoice_id": invoice_id,
        "original_amount": original_amount,
        "refund_percentage": percentage,
        "refund_amount": refund_amount,
        "reason": reason,
        "status": "processed",
        "version": "2.0.0"  # Indicates v2 capability
    }

    log_with_trace(
        "info",
        "Partial refund processed",
        refund_id=refund_id,
        refund_amount=refund_amount
    )

    return result


def resolve_dispute(
    dispute_id: str,
    resolution: str,
    credit_amount: Optional[float] = None
) -> dict:
    """Resolve a billing dispute (v2 capability).

    Args:
        dispute_id: The dispute identifier.
        resolution: Resolution type (credit, reject, escalate).
        credit_amount: Amount to credit if resolution is 'credit'.

    Returns:
        Dispute resolution confirmation.
    """
    log_with_trace(
        "info",
        "Resolving dispute",
        dispute_id=dispute_id,
        resolution=resolution,
        credit_amount=credit_amount
    )

    result = {
        "dispute_id": dispute_id,
        "resolution": resolution,
        "credit_amount": credit_amount,
        "status": "resolved",
        "resolved_at": datetime.now().isoformat(),
        "version": "2.0.0"
    }

    log_with_trace(
        "info",
        "Dispute resolved",
        dispute_id=dispute_id,
        resolution=resolution
    )

    return result


def check_extension_activated(extension_uri: str, headers: dict) -> bool:
    """Check if an extension is activated via headers (Example 4-17).

    Args:
        extension_uri: The extension URI to check.
        headers: Request headers.

    Returns:
        True if extension is activated.
    """
    activated_extensions = headers.get("X-A2A-Extensions", "").split(",")
    return extension_uri.strip() in [ext.strip() for ext in activated_extensions]


# =============================================================================
# BILLING AGENT DEFINITION
# =============================================================================

# Version 2 agent with full capabilities
billing_agent = Agent(
    model="gemini-2.5-flash",
    name="BillingAgent",
    description="Enterprise billing specialist with refunds, partial refunds, and dispute resolution",
    instruction="""You are an enterprise billing specialist for SmartHome Inc.

    Version 2.0 Capabilities:
    1. Query billing history (with dispute filtering)
    2. Process full refunds
    3. Process partial refunds (NEW in v2)
    4. Resolve billing disputes (NEW in v2)

    Security Requirements:
    - All operations are logged with trace context
    - Refunds over $50 require approval notation
    - PII is masked in logs when extension is active

    When handling requests:
    1. Always query billing history first to understand context
    2. For refunds, document the reason clearly
    3. For disputes, attempt automatic resolution before escalation
    4. Log all actions with appropriate trace context

    Be professional, accurate, and maintain audit trails.""",
    tools=[
        query_billing_history,
        process_refund,
        process_partial_refund,
        resolve_dispute
    ]
)


# =============================================================================
# A2A SERVER WITH PRODUCTION CONFIGURATION
# =============================================================================

# Create A2A app with the agent
a2a_app = to_a2a(billing_agent)

# For local adk web testing
root_agent = billing_agent


# =============================================================================
# VERSIONED AGENT ACCESS (Example 4-22)
# =============================================================================

def get_versioned_agent_card_url(version: str) -> str:
    """Get the Agent Card URL for a specific version.

    Args:
        version: Version string (e.g., "1.0.0", "2.0.0").

    Returns:
        Agent Card URL for the specified version.
    """
    base_url = "https://billing-service.company.com"
    major_version = version.split(".")[0]
    return f"{base_url}/v{major_version}/.well-known/agent-card.json"


# Example usage for clients (Example 4-22):
#
# # Old coordinator using v1
# billing_agent_v1 = RemoteA2aAgent(
#     name="BillingAgent",
#     agent_card=get_versioned_agent_card_url("1.0.0")
#     # URL: https://billing-service.company.com/v1/.well-known/agent-card.json
# )
#
# # New coordinator using v2
# billing_agent_v2 = RemoteA2aAgent(
#     name="BillingAgent",
#     agent_card=get_versioned_agent_card_url("2.0.0")
#     # URL: https://billing-service.company.com/v2/.well-known/agent-card.json
# )


# =============================================================================
# DISTRIBUTED TRACE EXAMPLE (Example 4-19)
# =============================================================================

TRACE_EXAMPLE = """
TRACE: 4bf92f3577b34da6a3ce929d0e0e4736
├─ Span: CustomerServiceCoordinator.process_request (2.1s)
│  ├─ Span: TechnicalAgent.diagnose (0.8s)
│  │  └─ Span: LLM.call (0.6s)
│  └─ Span: BillingAgent.analyze (1.2s) [Remote via A2A]
│     ├─ Span: query_billing_history (0.4s)
│     └─ Span: LLM.call (0.7s)
"""


# =============================================================================
# EXTENSION ACTIVATION EXAMPLE (Example 4-17)
# =============================================================================

EXTENSION_EXAMPLE = """
# Activating extensions via headers:

POST /agents/billing HTTP/1.1
Host: billing-service.company.com
Content-Type: application/json
X-A2A-Extensions: https://company.com/ext/audit-logging/v1

{"message": "Process refund for INV-2024-001"}

# The agent checks for extension activation:
if check_extension_activated("https://company.com/ext/audit-logging/v1", request.headers):
    enable_detailed_audit_logging()
"""
