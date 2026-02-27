# A2A Client Sample - Consuming Remote Agents

This sample demonstrates how to consume a remote A2A-compatible agent
using **RemoteA2aAgent**.
Based on Chapter 4, Example 4-12: Remote Agent Consumption.

## Overview

RemoteA2aAgent allows you to invoke agents running on remote servers as if
they were local sub-agents. The remote agent is discovered via its Agent Card
and integrated seamlessly into your agent hierarchy.

```
┌─────────────────────────────────────────────────────────────────┐
│                    06_a2a_client                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │            CustomerServiceCoordinator                     │ │
│  │                                                           │ │
│  │  Local Tools:                    Sub-Agents:              │ │
│  │  ├── check_device_status         └── BillingAgent         │ │
│  │  ├── lookup_error_codes               (RemoteA2aAgent)   │ │
│  │  └── run_device_diagnostics                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                           │                     │
│                                           │ A2A Protocol        │
│                                           ▼                     │
└───────────────────────────────────────────┼─────────────────────┘
                                            │
                                            │ HTTP
                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    05_a2a_server                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    BillingAgent                           │ │
│  │                                                           │ │
│  │  Tools:                                                   │ │
│  │  ├── query_billing_history                                │ │
│  │  ├── calculate_refund_amount                              │ │
│  │  ├── check_payment_status                                 │ │
│  │  ├── process_credit                                       │ │
│  │  └── generate_invoice                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Agent Card: http://localhost:8001/.well-known/agent-card.json │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. RemoteA2aAgent for Client Connections (Example 4-12)

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# Connect to remote agent via its Agent Card URL
billing_agent = RemoteA2aAgent(
    name="BillingAgent",
    description="Specialist for billing inquiries, refunds, and payment issues",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)
```

### 2. Using Remote Agents as Sub-Agents

```python
# Use just like a local sub-agent
coordinator = Agent(
    model="gemini-2.5-flash",
    name="CustomerServiceCoordinator",
    instruction="Route billing to BillingAgent, handle tech locally...",
    sub_agents=[billing_agent],  # Remote agent!
    tools=[check_device_status, lookup_error_codes]
)
```

### 3. Seamless Delegation

The coordinator automatically delegates to the remote BillingAgent when
billing-related queries are detected.

## Theme: Customer Support Coordinator

This sample implements a coordinator that combines:

1. **Local Technical Support**
   - Device status checks
   - Error code lookups
   - Device diagnostics

2. **Remote Billing Support** (via A2A)
   - Billing history
   - Refund processing
   - Payment issues

## Quick Start

### Step 1: Start the A2A Billing Server

First, start the billing agent from sample 05:

```bash
cd ../05_a2a_server

# Set up environment if needed
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Start the A2A server
uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
```

Verify it's running:
```bash
curl http://localhost:8001/.well-known/agent-card.json
```

### Step 2: Run the A2A Client

In a new terminal:

```bash
cd chapter-4/06_a2a_client

# Set up environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run with ADK web interface
adk web .
```

### Step 3: Test the Integration

Try these queries:

1. **Technical query (handled locally):**
   - "Check the status of device DEV-THERM-001"
   - "What does error code E001 mean?"

2. **Billing query (delegated to remote):**
   - "Show me billing history for customer CUST-001"
   - "I was overcharged $47 last month, can I get a refund?"

3. **Mixed query (both local and remote):**
   - "My thermostat seems defective and caused my bill to spike"

## Sample Queries to Try

| Query | Handled By | Description |
|-------|------------|-------------|
| "Check device DEV-THERM-001" | Local | Uses check_device_status |
| "What's error E002?" | Local | Uses lookup_error_codes |
| "Run diagnostics on my thermostat" | Local | Uses run_device_diagnostics |
| "Show billing for CUST-001" | Remote | Delegates to BillingAgent |
| "I need a refund for the $47 charge" | Remote | Delegates to BillingAgent |
| "Device defect caused billing issue" | Both | Local diagnosis + remote billing |

## Code Walkthrough

### Remote Agent Connection

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# The agent_card URL points to the A2A server's discovery endpoint
billing_agent = RemoteA2aAgent(
    name="BillingAgent",
    description="Specialist for billing inquiries, refunds, and payment issues",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)
```

The RemoteA2aAgent:
1. Fetches the Agent Card at startup
2. Validates the remote agent's capabilities
3. Provides a local proxy for delegation

### Coordinator Agent

```python
coordinator = Agent(
    model="gemini-2.5-flash",
    name="CustomerServiceCoordinator",
    instruction="""You handle customer inquiries by routing to specialists.

    For technical issues: use your local tools
    For billing questions: delegate to BillingAgent
    For mixed issues: handle both aspects""",
    sub_agents=[billing_agent],  # Remote agent integrated seamlessly
    tools=[
        check_device_status,
        lookup_error_codes,
        run_device_diagnostics
    ]
)
```

### Local Tools

```python
def check_device_status(device_id: str) -> dict:
    """Check current status of a smart home device."""
    return {
        "device_id": device_id,
        "status": "online",
        "firmware": "2.3.1",
        "alerts": ["firmware_update_available"]
    }

def lookup_error_codes(error_code: str) -> dict:
    """Look up device error code meanings."""
    return {
        "code": "E001",
        "name": "WiFi Connection Lost",
        "resolution": ["Check router", "Reset network settings"]
    }
```

## Error Handling

If the A2A server is unavailable:

```
❌ Could not connect to remote agent at
   http://localhost:8001/.well-known/agent-card.json

Solutions:
1. Ensure 05_a2a_server is running: uvicorn agent:a2a_app --port 8001
2. Check the server URL in agent.py
3. Verify network connectivity
```

## Architecture Benefits

| Aspect | Benefit |
|--------|---------|
| **Separation** | Billing team maintains their agent independently |
| **Scalability** | Remote agent can scale separately |
| **Security** | Billing logic stays in billing service |
| **Flexibility** | Easy to swap remote implementations |
| **Discovery** | Agent Card provides capability info |

## When to Use RemoteA2aAgent

✅ **Good Use Cases:**
- Cross-team agent collaboration
- Microservices with specialized agents
- Enterprise service mesh
- Third-party agent integration

❌ **Consider Local Sub-Agents When:**
- Same codebase/deployment
- No network latency acceptable
- Simple agent hierarchies

## Key Takeaways

1. **RemoteA2aAgent wraps A2A servers** - Appears as local sub-agent
2. **Agent Card URL is the entry point** - Discovery is automatic
3. **Delegation is seamless** - Coordinator routes naturally
4. **Works with local tools** - Mix remote agents and local capabilities
5. **Samples 05+06 work together** - Complete end-to-end A2A demo

## Dependencies

```
google-adk>=1.0.0
```

## Next Steps

- **07_hybrid_team**: Combine local, remote, and MCP in one workflow
- **08_production_agent**: Add security, tracing, and versioning
