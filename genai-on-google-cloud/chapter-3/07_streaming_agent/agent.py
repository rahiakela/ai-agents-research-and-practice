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
Streaming Agent - Real-Time Voice Support with Live API

This agent demonstrates ADK's Live API streaming capabilities,
matching Example 3-18 from Chapter 3.

Key concepts:
- StreamingMode.BIDI for bidirectional streaming
- LiveRequestQueue for real-time audio input
- runner.run_live() for live session handling
- speech_config with voice settings
- Audio transcription configuration

Theme: SmartHome Voice Support (consistent with Chapter 3)

NOTE: This sample includes:
- A standard agent (for ADK web with text)
- A streaming runner example (for programmatic use)
- Live API patterns (for voice applications)
"""

import asyncio
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import ToolContext


# =============================================================================
# VOICE SUPPORT TOOLS
# =============================================================================

def lookup_account(
    customer_id: str = None,
    phone_number: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Look up a customer account by ID or phone number.

    Args:
        customer_id: The customer account ID
        phone_number: Customer phone number as alternative lookup
        tool_context: Provided by ADK

    Returns:
        Customer account information
    """
    # Simulated customer data
    accounts = {
        "CUST-001": {
            "customer_id": "CUST-001",
            "name": "John Smith",
            "phone": "555-0100",
            "products": ["SmartHome Doorbell Pro", "Smart Thermostat"],
            "status": "active",
            "member_since": "2023-06-15"
        },
        "CUST-002": {
            "customer_id": "CUST-002",
            "name": "Sarah Johnson",
            "phone": "555-0101",
            "products": ["Smart Lock", "Indoor Camera"],
            "status": "active",
            "member_since": "2024-01-20"
        }
    }

    # Look up by ID or phone
    if customer_id and customer_id in accounts:
        return accounts[customer_id]

    if phone_number:
        for account in accounts.values():
            if phone_number in account.get("phone", ""):
                return account

    return {
        "error": "Account not found",
        "suggestion": "Please verify the customer ID or phone number"
    }


def create_ticket(
    issue_type: str,
    description: str,
    priority: str = "normal",
    tool_context: ToolContext = None
) -> dict:
    """Create a support ticket for the customer.

    Args:
        issue_type: Type of issue (technical, billing, returns, general)
        description: Description of the issue
        priority: Ticket priority (low, normal, high, urgent)
        tool_context: Provided by ADK

    Returns:
        Ticket confirmation
    """
    import random
    ticket_id = f"TKT-{random.randint(10000, 99999)}"

    if tool_context:
        tickets = tool_context.state.get("user:tickets", [])
        tickets.append({
            "ticket_id": ticket_id,
            "issue_type": issue_type,
            "priority": priority,
            "created": datetime.now().isoformat()
        })
        tool_context.state["user:tickets"] = tickets

    return {
        "ticket_id": ticket_id,
        "issue_type": issue_type,
        "priority": priority,
        "status": "open",
        "message": f"Ticket {ticket_id} created. A specialist will follow up.",
        "estimated_response": "24 hours" if priority == "normal" else "4 hours"
    }


def check_device_status(
    device_type: str,
    tool_context: ToolContext = None
) -> dict:
    """Check the status of a SmartHome device.

    Args:
        device_type: Type of device to check
        tool_context: Provided by ADK

    Returns:
        Device status information
    """
    statuses = {
        "doorbell": {"online": True, "battery": "85%", "last_motion": "2 hours ago"},
        "thermostat": {"online": True, "current_temp": "72°F", "mode": "cooling"},
        "lock": {"online": True, "locked": True, "last_activity": "30 min ago"},
        "camera": {"online": False, "issue": "Connection timeout", "last_online": "1 hour ago"}
    }

    device_key = device_type.lower()
    for key, status in statuses.items():
        if key in device_key:
            return {"device": device_type, **status}

    return {"error": f"Device type '{device_type}' not recognized"}


def transfer_to_specialist(
    department: str,
    reason: str,
    tool_context: ToolContext = None
) -> dict:
    """Transfer the call to a specialist department.

    Args:
        department: Department to transfer to (technical, billing, returns)
        reason: Reason for transfer
        tool_context: Provided by ADK

    Returns:
        Transfer confirmation
    """
    departments = {
        "technical": {"queue_time": "5 minutes", "available": True},
        "billing": {"queue_time": "2 minutes", "available": True},
        "returns": {"queue_time": "10 minutes", "available": True},
        "escalation": {"queue_time": "3 minutes", "available": True}
    }

    dept_info = departments.get(department.lower(), departments["technical"])

    return {
        "transfer_to": department,
        "reason": reason,
        "queue_time": dept_info["queue_time"],
        "message": f"Transferring to {department}. Estimated wait: {dept_info['queue_time']}"
    }


# =============================================================================
# ROOT AGENT (Works with ADK web for text, Live API for voice)
# =============================================================================

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products via voice support.

You are a voice support agent. Keep responses:
- **Concise**: Speak in short, clear sentences
- **Conversational**: Use natural speech patterns
- **Helpful**: Address the customer's needs directly

Your capabilities:
- Look up customer accounts
- Check device status
- Create support tickets
- Transfer to specialists when needed

Voice support guidelines:
1. Greet warmly but briefly
2. Confirm what the customer needs
3. Take action using your tools
4. Summarize what you've done
5. Ask if there's anything else

Remember: You're speaking, not typing. Avoid bullet points and
long lists in responses - use natural conversational flow.""",
    tools=[
        lookup_account,
        create_ticket,
        check_device_status,
        transfer_to_specialist
    ]
)


# =============================================================================
# LIVE API STREAMING EXAMPLE (Example 3-18)
# =============================================================================

async def live_voice_support_example():
    """
    Example 3-18: Live API patterns for real-time voice streaming.

    This demonstrates:
    - StreamingMode.BIDI configuration
    - LiveRequestQueue for bidirectional streaming
    - runner.run_live() event handling
    - speech_config with voice settings
    - Audio transcription configuration
    """
    from google.adk.runners import Runner, RunConfig
    from google.adk.agents import LiveRequestQueue
    from google.adk.agents.run_config import StreamingMode
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    # Create session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="voice_support",
        session_service=session_service
    )

    # Create a session
    session = await session_service.create_session(
        app_name="voice_support",
        user_id="voice_user"
    )

    # Example 3-18: Configure for bidirectional audio streaming
    run_config = RunConfig(
        streaming_mode=StreamingMode.BIDI,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Aoede"  # Natural-sounding voice
                )
            )
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    # Create live request queue for sending audio
    live_request_queue = LiveRequestQueue()

    print("=== Live Voice Support Demo ===\n")
    print("Starting live streaming session...")
    print("(In production, audio would stream through WebSocket)\n")

    # Start live streaming session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config
    )

    # Process events from the agent
    async for event in live_events:
        # Handle output transcription (what the agent says)
        if event.output_transcription and event.output_transcription.text:
            print(f"Agent said: {event.output_transcription.text}")

        # Handle input transcription (what the user said)
        if event.input_transcription and event.input_transcription.text:
            print(f"User said: {event.input_transcription.text}")

        # Handle turn completion
        if event.turn_complete:
            print("[Turn complete]")

        # Handle interruption
        if event.interrupted:
            print("[User interrupted]")

    print("\n=== Session Complete ===")


def send_audio_example():
    """
    Example of sending audio to the live session.

    In production, this would be called when audio data arrives
    from the microphone or WebSocket.
    """
    from google.adk.agents import LiveRequestQueue
    from google.genai import types

    # Create queue (in production, reuse the same queue)
    live_request_queue = LiveRequestQueue()

    # Example: Send audio bytes
    # audio_bytes would come from microphone or WebSocket
    audio_bytes = b""  # Placeholder

    if audio_bytes:
        live_request_queue.send_realtime(
            types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
        )

    # Signal end of audio input
    live_request_queue.close()


# =============================================================================
# TEXT STREAMING EXAMPLE (For comparison)
# =============================================================================

async def text_streaming_example():
    """
    Standard text streaming example using run_async().
    This is simpler than Live API and works with text input.
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="voice_support",
        session_service=session_service
    )

    session = await session_service.create_session(
        app_name="voice_support",
        user_id="demo_user"
    )

    print("=== Text Streaming Demo ===\n")
    prompt = "My doorbell camera isn't connecting. Can you help?"

    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=prompt
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    print(part.text, end='', flush=True)

    print("\n\n=== Complete ===")


# Allow running this file directly
if __name__ == "__main__":
    print("Streaming Agent Demo")
    print("=" * 50)
    print("\nFor ADK web interface: adk web .")
    print("\nRunning text streaming example...\n")

    try:
        asyncio.run(text_streaming_example())
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure google-adk is installed: pip install google-adk")
