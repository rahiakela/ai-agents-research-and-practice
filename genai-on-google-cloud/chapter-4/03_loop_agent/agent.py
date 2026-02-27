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

"""Loop Agent Sample - The Iterative Refiner Pattern.

This sample demonstrates LoopAgent for iterative execution with escalation.
Based on Chapter 4, Examples 4-7 and 4-8: Progressive Troubleshooting.

Key Concepts:
- LoopAgent executes sub-agents repeatedly until termination
- max_iterations provides a safety limit
- escalate=True in tool_context.actions terminates the loop early
- Progressive refinement through iteration

Theme: SmartHome Customer Support - Progressive Troubleshooting
"""

from google.adk.agents import Agent, LoopAgent


# =============================================================================
# SIMULATED TOOLS
# =============================================================================

def lookup_troubleshooting_steps(product_type: str, issue_category: str) -> dict:
    """Look up troubleshooting steps from the knowledge base.

    Args:
        product_type: Type of product (e.g., "thermostat", "light", "camera").
        issue_category: Category of issue (e.g., "connectivity", "display", "power").

    Returns:
        Troubleshooting steps for the given issue.
    """
    steps_db = {
        ("thermostat", "connectivity"): [
            "Step 1: Check if the device is powered on",
            "Step 2: Verify WiFi network is working",
            "Step 3: Move device closer to router",
            "Step 4: Reset network settings on device",
            "Step 5: Factory reset and re-pair"
        ],
        ("thermostat", "display"): [
            "Step 1: Check if display brightness is turned up",
            "Step 2: Power cycle the device",
            "Step 3: Check for firmware updates",
            "Step 4: Inspect for physical damage",
            "Step 5: Replace the unit"
        ],
        ("thermostat", "temperature"): [
            "Step 1: Verify location away from heat sources",
            "Step 2: Calibrate temperature sensor in settings",
            "Step 3: Check HVAC filter",
            "Step 4: Run system diagnostic",
            "Step 5: Schedule technician visit"
        ]
    }
    key = (product_type.lower(), issue_category.lower())
    return {
        "product_type": product_type,
        "issue_category": issue_category,
        "steps": steps_db.get(key, [
            "Step 1: Power cycle the device",
            "Step 2: Check all connections",
            "Step 3: Update firmware",
            "Step 4: Factory reset",
            "Step 5: Contact support"
        ])
    }


def check_known_issues(product_type: str, symptoms: str) -> dict:
    """Check for known issues matching the symptoms.

    Args:
        product_type: Type of product.
        symptoms: Description of symptoms.

    Returns:
        Any known issues and their resolutions.
    """
    known_issues = [
        {
            "product": "Smart Thermostat Pro",
            "issue": "WiFi disconnects after firmware 2.3.1",
            "symptoms": ["connectivity", "disconnection", "wifi"],
            "resolution": "Downgrade to firmware 2.3.0 or wait for 2.3.2 patch"
        },
        {
            "product": "Smart Thermostat Pro",
            "issue": "Display flicker in cold temperatures",
            "symptoms": ["display", "flicker", "cold"],
            "resolution": "Move device away from exterior walls; firmware fix pending"
        }
    ]

    matches = []
    for issue in known_issues:
        if any(s in symptoms.lower() for s in issue["symptoms"]):
            matches.append(issue)

    return {
        "query_symptoms": symptoms,
        "known_issues_found": len(matches),
        "issues": matches
    }


def prompt_user_for_feedback(suggested_solution: str) -> dict:
    """Prompt the user to test the suggested solution and provide feedback.

    Args:
        suggested_solution: The solution to test.

    Returns:
        Simulated user feedback.
    """
    # Simulated responses - in production this would wait for actual user input
    # For demo purposes, we cycle through different responses
    import random
    responses = [
        {"tested": True, "result": "still_broken", "details": "Tried that, still not connecting"},
        {"tested": True, "result": "partial", "details": "It connected briefly but dropped again"},
        {"tested": True, "result": "resolved", "details": "That worked! It's connecting now"},
        {"tested": False, "result": "need_help", "details": "I don't understand how to do that"}
    ]
    # Weight towards not resolved early to show loop behavior
    weights = [0.4, 0.3, 0.2, 0.1]
    response = random.choices(responses, weights=weights)[0]
    return {
        "solution_tested": suggested_solution,
        "user_feedback": response
    }


def analyze_test_results(feedback: dict) -> dict:
    """Analyze the test results from user feedback.

    Args:
        feedback: User feedback dictionary.

    Returns:
        Analysis of whether the issue is resolved.
    """
    result = feedback.get("result", "unknown")
    analysis = {
        "resolved": result == "resolved",
        "partial_success": result == "partial",
        "needs_escalation": result == "need_help",
        "should_continue": result in ["still_broken", "partial"],
        "recommendation": ""
    }

    if result == "resolved":
        analysis["recommendation"] = "Issue resolved. Close the support case."
    elif result == "partial":
        analysis["recommendation"] = "Partial success. Try a more advanced solution."
    elif result == "still_broken":
        analysis["recommendation"] = "Solution didn't work. Escalate to next step."
    elif result == "need_help":
        analysis["recommendation"] = "User needs assistance. Provide clearer instructions."

    return analysis


def check_resolution(solution_status: str, tool_context) -> dict:
    """Check if issue is resolved and escalate to terminate loop if so.

    This tool demonstrates Example 4-8: using escalate=True to exit the loop
    early when a termination condition is met.

    Args:
        solution_status: Current status of the solution attempt.
        tool_context: The tool context for accessing actions.

    Returns:
        Resolution status.
    """
    # Check if resolved keywords are present
    resolved_keywords = ["resolved", "fixed", "working", "success"]
    is_resolved = any(kw in solution_status.lower() for kw in resolved_keywords)

    if is_resolved:
        # Example 4-8: Set escalate to True to terminate the loop early
        tool_context.actions.escalate = True
        return {
            "status": "resolved",
            "message": "Issue has been resolved. Terminating troubleshooting loop.",
            "loop_terminated": True
        }

    return {
        "status": "ongoing",
        "message": "Issue not yet resolved. Continuing troubleshooting.",
        "loop_terminated": False
    }


def get_next_troubleshooting_level(current_level: int, issue_type: str) -> dict:
    """Get the next level of troubleshooting steps.

    Args:
        current_level: Current troubleshooting level (1-5).
        issue_type: Type of issue being addressed.

    Returns:
        Next level troubleshooting information.
    """
    levels = {
        1: {"name": "Basic", "description": "Simple restarts and checks"},
        2: {"name": "Intermediate", "description": "Settings and configuration adjustments"},
        3: {"name": "Advanced", "description": "System diagnostics and resets"},
        4: {"name": "Expert", "description": "Hardware checks and replacements"},
        5: {"name": "Escalation", "description": "Technician visit or replacement unit"}
    }

    next_level = min(current_level + 1, 5)
    return {
        "current_level": current_level,
        "next_level": next_level,
        "level_info": levels.get(next_level, levels[5]),
        "max_level_reached": next_level >= 5
    }


# =============================================================================
# LOOP AGENT WORKFLOW (Examples 4-7 and 4-8)
# =============================================================================

# Agent that suggests a solution (Example 4-7)
solution_agent = Agent(
    model="gemini-2.5-flash",
    name="SolutionAgent",
    instruction="""You are a troubleshooting specialist. Based on the issue
    description and any previous attempts, suggest the next troubleshooting step.

    Context available:
    - Issue description: {issue_description}
    - Previous attempts: {previous_attempts}
    - Last suggested solution: {suggested_solution}

    Guidelines:
    1. Start with simple solutions (power cycle, check connections)
    2. Progress to more complex ones (factory reset, firmware update)
    3. Use lookup_troubleshooting_steps to get standard procedures
    4. Check check_known_issues for any matching known problems
    5. Each iteration should try a different, more advanced approach

    Provide clear, step-by-step instructions the customer can follow.""",
    output_key="suggested_solution",
    tools=[lookup_troubleshooting_steps, check_known_issues, get_next_troubleshooting_level]
)

# Agent that validates if the solution worked (Example 4-7)
validation_agent = Agent(
    model="gemini-2.5-flash",
    name="ValidationAgent",
    instruction="""You validate whether the suggested solution resolved the issue.

    The suggested solution was: {suggested_solution}

    Your tasks:
    1. Use prompt_user_for_feedback to ask the customer to test the solution
    2. Use analyze_test_results to interpret their feedback
    3. Use check_resolution to determine if we should stop the loop

    If the issue is resolved, call check_resolution with a status containing
    "resolved" to terminate the troubleshooting loop.

    If not resolved, summarize what was tried and what the result was so the
    next iteration can try a different approach.""",
    output_key="solution_status",
    tools=[prompt_user_for_feedback, analyze_test_results, check_resolution]
)

# Loop until resolved or max attempts reached (Example 4-7)
troubleshooting_loop = LoopAgent(
    name="TroubleshootingLoop",
    sub_agents=[solution_agent, validation_agent],
    max_iterations=5  # Safety limit - prevent infinite loops
)

# For adk web compatibility - export as root_agent
root_agent = troubleshooting_loop
