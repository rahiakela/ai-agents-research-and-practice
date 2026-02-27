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
Multimodal Agent - Image Analysis and Artifact Storage

This agent demonstrates ADK's multimodal capabilities and artifact storage,
matching Examples 3-17 and 3-19 from Chapter 3.

Key concepts:
- Handling image inputs for damage assessment
- Artifact storage with save_artifact()
- user: prefix for cross-session persistence
- types.Part.from_bytes() for binary data
- list_artifacts() for retrieval

Theme: SmartHome Customer Support - Product Damage Assessment
"""

import json
import random
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types


# =============================================================================
# DAMAGE ASSESSMENT TOOLS (Example 3-17)
# =============================================================================

# Example 3-17: Multimodal damage analysis with artifact saving
async def analyze_product_damage_with_report(tool_context: ToolContext) -> dict:
    """Analyze product damage from customer-provided images and generate a report.

    This function analyzes the damage visible in uploaded images and creates
    a JSON report that is saved as an artifact for future reference.

    Args:
        tool_context: Provided by ADK for state and artifact access

    Returns:
        Damage assessment with report reference
    """
    # Generate case number
    case_number = f"DMG-{random.randint(10000, 99999)}"

    # Simulated damage assessment (in production, this would use vision analysis)
    assessment = {
        "damage_severity": "moderate",
        "damage_type": "electrical issue",
        "warranty_coverage": "Covered - component failure",
        "recommended_action": "Warranty replacement approved"
    }

    # Create detailed report content
    report_content = {
        "case_number": case_number,
        "assessment_date": datetime.now().isoformat(),
        "product_category": "SmartHome Device",
        "damage_assessment": assessment,
        "inspector_notes": "Visual inspection completed via customer-submitted images",
        "next_steps": [
            "Customer will receive replacement device",
            "Return label will be emailed within 24 hours",
            "Original device should be returned within 14 days"
        ]
    }

    # Example 3-17: Save as artifact for permanent storage
    report_artifact = types.Part.from_bytes(
        data=json.dumps(report_content, indent=2).encode('utf-8'),
        mime_type="application/json"
    )

    # Use user: prefix for cross-session persistence
    filename = f"user:damage_report_{case_number}.json"
    version = await tool_context.save_artifact(
        filename=filename,
        artifact=report_artifact
    )

    # Also track in user state
    reports = tool_context.state.get("user:damage_reports", [])
    reports.append({
        "case_number": case_number,
        "filename": filename,
        "version": version,
        "date": datetime.now().isoformat()
    })
    tool_context.state["user:damage_reports"] = reports

    return {
        "case_number": case_number,
        "assessment": assessment,
        "report_saved": True,
        "report_filename": filename,
        "report_version": version,
        "message": f"Damage report saved. Case number: {case_number}"
    }


async def assess_warranty_from_image(
    product_type: str,
    damage_description: str,
    tool_context: ToolContext = None
) -> dict:
    """Assess warranty coverage based on visible damage.

    Args:
        product_type: Type of SmartHome product
        damage_description: Description of visible damage
        tool_context: Provided by ADK

    Returns:
        Warranty assessment
    """
    # Warranty coverage rules
    covered_damage = ["component failure", "electrical", "defect", "malfunction"]
    not_covered = ["water damage", "physical abuse", "dropped", "cracked screen"]

    damage_lower = damage_description.lower()

    is_covered = any(term in damage_lower for term in covered_damage)
    is_excluded = any(term in damage_lower for term in not_covered)

    if is_excluded:
        coverage = "Not covered - physical damage or user error"
        action = "Paid repair or replacement options available"
    elif is_covered:
        coverage = "Covered under warranty"
        action = "Free replacement or repair"
    else:
        coverage = "Pending review"
        action = "Additional inspection may be required"

    return {
        "product_type": product_type,
        "damage_description": damage_description,
        "warranty_coverage": coverage,
        "recommended_action": action,
        "next_step": "Submit damage photos for final assessment"
    }


# Example 3-19: List and retrieve artifacts
async def list_user_documents(tool_context: ToolContext) -> dict:
    """List all documents and reports saved for this customer.

    Example 3-19: Artifact management for cross-session access.

    Args:
        tool_context: Provided by ADK

    Returns:
        List of saved documents
    """
    # Get saved damage reports from state
    damage_reports = tool_context.state.get("user:damage_reports", [])

    # In a full implementation, you could also use:
    # artifacts = await tool_context.list_artifacts()

    if not damage_reports:
        return {
            "message": "No documents found",
            "documents": []
        }

    return {
        "total_documents": len(damage_reports),
        "documents": damage_reports,
        "note": "Use case number to reference specific reports"
    }


async def retrieve_damage_report(
    case_number: str,
    tool_context: ToolContext = None
) -> dict:
    """Retrieve a previously saved damage report.

    Args:
        case_number: The case number of the report to retrieve
        tool_context: Provided by ADK

    Returns:
        The saved report or error message
    """
    if tool_context:
        damage_reports = tool_context.state.get("user:damage_reports", [])

        for report in damage_reports:
            if report["case_number"] == case_number:
                # In production, you would load the artifact:
                # artifact = await tool_context.load_artifact(report["filename"])
                return {
                    "found": True,
                    "case_number": case_number,
                    "filename": report["filename"],
                    "created_date": report["date"],
                    "version": report.get("version", 0)
                }

        return {
            "found": False,
            "message": f"No report found for case {case_number}"
        }

    return {"error": "Context not available"}


def get_product_visual_guide(product_name: str) -> dict:
    """Get visual troubleshooting guide for a product.

    Args:
        product_name: Name of the SmartHome product

    Returns:
        Troubleshooting guide
    """
    guides = {
        "doorbell": {
            "product": "SmartHome Doorbell Pro",
            "common_issues": [
                {"issue": "No power", "visual_check": "LED should be solid blue"},
                {"issue": "Poor video", "visual_check": "Check for lens obstruction"},
                {"issue": "Connection lost", "visual_check": "WiFi indicator should be green"}
            ],
            "image_submission_tips": [
                "Take photo of the device mounted",
                "Include close-up of any visible damage",
                "Photograph the LED status lights"
            ]
        },
        "thermostat": {
            "product": "Smart Thermostat",
            "common_issues": [
                {"issue": "Blank screen", "visual_check": "Check for power at C-wire"},
                {"issue": "Wrong reading", "visual_check": "Verify sensor placement"},
                {"issue": "Not heating", "visual_check": "Check HVAC connection lights"}
            ],
            "image_submission_tips": [
                "Photo of thermostat display",
                "Photo of wiring connections",
                "Photo showing installation location"
            ]
        }
    }

    product_key = product_name.lower()
    for key, guide in guides.items():
        if key in product_key:
            return guide

    return {
        "message": f"No specific guide for {product_name}",
        "general_tips": [
            "Take clear, well-lit photos",
            "Include photos from multiple angles",
            "Photograph any visible damage or issues"
        ]
    }


# =============================================================================
# ROOT AGENT
# =============================================================================

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products.

You specialize in product damage assessment and warranty claims:

1. **Analyze Damage**: When customers share images of damaged products,
   assess the damage and determine warranty coverage.

2. **Generate Reports**: Create detailed damage reports saved as artifacts
   that persist across sessions.

3. **Track Cases**: Maintain records of all damage assessments and reports.

4. **Provide Guidance**: Help customers photograph issues correctly
   for accurate assessment.

When a customer reports damage:
1. Ask for product type and damage description
2. Request images if not provided
3. Analyze and assess warranty coverage
4. Generate and save a formal damage report
5. Provide next steps for resolution

All reports are saved with user: prefix for cross-session access.""",
    tools=[
        analyze_product_damage_with_report,
        assess_warranty_from_image,
        list_user_documents,
        retrieve_damage_report,
        get_product_visual_guide
    ]
)
