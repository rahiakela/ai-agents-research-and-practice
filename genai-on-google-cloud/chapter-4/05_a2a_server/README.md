# A2A Server Sample - Exposing Agents as Services

This sample demonstrates how to expose an ADK agent via the **A2A (Agent-to-Agent)**
protocol using `to_a2a()`.
Based on Chapter 4, Examples 4-10 and 4-11.

## Overview

A2A (Agent-to-Agent) is a protocol that allows agents to communicate with each
other across services and organizations. By exposing your agent via A2A, it
becomes discoverable and invocable by any A2A-compatible client.

```
┌─────────────────────────────────────────────────────────────────┐
│                         A2A Server                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    to_a2a(billing_agent)                  │ │
│  │                                                           │ │
│  │  GET /.well-known/agent-card.json                         │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ {                                                   │ │ │
│  │  │   "name": "BillingAgent",                          │ │ │
│  │  │   "description": "Specialist for billing...",      │ │ │
│  │  │   "url": "http://localhost:8001",                  │ │ │
│  │  │   "capabilities": { ... }                          │ │ │
│  │  │ }                                                   │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                           │ │
│  │  POST /                                                   │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │               BillingAgent                          │ │ │
│  │  │  - query_billing_history                            │ │ │
│  │  │  - calculate_refund_amount                          │ │ │
│  │  │  - check_payment_status                             │ │ │
│  │  │  - process_credit                                   │ │ │
│  │  │  - generate_invoice                                 │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Listening on http://localhost:8001                            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Exposing an Agent via A2A (Example 4-10)

```python
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Define your agent as usual
billing_agent = Agent(
    model="gemini-2.5-flash",
    name="BillingAgent",
    description="Specialist for billing inquiries, refunds, and payment processing",
    instruction="...",
    tools=[query_billing_history, calculate_refund_amount, ...]
)

# Expose it via A2A - one line!
a2a_app = to_a2a(billing_agent, port=8001)
```

### 2. Deploying with uvicorn (Example 4-11)

```bash
uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
```

### 3. Agent Card Discovery

The Agent Card is automatically generated and served at:
```
GET http://localhost:8001/.well-known/agent-card.json
```

Sample Agent Card:
```json
{
  "name": "BillingAgent",
  "description": "Specialist for billing inquiries, refunds, and payment processing",
  "url": "http://localhost:8001",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  }
}
```

## Theme: SmartHome Billing Service

This sample implements a billing agent owned by the "Finance Team" that:

1. **Queries billing history** - View invoices and payments
2. **Calculates refunds** - Full or partial refund amounts
3. **Checks payment status** - Invoice payment details
4. **Processes credits** - Apply account credits
5. **Generates invoices** - Create new invoices

## Quick Start

### Step 1: Start the A2A Server

```bash
cd chapter-4/05_a2a_server

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start the A2A server
uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Step 2: Verify the Agent Card

```bash
curl http://localhost:8001/.well-known/agent-card.json | jq
```

Expected output:
```json
{
  "name": "BillingAgent",
  "description": "Specialist for billing inquiries, refunds, and payment processing",
  "url": "http://localhost:8001",
  ...
}
```

### Step 3: Test with a Client

See **06_a2a_client** for consuming this agent from another service.

Or test directly with curl:
```bash
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Check billing for customer CUST-001"}'
```

## Code Walkthrough

### Agent Definition

```python
billing_agent = Agent(
    model="gemini-2.5-flash",
    name="BillingAgent",
    # IMPORTANT: description appears in Agent Card for discovery
    description="Specialist for billing inquiries, refunds, and payment processing",
    instruction="""You are a billing specialist...""",
    tools=[
        query_billing_history,
        calculate_refund_amount,
        check_payment_status,
        process_credit,
        generate_invoice
    ]
)
```

### A2A Exposure

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# to_a2a() creates an ASGI app with:
# - POST / - Main agent interaction endpoint
# - GET /.well-known/agent-card.json - Agent discovery
a2a_app = to_a2a(billing_agent, port=8001)
```

### Billing Tools

```python
def query_billing_history(customer_id: str, months: int = 6) -> dict:
    """Query billing history for a customer."""
    # Returns invoices, payments, and anomalies
    return {
        "customer_id": customer_id,
        "invoices": [...],
        "anomalies_found": 1
    }

def calculate_refund_amount(invoice_id: str, reason: str, partial_percentage: float = 100.0) -> dict:
    """Calculate the refund amount for an invoice."""
    return {
        "invoice_id": invoice_id,
        "refund_amount": 47.00,
        "approval_required": False
    }
```

## Integration with 06_a2a_client

This server is designed to work with the **06_a2a_client** sample:

```
┌──────────────────────┐         ┌──────────────────────┐
│   06_a2a_client      │         │   05_a2a_server      │
│                      │         │                      │
│  RemoteA2aAgent ─────┼────────►│  BillingAgent        │
│  "BillingAgent"      │  A2A    │  (to_a2a)            │
│                      │         │                      │
│  Port: adk web       │         │  Port: 8001          │
└──────────────────────┘         └──────────────────────┘
```

## Deployment Options

### Local Development

```bash
uvicorn agent:a2a_app --host 0.0.0.0 --port 8001 --reload
```

### Production (with gunicorn)

```bash
gunicorn agent:a2a_app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "agent:a2a_app", "--host", "0.0.0.0", "--port", "8001"]
```

### Cloud Run

```bash
gcloud run deploy billing-agent \
  --source . \
  --port 8001 \
  --allow-unauthenticated
```

## When to Use A2A

✅ **Good Use Cases:**
- Microservices architecture with specialized agents
- Cross-team agent collaboration
- Enterprise service mesh with agents
- Public agent APIs

❌ **Consider Alternatives When:**
- Single monolithic application (use sub_agents directly)
- Same process communication (overhead not needed)
- Latency-critical paths (network adds latency)

## Security Considerations

For production, add authentication:

```python
# See 08_production_agent for full security examples
a2a_app = to_a2a(
    billing_agent,
    # Security configuration in Agent Card
)
```

Agent Card with security (Example 4-15):
```json
{
  "name": "BillingAgent",
  "securitySchemes": {
    "oauth": {
      "type": "oauth2",
      "flows": {
        "clientCredentials": {
          "tokenUrl": "https://auth.example.com/token",
          "scopes": {
            "billing:read": "Read billing information",
            "billing:refund": "Process refunds"
          }
        }
      }
    }
  }
}
```

## Key Takeaways

1. **to_a2a() creates an ASGI app** - Deploy with any ASGI server
2. **Agent Card is automatic** - Generated from agent metadata
3. **Description is critical** - It's how clients discover your agent
4. **Standard HTTP deployment** - uvicorn, gunicorn, Cloud Run, etc.
5. **Integrates with 06_a2a_client** - Together they demo full A2A flow

## Dependencies

```
google-adk>=1.0.0
uvicorn>=0.23.0
```

## Next Steps

- **06_a2a_client**: Consume this agent from another service
- **07_hybrid_team**: Combine with local agents and MCP
- **08_production_agent**: Add security, tracing, and versioning
