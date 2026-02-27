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
Guardrails Agent - Safety and Security Through Callbacks

This agent demonstrates ADK's callback system for implementing safety
guardrails and content moderation, matching Examples 3-20, 3-21, and 3-22.

Callbacks allow you to:
- Validate inputs before they reach the model
- Filter outputs before they reach the user
- Control tool execution
- Log and audit agent behavior

Key concepts:
- before_model_callback: Intercept/modify input
- after_model_callback: Intercept/modify output
- before_tool_callback: Control tool execution
- after_tool_callback: Validate tool results
- LongRunningFunctionTool: Async operations requiring approval (Example 3-20)
- FunctionTool with require_confirmation: Human-in-the-loop (Example 3-21)

Theme: SmartHome Customer Support with content moderation
"""

import re
import random
from datetime import datetime
from typing import Optional, Any

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext, LongRunningFunctionTool, FunctionTool
from google.genai import types


# =============================================================================
# CONFIGURATION - Customizable Guardrails
# =============================================================================

# Words/phrases to block in input
BLOCKED_INPUT_PATTERNS = [
    r"\b(hack|exploit|bypass)\b",
    r"\b(password|credential|secret)\s*(is|:)",
    r"ignore\s+(previous|all)\s+instructions",
]

# Patterns to redact from output
OUTPUT_REDACTION_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]"),  # SSN pattern
    (r"\b\d{16}\b", "[CARD REDACTED]"),  # Credit card
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL REDACTED]"),
]

# Tools that require extra validation
SENSITIVE_TOOLS = ["process_refund", "update_account"]

# Maximum message length
MAX_INPUT_LENGTH = 2000


# =============================================================================
# CALLBACK IMPLEMENTATIONS
# =============================================================================

def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Called before each model invocation. Can modify the request or
    return a response to skip the model entirely.

    Args:
        callback_context: Context with state and invocation info
        llm_request: The request about to be sent to the model

    Returns:
        None to continue, or LlmResponse to skip model and return directly
    """
    # Get the latest user message
    if not llm_request.contents:
        return None

    last_content = llm_request.contents[-1]
    if not hasattr(last_content, 'parts') or not last_content.parts:
        return None

    user_text = ""
    for part in last_content.parts:
        if hasattr(part, 'text'):
            user_text += part.text

    # Check input length
    if len(user_text) > MAX_INPUT_LENGTH:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=(
                    "I apologize, but your message is too long. "
                    f"Please limit your message to {MAX_INPUT_LENGTH} characters."
                ))]
            )
        )

    # Check for blocked patterns
    user_text_lower = user_text.lower()
    for pattern in BLOCKED_INPUT_PATTERNS:
        if re.search(pattern, user_text_lower, re.IGNORECASE):
            # Log the blocked attempt
            print(f"[GUARDRAIL] Blocked input matching pattern: {pattern}")

            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=(
                        "I'm sorry, but I can't process that request. "
                        "If you have a legitimate customer service question, "
                        "please rephrase it and I'll be happy to help."
                    ))]
                )
            )

    # Log successful pass-through
    print(f"[GUARDRAIL] Input passed validation ({len(user_text)} chars)")
    return None  # Continue to model


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse
) -> LlmResponse:
    """
    Called after each model response. Can modify the response
    before it reaches the user.

    Args:
        callback_context: Context with state and invocation info
        llm_response: The response from the model

    Returns:
        The (potentially modified) response
    """
    if not llm_response.content or not llm_response.content.parts:
        return llm_response

    modified = False
    new_parts = []

    for part in llm_response.content.parts:
        if hasattr(part, 'text') and part.text:
            text = part.text

            # Apply redaction patterns
            for pattern, replacement in OUTPUT_REDACTION_PATTERNS:
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    modified = True
                    text = new_text

            new_parts.append(types.Part(text=text))
        else:
            new_parts.append(part)

    if modified:
        print("[GUARDRAIL] Output redacted sensitive information")
        llm_response.content.parts = new_parts

    return llm_response


def before_tool_callback(
    callback_context: CallbackContext,
    tool_name: str,
    tool_args: dict
) -> Optional[dict]:
    """
    Called before each tool execution. Can modify arguments or
    return a result to skip tool execution.

    Args:
        callback_context: Context with state and invocation info
        tool_name: Name of the tool being called
        tool_args: Arguments being passed to the tool

    Returns:
        None to continue, or dict to skip tool and return directly
    """
    print(f"[GUARDRAIL] Tool call: {tool_name} with args: {tool_args}")

    # Extra validation for sensitive tools
    if tool_name in SENSITIVE_TOOLS:
        # In production, you might check user permissions here
        print(f"[GUARDRAIL] Sensitive tool {tool_name} - extra validation")

        # Example: Block refunds over a certain amount
        if tool_name == "process_refund":
            amount = tool_args.get("amount", 0)
            if amount > 500:
                return {
                    "success": False,
                    "error": "Refunds over $500 require manager approval. "
                            "Please contact support at 1-800-EXAMPLE."
                }

    return None  # Continue with tool execution


def after_tool_callback(
    callback_context: CallbackContext,
    tool_name: str,
    tool_args: dict,
    tool_result: dict
) -> dict:
    """
    Called after each tool execution. Can modify the result
    before it's returned to the model.

    Args:
        callback_context: Context with state and invocation info
        tool_name: Name of the tool that was called
        tool_args: Arguments that were passed
        tool_result: Result from the tool

    Returns:
        The (potentially modified) result
    """
    # Log tool results for auditing
    print(f"[GUARDRAIL] Tool {tool_name} completed: {tool_result.get('success', 'N/A')}")

    # Redact sensitive data from tool results
    if isinstance(tool_result, dict):
        for key, value in tool_result.items():
            if isinstance(value, str):
                for pattern, replacement in OUTPUT_REDACTION_PATTERNS:
                    tool_result[key] = re.sub(pattern, replacement, value)

    return tool_result


# =============================================================================
# CUSTOMER SERVICE TOOLS
# =============================================================================

def check_order_status(
    order_id: str,
    tool_context: ToolContext = None
) -> dict:
    """Check the status of an order.

    Args:
        order_id: The order ID to look up
        tool_context: Provided by ADK

    Returns:
        Order status information
    """
    # Simulated order data
    orders = {
        "ORD-001": {"status": "shipped", "carrier": "UPS", "eta": "2 days"},
        "ORD-002": {"status": "processing", "eta": "5-7 days"},
        "ORD-003": {"status": "delivered", "delivered_date": "2024-01-15"},
    }

    if order_id in orders:
        return {
            "success": True,
            "order_id": order_id,
            **orders[order_id]
        }

    return {
        "success": False,
        "error": f"Order {order_id} not found. Please check the order ID."
    }


def get_product_info(
    product_name: str,
    tool_context: ToolContext = None
) -> dict:
    """Get information about a product.

    Args:
        product_name: Name or ID of the product
        tool_context: Provided by ADK

    Returns:
        Product information
    """
    products = {
        "laptop": {"name": "Pro Laptop 15", "price": 1299.99, "in_stock": True},
        "phone": {"name": "SmartPhone X", "price": 899.99, "in_stock": True},
        "tablet": {"name": "TabletPro", "price": 599.99, "in_stock": False},
    }

    product_key = product_name.lower()
    for key, info in products.items():
        if key in product_key or product_key in info["name"].lower():
            return {"success": True, **info}

    return {
        "success": False,
        "error": f"Product '{product_name}' not found."
    }


def process_refund(
    order_id: str,
    amount: float,
    reason: str,
    tool_context: ToolContext = None
) -> dict:
    """Process a refund for an order.

    Args:
        order_id: The order to refund
        amount: Refund amount in dollars
        reason: Reason for the refund
        tool_context: Provided by ADK

    Returns:
        Refund confirmation
    """
    # Note: Large refunds are blocked by before_tool_callback

    if tool_context:
        refunds = tool_context.state.get("user:refunds", [])
        refunds.append({
            "order_id": order_id,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        tool_context.state["user:refunds"] = refunds

    return {
        "success": True,
        "refund_id": f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_id": order_id,
        "amount": amount,
        "message": f"Refund of ${amount:.2f} processed. Allow 3-5 business days."
    }


def update_account(
    field: str,
    new_value: str,
    tool_context: ToolContext = None
) -> dict:
    """Update user account information.

    Args:
        field: The field to update (email, phone, address)
        new_value: The new value
        tool_context: Provided by ADK

    Returns:
        Update confirmation
    """
    allowed_fields = ["email", "phone", "address", "name"]

    if field.lower() not in allowed_fields:
        return {
            "success": False,
            "error": f"Cannot update '{field}'. Allowed: {', '.join(allowed_fields)}"
        }

    if tool_context:
        account = tool_context.state.get("user:account", {})
        account[field.lower()] = new_value
        tool_context.state["user:account"] = account

    return {
        "success": True,
        "field": field,
        "message": f"Your {field} has been updated successfully."
    }


# =============================================================================
# LONG-RUNNING FUNCTION TOOL (Example 3-20)
# =============================================================================

# Example 3-20: LongRunningFunctionTool for async operations
def request_manager_approval(purpose: str, amount: float) -> dict[str, Any]:
    """Initiates a request for manager approval for an expense or refund.

    This operation is asynchronous - it creates a ticket and returns immediately.
    The actual approval happens later.

    Args:
        purpose: Description of what the approval is for
        amount: The dollar amount requiring approval

    Returns:
        Ticket information for tracking the approval request
    """
    ticket_id = f"TICKET-{random.randint(1000, 9999)}"
    return {
        "status": "pending",
        "ticket_id": ticket_id,
        "amount": amount,
        "purpose": purpose,
        "message": f"Approval request created: {ticket_id}. A manager will review within 24 hours.",
        "estimated_response": "24 hours"
    }


def check_approval_status(ticket_id: str) -> dict[str, Any]:
    """Check the status of a pending approval request.

    Args:
        ticket_id: The ticket ID from request_manager_approval

    Returns:
        Current status of the approval request
    """
    # Simulate random approval status
    statuses = ["pending", "approved", "denied"]
    status = random.choice(statuses)

    result = {
        "ticket_id": ticket_id,
        "status": status
    }

    if status == "approved":
        result["message"] = "Request approved by manager. Proceeding with action."
        result["approved_by"] = "Manager"
        result["approved_at"] = datetime.now().isoformat()
    elif status == "denied":
        result["message"] = "Request denied. Please contact support for alternatives."
        result["reason"] = "Exceeds policy limits"
    else:
        result["message"] = "Still awaiting manager review."

    return result


# Wrap the function as a LongRunningFunctionTool (Example 3-20)
approval_tool = LongRunningFunctionTool(func=request_manager_approval)


# =============================================================================
# FUNCTION TOOL WITH CONFIRMATION (Example 3-21)
# =============================================================================

# Example 3-21: FunctionTool with require_confirmation for HITL
def delete_account_data(
    data_type: str,
    confirm: bool = False,
    tool_context: ToolContext = None
) -> dict:
    """Delete specific customer data (requires confirmation).

    This is a destructive operation that requires explicit user confirmation.

    Args:
        data_type: Type of data to delete (order_history, preferences, all)
        confirm: Must be True to proceed with deletion
        tool_context: Provided by ADK

    Returns:
        Deletion status
    """
    if not confirm:
        return {
            "status": "confirmation_required",
            "message": f"Are you sure you want to delete {data_type}? This cannot be undone.",
            "action_needed": "Set confirm=True to proceed"
        }

    # Simulated deletion
    return {
        "status": "deleted",
        "data_type": data_type,
        "message": f"Successfully deleted {data_type}",
        "timestamp": datetime.now().isoformat()
    }


# Wrap with require_confirmation for human-in-the-loop (Example 3-21)
# Note: This requires the user to explicitly confirm before execution
delete_data_tool = FunctionTool(
    func=delete_account_data,
    # require_confirmation=True  # Uncomment when using ADK with HITL support
)


# =============================================================================
# ROOT AGENT WITH CALLBACKS
# =============================================================================

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products.

You can help customers with:
- Checking order status
- Product information and availability
- Processing refunds (with limits)
- Updating account information
- Requesting manager approval for large refunds

Guidelines:
- Be polite and professional
- Protect customer privacy
- Don't share sensitive information
- Escalate issues you can't handle
- For refunds over $500, request manager approval

Note: Some operations have limits (e.g., large refunds need approval).
Always explain next steps clearly to the customer.""",
    tools=[
        check_order_status,
        get_product_info,
        process_refund,
        update_account,
        approval_tool,  # Example 3-20: LongRunningFunctionTool
        check_approval_status,
        delete_data_tool  # Example 3-21: Confirmation required
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)
