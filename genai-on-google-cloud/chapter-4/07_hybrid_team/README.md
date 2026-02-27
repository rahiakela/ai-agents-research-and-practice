# Hybrid Team Sample - Local + Remote + MCP Combined

This sample demonstrates combining all three agent integration types in one
comprehensive workflow:
- **Local agents** with specialized tools
- **Remote A2A agents** for cross-service communication
- **MCP tools** for external system access

Based on Chapter 4, Examples 4-13 and 4-14: Hybrid Agent Team.

## Overview

The hybrid architecture represents the most sophisticated pattern for enterprise
agent systems. It combines the strengths of each integration type:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CustomerServiceCoordinator                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Hybrid Resources                             │   │
│  │                                                                      │   │
│  │   LOCAL                   REMOTE                    MCP              │   │
│  │   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐   │   │
│  │   │ Technical    │       │ Billing      │       │ Customer     │   │   │
│  │   │ Agent        │       │ Agent        │       │ Database     │   │   │
│  │   │              │       │              │       │              │   │   │
│  │   │ • diagnostics│       │ • billing    │       │ • lookup     │   │   │
│  │   │ • errors     │       │ • refunds    │       │ • usage      │   │   │
│  │   │ • known issues│      │ • credits    │       │ • devices    │   │   │
│  │   └──────────────┘       └──────────────┘       └──────────────┘   │   │
│  │         │                       │                      │           │   │
│  │         │ sub_agents            │ A2A                  │ MCP       │   │
│  │         ▼                       ▼                      ▼           │   │
│  │   Same Process            Port 8001               Port 8080        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Three Integration Types in One Agent (Example 4-13)

```python
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# LOCAL: Technical diagnostics agent
technical_agent = Agent(
    model="gemini-2.5-flash",
    name="TechnicalAgent",
    instruction="Diagnose device issues...",
    output_key="technical_diagnosis",
    tools=[check_device_diagnostics, analyze_error_patterns]
)

# REMOTE: Billing agent via A2A
billing_agent = RemoteA2aAgent(
    name="BillingAgent",
    description="Handles billing and refunds",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)

# MCP: Customer database tools
customer_db = McpToolset(
    connection_params=SseConnectionParams(url="http://localhost:8080/sse")
)

# COORDINATOR: Combines all resources
coordinator = Agent(
    model="gemini-2.5-flash",
    name="CustomerServiceCoordinator",
    instruction="Orchestrate local, remote, and MCP resources...",
    sub_agents=[technical_agent, billing_agent],  # Local + Remote
    tools=[customer_db]  # MCP tools
)
```

### 2. Synthesized Response (Example 4-14)

The coordinator combines outputs from all specialists into a unified response:

```
Based on my analysis:

Technical: Your thermostat has a defective temperature sensor...
Billing: The sensor defect caused approximately $47 in excess costs...
Resolution: Replacement initiated, $50 credit applied...
```

## Theme: Complete Customer Support System

This sample implements a full-featured support system handling:

1. **Customer Lookup** (MCP) - Identify customer and their devices
2. **Technical Diagnosis** (Local) - Diagnose device issues
3. **Billing Analysis** (Remote) - Handle financial impact

## Quick Start

### Step 1: Start the MCP Server

```bash
cd chapter-4/07_hybrid_team

# Install dependencies if needed
pip install mcp starlette uvicorn

# Start the MCP server
python mcp_server.py  # Runs on port 8080
```

### Step 2: Start the A2A Billing Server

In a new terminal:

```bash
cd chapter-4/05_a2a_server

# Set up environment if needed
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Start the A2A server
uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
```

### Step 3: Run the Hybrid Coordinator

In a third terminal:

```bash
cd chapter-4/07_hybrid_team

# Set up environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run with ADK web interface
adk web .
```

## Sample Query

Try this comprehensive query that exercises all three integration types:

**"My smart thermostat is showing a wiring error, and I think it might have
overcharged my last bill."**

This triggers:
1. **MCP** → Customer lookup, device usage history
2. **Local** → Technical diagnosis, error pattern analysis
3. **Remote** → Billing analysis, credit processing

### Expected Response (Example 4-14)

```
Based on my analysis:

**Technical:** Your thermostat (DEV-THERM-001) has a defective temperature
sensor causing readings 5°F too high. This is a known issue (ISSUE-2024-001)
covered under warranty. The sensor malfunction caused your HVAC to overcycle.

**Billing:** The sensor defect resulted in approximately 45 hours of excess
HVAC runtime, consuming an estimated 38.5 kWh of additional energy. This
translates to roughly $47 in excess charges on your November bill.

**Resolution:**
• Warranty replacement initiated - new thermostat ships within 2-3 days
• $50 credit applied to your account to cover excess energy costs
• Free installation included with replacement

Is there anything else I can help you with?
```

## Code Walkthrough

### Local Technical Agent

```python
technical_agent = Agent(
    model="gemini-2.5-flash",
    name="TechnicalAgent",
    description="Diagnoses technical issues with smart home devices",
    instruction="Run diagnostics, analyze errors, check known issues...",
    output_key="technical_diagnosis",  # Results available to coordinator
    tools=[
        check_device_diagnostics,
        analyze_error_patterns,
        lookup_known_issues
    ]
)
```

### Remote A2A Agent

```python
billing_agent = RemoteA2aAgent(
    name="BillingAgent",
    description="Handles billing inquiries, refunds, and payment processing",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)
```

### MCP Customer Database

```python
customer_db = MCPToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse"
    )
)
```

### Coordinator (Combines All)

```python
coordinator = Agent(
    model="gemini-2.5-flash",
    name="CustomerServiceCoordinator",
    instruction="""Orchestrate local, remote, and MCP resources:
    1. Use MCP to look up customer and device usage
    2. Delegate to TechnicalAgent for diagnosis
    3. Delegate to BillingAgent for financial impact
    4. Synthesize all findings into unified response""",
    sub_agents=[technical_agent, billing_agent],
    tools=[customer_db]
)
```

## Architecture Benefits

| Resource Type | Benefits | Use Case |
|---------------|----------|----------|
| **Local Agent** | Low latency, same process | Domain-specific logic |
| **Remote A2A** | Team ownership, independent scaling | Cross-boundary services |
| **MCP Tools** | Standard protocol, reusable | External systems/databases |

## When to Use Hybrid Architecture

✅ **Good Use Cases:**
- Enterprise systems with multiple domains
- Cross-team collaboration requirements
- External system integrations
- Complex workflows requiring synthesis

❌ **Consider Simpler Patterns When:**
- Single-domain applications
- No external dependencies
- Latency-critical paths

## Troubleshooting

### MCP Server Not Responding

```
Error: Could not connect to MCP server at http://localhost:8080

Solution: Start the MCP server:
    cd chapter-4/07_hybrid_team
    python mcp_server.py
```

### A2A Server Not Responding

```
Error: Could not fetch agent card from http://localhost:8001

Solution: Start the A2A server:
    cd chapter-4/05_a2a_server
    uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
```

### Services Status Check

```bash
# Check MCP server
curl http://localhost:8080/sse

# Check A2A server
curl http://localhost:8001/.well-known/agent-card.json
```

## Key Takeaways

1. **Hybrid combines all integration types** - Local, Remote, MCP in one coordinator
2. **Each type has strengths** - Choose based on ownership, latency, reusability
3. **Coordinator synthesizes outputs** - Unified response from all specialists
4. **Example 4-14 shows synthesis** - Technical + Billing → Complete resolution
5. **Enterprise-ready pattern** - Scales across teams and systems

## Dependencies

```
google-adk>=1.0.0
mcp>=1.0.0
starlette>=0.32.0
uvicorn>=0.23.0
```

## Next Steps

- **08_production_agent**: Add security, tracing, and versioning to your agents
