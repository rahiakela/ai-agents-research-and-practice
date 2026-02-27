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

"""Sequential Agent Sample - The Assembly Line Pattern.

This sample demonstrates SequentialAgent for ordered workflow execution.
Based on Chapter 4, Example 4-5: Warranty Claim Workflow.

Key Concepts:
- SequentialAgent executes sub-agents in strict order
- output_key saves agent output to state for next agent to read
- {placeholder} syntax in instructions reads from state
- Each step must complete before the next begins

Theme: SmartHome Customer Support - Warranty Claim Processing
"""

from google.adk.agents import Agent, SequentialAgent


# =============================================================================
# SIMULATED TOOLS
# =============================================================================
# These tools simulate real operations for demo purposes.

def check_device_logs(device_id: str) -> dict:
    """Check device diagnostic logs.

    Args:
        device_id: The device identifier to check.

    Returns:
        Device log information including error codes.
    """
    # Simulated device logs
    return {
        "device_id": device_id or "THERM-2024-001",
        "error_codes": ["E-WIRE-003", "E-TEMP-SENSOR"],
        "last_error_time": "2025-01-13T14:30:00Z",
        "firmware_version": "2.3.1",
        "status": "error_state"
    }


def analyze_error_patterns(error_codes: list) -> dict:
    """Analyze error patterns to determine root cause.

    Args:
        error_codes: List of error codes from device logs.

    Returns:
        Analysis results including diagnosis.
    """
    # Simulated error pattern analysis
    return {
        "primary_issue": "defective_temperature_sensor",
        "is_hardware_defect": True,
        "is_user_error": False,
        "confidence": 0.95,
        "recommendation": "Hardware replacement required"
    }


def lookup_purchase_date(customer_id: str) -> dict:
    """Look up the purchase date for warranty verification.

    Args:
        customer_id: The customer identifier.

    Returns:
        Purchase information for warranty check.
    """
    # Simulated purchase lookup
    return {
        "customer_id": customer_id or "CUST-12345",
        "product": "Smart Thermostat Pro",
        "purchase_date": "2024-08-15",
        "days_since_purchase": 151,
        "retailer": "SmartHome Direct"
    }


def check_coverage_terms(product_type: str) -> dict:
    """Check warranty coverage terms for the product.

    Args:
        product_type: The type of product.

    Returns:
        Warranty coverage information.
    """
    # Simulated warranty terms
    return {
        "product_type": product_type or "Smart Thermostat",
        "warranty_period_days": 365,
        "covers_hardware_defects": True,
        "covers_user_damage": False,
        "covers_shipping": True,
        "replacement_policy": "New unit replacement"
    }


def initiate_replacement(claim_details: str) -> dict:
    """Initiate the warranty replacement process.

    Args:
        claim_details: Details about the claim.

    Returns:
        Replacement order confirmation.
    """
    # Simulated replacement initiation
    return {
        "claim_id": "WC-2025-00789",
        "status": "approved",
        "replacement_product": "Smart Thermostat Pro (New)",
        "estimated_delivery": "2-3 business days",
        "shipping_method": "Express",
        "tracking_available": True
    }


def send_confirmation(customer_email: str, claim_id: str) -> dict:
    """Send confirmation email to customer.

    Args:
        customer_email: Customer's email address.
        claim_id: The warranty claim ID.

    Returns:
        Email confirmation status.
    """
    # Simulated email sending
    return {
        "email_sent": True,
        "recipient": customer_email or "customer@example.com",
        "claim_id": claim_id or "WC-2025-00789",
        "subject": "Your Warranty Claim Has Been Approved",
        "timestamp": "2025-01-13T15:00:00Z"
    }


# =============================================================================
# SEQUENTIAL AGENT WORKFLOW (Example 4-5)
# =============================================================================

# Step 1: Diagnose the issue
diagnostic_agent = Agent(
    model="gemini-2.5-flash",
    name="DiagnosticAgent",
    instruction="""Analyze the reported issue and determine if it's a product
    defect or user error. Save your conclusion to state.

    When the user reports an issue:
    1. Use check_device_logs to retrieve device diagnostic information
    2. Use analyze_error_patterns to determine the root cause
    3. Provide a clear diagnosis of whether this is a hardware defect or user error

    Be thorough but concise in your analysis.""",
    output_key="diagnosis_result",
    tools=[check_device_logs, analyze_error_patterns]
)

# Step 2: Check warranty eligibility
warranty_check_agent = Agent(
    model="gemini-2.5-flash",
    name="WarrantyCheckAgent",
    instruction="""Based on the diagnosis in {diagnosis_result}, verify if
    this issue is covered under warranty. Check purchase date and coverage terms.

    Steps:
    1. Use lookup_purchase_date to verify when the product was purchased
    2. Use check_coverage_terms to understand what's covered
    3. Determine if the issue qualifies for warranty replacement

    Clearly state whether the warranty covers this issue.""",
    output_key="warranty_status",
    tools=[lookup_purchase_date, check_coverage_terms]
)

# Step 3: Process the claim
claim_processor = Agent(
    model="gemini-2.5-flash",
    name="ClaimProcessor",
    instruction="""If {warranty_status} indicates coverage, process the
    replacement claim. Use details from {diagnosis_result}.

    If covered:
    1. Use initiate_replacement to start the replacement process
    2. Use send_confirmation to notify the customer

    If not covered:
    - Explain why and provide alternative options (repair service, purchase new)

    Provide a complete summary of the claim outcome.""",
    tools=[initiate_replacement, send_confirmation]
)

# Orchestrate the sequence
warranty_claim_workflow = SequentialAgent(
    name="WarrantyClaimWorkflow",
    sub_agents=[diagnostic_agent, warranty_check_agent, claim_processor]
)

# For adk web compatibility - export as root_agent
root_agent = warranty_claim_workflow
