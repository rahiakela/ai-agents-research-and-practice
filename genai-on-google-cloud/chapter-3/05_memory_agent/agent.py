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
Memory Agent - Long-Term Memory with Vertex AI Memory Bank

This agent demonstrates ADK's integration with Vertex AI Memory Bank for
persistent, semantic memory, matching Examples 3-14, 3-15, and 3-16.

Key concepts:
- VertexAiMemoryBankService for memory storage
- VertexAiSessionService for session management
- PreloadMemoryTool for automatic memory retrieval
- {memory} placeholder in instructions (Example 3-16)
- add_session_to_memory() for memory extraction (Example 3-15)

NOTE: This sample requires Vertex AI and a Google Cloud project.
See README.md for setup instructions.

Theme: SmartHome Customer Support (consistent with Chapter 3)
"""

import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_ENGINE_ID = os.environ.get("AGENT_ENGINE_ID")

# =============================================================================
# MEMORY BANK SETUP (Example 3-14)
# =============================================================================

memory_service = None
session_service = None
memory_tools = []

if PROJECT_ID and AGENT_ENGINE_ID:
    try:
        from google.adk.memory import VertexAiMemoryBankService
        from google.adk.sessions import VertexAiSessionService
        from google.adk.tools import PreloadMemoryTool

        # Example 3-14: Complete VertexAiSessionService + VertexAiMemoryBankService setup
        session_service = VertexAiSessionService(
            project=PROJECT_ID,
            location=LOCATION
        )

        memory_service = VertexAiMemoryBankService(
            project=PROJECT_ID,
            location=LOCATION,
            agent_engine_id=AGENT_ENGINE_ID
        )

        # Create the memory preload tool
        preload_memory = PreloadMemoryTool()
        memory_tools = [preload_memory]

        print(f"Memory Bank initialized for project: {PROJECT_ID}")
        print(f"Agent Engine ID: {AGENT_ENGINE_ID}")

    except ImportError as e:
        print(f"Memory Bank imports failed: {e}")
        print("Running in demo mode without persistent memory.")

    except Exception as e:
        print(f"Memory Bank initialization failed: {e}")
        print("Running in demo mode without persistent memory.")
else:
    if not PROJECT_ID:
        print("GOOGLE_CLOUD_PROJECT not set.")
    if not AGENT_ENGINE_ID:
        print("AGENT_ENGINE_ID not set.")
    print("Running in demo mode. Set both environment variables for Memory Bank.")


# =============================================================================
# CUSTOMER SUPPORT TOOLS
# =============================================================================

def save_customer_preference(
    preference_type: str,
    preference_value: str,
    tool_context: ToolContext = None
) -> dict:
    """Save a customer preference for future interactions.

    Args:
        preference_type: Type of preference (e.g., "contact_method", "language")
        preference_value: The preference value
        tool_context: Provided by ADK

    Returns:
        Confirmation of saved preference
    """
    if tool_context:
        prefs = tool_context.state.get("user:preferences", {})
        prefs[preference_type] = preference_value
        tool_context.state["user:preferences"] = prefs

        return {
            "success": True,
            "message": f"Saved {preference_type} preference: {preference_value}"
        }

    return {"success": False, "error": "Context not available"}


def get_customer_preferences(tool_context: ToolContext = None) -> dict:
    """Retrieve all saved customer preferences.

    Args:
        tool_context: Provided by ADK

    Returns:
        All saved preferences
    """
    if tool_context:
        prefs = tool_context.state.get("user:preferences", {})
        if prefs:
            return {"preferences": prefs}
        return {"message": "No preferences saved yet"}

    return {"error": "Context not available"}


def log_product_issue(
    product_name: str,
    issue_description: str,
    tool_context: ToolContext = None
) -> dict:
    """Log a product issue for the customer.

    Args:
        product_name: Name of the SmartHome product
        issue_description: Description of the issue
        tool_context: Provided by ADK

    Returns:
        Confirmation with case number
    """
    if tool_context:
        import random
        case_number = f"CASE-{random.randint(10000, 99999)}"

        issues = tool_context.state.get("user:issues", [])
        issues.append({
            "case_number": case_number,
            "product": product_name,
            "issue": issue_description
        })
        tool_context.state["user:issues"] = issues

        return {
            "success": True,
            "case_number": case_number,
            "message": f"Issue logged for {product_name}"
        }

    return {"success": False, "error": "Context not available"}


def get_customer_history(tool_context: ToolContext = None) -> dict:
    """Get the customer's interaction history.

    Args:
        tool_context: Provided by ADK

    Returns:
        Customer's previous interactions
    """
    if tool_context:
        history = {
            "preferences": tool_context.state.get("user:preferences", {}),
            "issues": tool_context.state.get("user:issues", []),
            "orders": tool_context.state.get("user:order_count", 0)
        }
        return history

    return {"error": "Context not available"}


# =============================================================================
# ROOT AGENT WITH MEMORY PLACEHOLDER (Example 3-16)
# =============================================================================

# Combine custom tools with memory tools
all_tools = [
    save_customer_preference,
    get_customer_preferences,
    log_product_issue,
    get_customer_history
] + memory_tools

# Example 3-16: Agent with {memory} placeholder in instruction
root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products.

Before responding, review these memories:
---
Retrieved Memories:
{memory}
---

Use this context to provide personalized support. Reference previous
interactions, preferences, and issues when relevant.

Your capabilities:
- Remember customer preferences (contact method, language, etc.)
- Log and track product issues
- Provide personalized recommendations based on history

Guidelines:
- If you recognize the customer from memories, acknowledge them
- Reference their preferences and past issues when helpful
- Save new preferences when customers share them
- Be warm and remember details that matter to them""",
    tools=all_tools
)


# =============================================================================
# RUNNER WITH MEMORY BANK (Example 3-14)
# =============================================================================

def create_runner():
    """Create a runner with Memory Bank if available.

    Example 3-14: Complete VertexAiSessionService + VertexAiMemoryBankService setup
    Example 3-15: add_session_to_memory() for memory extraction
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    # Use Vertex AI session service if available, otherwise in-memory
    active_session_service = session_service if session_service else InMemorySessionService()

    runner_kwargs = {
        "agent": root_agent,
        "app_name": AGENT_ENGINE_ID or "memory_agent",
        "session_service": active_session_service
    }

    # Add memory service if available
    if memory_service:
        runner_kwargs["memory_service"] = memory_service

    return Runner(**runner_kwargs)


# Example 3-15: Memory extraction after session
async def save_session_memories(runner, session):
    """Extract and save memories from a completed session.

    Call this after a session ends to persist important information
    to the Memory Bank for future sessions.

    Example 3-15: add_session_to_memory() pattern
    """
    if memory_service:
        await memory_service.add_session_to_memory(session)
        print(f"Memories extracted and saved for session: {session.id}")
    else:
        print("Memory service not available - memories not persisted")
