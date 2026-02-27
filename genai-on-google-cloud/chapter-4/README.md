<div align="center">
  <img src="../images/owl-front.png" alt="Chapter Guide" width="100"/>

  # Chapter 4: Orchestrating Intelligent Agent Teams
</div>

---

**Estimated Time**: 2-3 hours
**Prerequisites**: Complete Chapter 3 (Building Multimodal Agents with ADK)

## Overview

This chapter teaches you how to build **multiagent systems** using Google's Agent Development Kit (ADK). You'll learn to orchestrate teams of specialized agents that collaborate to solve complex, multi-domain problems.

The journey progresses from **local orchestration** (workflow agents running in the same process) to **distributed collaboration** (agents communicating across network boundaries via A2A and MCP protocols) to **production patterns** (security, tracing, and versioning).

## The Problem: Monolithic Agents Don't Scale

Consider this customer query:

> *"My new smart thermostat is showing a wiring error, and I think it might have overcharged my last bill. Can you check if it's eligible for a warranty replacement and fix the billing issue?"*

This single query requires expertise from **three domains**: technical diagnostics, warranty policy, and billing reconciliation. A monolithic agent trying to handle all three creates:

- **Conflicting instructions** (diagnostic mindset vs. financial compliance mindset)
- **Tool selection paralysis** (50+ tools to choose from)
- **Maintenance nightmares** (every change affects the entire system)

### Why This Fails: The Monolithic Antipattern

A single "super-agent" approach leads to:

**Instruction Conflicts** (Chapter Example 4-1):
```python
# 500+ line instruction combining incompatible mindsets
instruction = """
You are a technical expert who diagnoses hardware issues...
You are also a financial analyst who validates billing...
You are also a customer service representative...
"""
# Result: Agent confused about which "persona" to use
```

**Tool Paralysis** (Chapter Example 4-2):
```python
tools = [
    # Technical tools (15+)
    diagnose_wiring, check_firmware, test_connectivity, ...
    # Warranty tools (10+)
    check_warranty_status, validate_claim, ...
    # Billing tools (20+)
    get_invoice, calculate_refund, process_payment, ...
]
# Result: 50+ tools → agent struggles to select the right one
```

**Maintenance Nightmare**:
- Change billing logic → might break technical diagnostics
- Update warranty policy → entire agent needs redeployment
- Every team member editing the same 1000-line file

## Enterprise Context: Why Distributed Teams Matter

In real organizations, different teams own different services:

| Team | Service | Infrastructure | Database |
|------|---------|----------------|----------|
| **Technical Support** | Diagnostics API | On-premise servers | Device telemetry DB |
| **Warranty** | Policy Engine | Cloud Run | Warranty claims DB |
| **Billing** | Payment Gateway | Third-party SaaS | Financial transactions DB |

**Key Insight**: These teams operate independently with:
- Different deployment cycles (warranty updates monthly, billing updates daily)
- Different security requirements (PCI compliance for billing)
- Different ownership boundaries (can't modify other team's code)

**Local vs Remote Agents**:

| Dimension | Local Agents (same process) | Remote Agents (network) |
|-----------|------------------------------|-------------------------|
| **Location** | Same Python process | Independent services |
| **Communication** | In-memory (instant) | HTTP/network (latency) |
| **State** | Shared directly | Serialized via JSON |
| **Auth** | None needed | OAuth, API keys, mTLS |
| **Deployment** | Single deployment | Independent deployments |
| **Team Ownership** | One team | Multiple teams |

## The Solution: Agent Teams

Instead of one agent doing everything, build a **team of specialists**:

```
                    +-----------------------------+
                    |  CustomerServiceCoordinator |
                    | (Routes queries to specialists) |
                    +-------------+---------------+
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
   +-------------+        +-------------+        +-------------+
   | Technical   |        |  Warranty   |        |  Billing    |
   | Specialist  |        |  Specialist |        |  Specialist |
   +-------------+        +-------------+        +-------------+
```

## Key Concepts Deep Dive

### Three Orchestration Layers

Multi-agent systems operate at three distinct levels:

**1. Local Teams** (same process, shared memory):
- Workflow agents: SequentialAgent, ParallelAgent, LoopAgent
- Communication via `output_key` and `{placeholder}` syntax
- Zero network latency, instant state sharing
- Use when: All agents deployed together, single team ownership

**2. Distributed Collaboration** (network boundaries, protocols):
- **MCP (Model Context Protocol)**: Stateless tool access
  - Pattern: Request → Response (no conversation history)
  - Use for: Database queries, API calls, filesystem operations
- **A2A (Agent-to-Agent Protocol)**: Stateful delegation
  - Pattern: Multi-turn conversational handoff
  - Use for: Complex tasks requiring judgment (troubleshooting, negotiation)

**3. Production Realities** (security, tracing, versioning):
- Authentication schemes (OAuth, API keys, mTLS)
- Distributed tracing (W3C Trace Context)
- Version management and compatibility

### Workflow Agents Decision Matrix

Choose the right workflow agent based on task dependencies:

| Agent | Pattern | Performance | When to Use | State Passing |
|-------|---------|-------------|-------------|---------------|
| **SequentialAgent** | Assembly Line | O(n*t) linear | Ordered dependencies (A must finish before B) | `output_key` → `{placeholder}` |
| **ParallelAgent** | Taskforce | O(max(t)) concurrent | Independent tasks (can run simultaneously) | All outputs → synthesis agent |
| **LoopAgent** | Refiner | O(iterations*t) | Trial-and-error, iterative improvement | Previous iteration feedback |

**Performance Example** (from chapter):
- Sequential (3 agents @ 5s each): 15 seconds total
- Parallel (3 agents @ 5s each): 5 seconds total (67% faster)
- Loop (3 iterations @ 5s each): 15 seconds max

### State Communication Mechanism

Agents communicate by writing to and reading from shared state:

**Write with output_key**:
```python
diagnostics_agent = Agent(
    name="DiagnosticsAgent",
    output_key="diagnostic_result",  # Saves output to state["diagnostic_result"]
    instruction="Analyze the wiring error and provide diagnosis..."
)
```

**Read with {placeholder}**:
```python
warranty_agent = Agent(
    name="WarrantyAgent",
    instruction="""
    Based on this diagnosis: {diagnostic_result}
    Check if the issue is covered under warranty...
    """  # Reads from state["diagnostic_result"]
)
```

**Flow**: Agent A writes → State → Agent B reads → Agent B writes → State → Agent C reads

### Protocol Selection Framework

**When should you use MCP vs A2A?** Use this decision tree:

```
Need to extend agent capabilities across network?
├─ Stateless operations (DB query, API call)?
│  └─ Use MCP
│     • Request-response pattern
│     • No conversation history
│     • Examples: Query database, call weather API, read file
│
└─ Stateful delegation (complex judgment task)?
   └─ Use A2A
      • Multi-turn conversation
      • Maintains context across turns
      • Examples: Troubleshoot issue, negotiate refund, analyze case
```

**MCP vs A2A Comparison**:

| Dimension | MCP | A2A |
|-----------|-----|-----|
| **Purpose** | Tool access | Agent delegation |
| **Pattern** | Request-response | Conversational |
| **State** | Stateless (each call independent) | Stateful (conversation history) |
| **Latency** | Low (single network call) | Variable (multiple turns) |
| **Use When** | Deterministic operations | Requires reasoning/empathy |
| **Examples** | `query_database(sql)`, `get_weather(city)` | "Troubleshoot this wiring issue", "Negotiate refund" |

### Four Production Challenges

Enterprise deployments must address these critical concerns:

**1. Trust** (Security):
- How do agents authenticate each other?
- Solutions: OAuth 2.0, API keys, mTLS, OpenID Connect

**2. Extension** (Versioning):
- How do agents evolve without breaking compatibility?
- Solutions: Extension URIs, optional features, backward-compatible changes

**3. Visibility** (Tracing):
- How do you debug distributed agent flows?
- Solutions: W3C Trace Context, distributed logging, single trace ID

**4. Evolution** (Compatibility):
- How do you deploy v2 while v1 clients still exist?
- Solutions: Semantic versioning, versioned AgentCards, gradual migration

## Learning Path

| # | Sample | Pattern | Chapter Concepts | What You'll Learn |
|---|--------|---------|------------------|-------------------|
| 1 | `01_sequential_agent/` | SequentialAgent | **Ordered workflows** (state passing, dependencies) | output_key, {placeholder} syntax |
| 2 | `02_parallel_agent/` | ParallelAgent | **Concurrent execution** (O(n*t) → O(max(t)) latency) | Synthesis patterns, independent tasks |
| 3 | `03_loop_agent/` | LoopAgent | **Iterative refinement** (escalate termination, max_iterations) | Trial-and-error, early exit |
| 4 | `04_mcp_agent/` | MCP Integration | **Stateless tool access** (request-response, schema-based) | MCPToolset, external resources |
| 5 | `05_a2a_server/` | A2A Server | **Agent exposure** (to_a2a(), AgentCard) | Publishing agents as HTTP services |
| 6 | `06_a2a_client/` | A2A Client | **Remote delegation** (RemoteA2aAgent, conversational) | Consuming remote agents |
| 7 | `07_hybrid_team/` | Hybrid Architecture | **Full system** (local + A2A + MCP combined) | Realistic enterprise pattern |
| 8 | `08_production_agent/` | Production Patterns | **Enterprise concerns** (security schemes, tracing, versioning) | OAuth, W3C Trace Context, extensions |

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed
- **Google Cloud account** with Gemini API access
- **ADK installed**: `pip install google-adk`
- **Additional dependencies**:
  ```bash
  pip install uvicorn mcp python-dotenv
  ```

## Quick Start

1. **Set up API key**:
   ```bash
   export GOOGLE_API_KEY=your-api-key-here
   ```

2. **Run any sample**:
   ```bash
   cd chapter-4/01_sequential_agent
   adk web .
   ```

3. **Open browser**: Navigate to http://localhost:8000

## Key Concepts

### Workflow Agents (Local Orchestration)

ADK provides three workflow agents for deterministic orchestration:

| Agent | Pattern | When to Use |
|-------|---------|-------------|
| `SequentialAgent` | Assembly Line | Tasks with dependencies (A must complete before B) |
| `ParallelAgent` | Independent Taskforce | Independent tasks that can run concurrently |
| `LoopAgent` | Iterative Refiner | Trial-and-error, progressive refinement |

### Communication Patterns

**State Passing with output_key**:
```python
agent_a = Agent(
    name="AgentA",
    output_key="result_a",  # Saves output to state["result_a"]
    instruction="Analyze the issue..."
)

agent_b = Agent(
    name="AgentB",
    instruction="Use {result_a} to..."  # Reads from state["result_a"]
)
```

### Distributed Protocols

| Protocol | Purpose | When to Use |
|----------|---------|-------------|
| **MCP** | Tool access | Stateless operations (database queries, API calls) |
| **A2A** | Agent delegation | Stateful, conversational delegation to specialists |

## Protocol Decision Framework

### Decision Tree: Workflow vs MCP vs A2A

Use this framework to choose the right orchestration approach:

```
Need to coordinate multiple capabilities?
│
├─ All in same process (single deployment)?
│  └─ Use WORKFLOW AGENTS
│     │
│     ├─ Ordered dependencies? → SequentialAgent
│     ├─ Independent tasks? → ParallelAgent
│     └─ Trial-and-error? → LoopAgent
│
└─ Across network boundaries (different services)?
   │
   ├─ Stateless operations (no conversation)?
   │  └─ Use MCP
   │     Examples:
   │     • Query PostgreSQL database
   │     • Call REST API
   │     • Read/write files
   │     • Fetch weather data
   │
   └─ Stateful delegation (conversational)?
      └─ Use A2A
         Examples:
         • "Troubleshoot this wiring issue" (multi-turn diagnosis)
         • "Negotiate a refund for this customer" (judgment required)
         • "Research this complex billing discrepancy" (context-dependent)
```

### MCP vs A2A: Detailed Comparison

| Dimension | MCP (Model Context Protocol) | A2A (Agent-to-Agent Protocol) |
|-----------|------------------------------|-------------------------------|
| **Communication Pattern** | Request → Response | Multi-turn conversation |
| **State Management** | Stateless (each call independent) | Stateful (conversation history) |
| **Typical Latency** | Low (single network round-trip) | Variable (multiple LLM calls) |
| **Best For** | Deterministic operations | Complex judgment tasks |
| **Conversation History** | Not maintained | Full context preserved |
| **Use When** | You know exact operation needed | Agent needs to reason about task |
| **Typical Duration** | Milliseconds to seconds | Seconds to minutes |
| **Error Handling** | Simple (retry on failure) | Complex (agent can ask clarifying questions) |
| **Integration Complexity** | Low (standard tool definition) | Medium (HTTP server, AgentCard) |

**Example Comparison**:

**MCP Scenario**:
```
User → Agent: "What's my order status?"
Agent → MCP Tool: query_database("SELECT * FROM orders WHERE user_id=123")
MCP Tool → Agent: {"order_id": "ORD-456", "status": "shipped"}
Agent → User: "Your order ORD-456 has shipped!"
# Single round-trip, deterministic
```

**A2A Scenario**:
```
User → Coordinator: "My thermostat has a wiring error"
Coordinator → TechnicalAgent: "Diagnose this wiring issue: [details]"
TechnicalAgent: "What error code is displayed?"
Coordinator → User: "The technician needs to know the error code"
User → Coordinator: "E12"
Coordinator → TechnicalAgent: "Error code is E12"
TechnicalAgent → Coordinator: "E12 indicates reversed C-wire. Repair needed."
Coordinator → User: "You need a technician visit for reversed wiring"
# Multi-turn, conversational, judgment required
```

### Workflow Agent Selection

When using local orchestration (same process), choose based on task structure:

| Agent Type | When to Use | Performance | Example Scenario |
|------------|-------------|-------------|------------------|
| **SequentialAgent** | • Tasks have dependencies<br>• Output of A needed for B<br>• Order matters | O(n*t)<br>Linear | 1. Diagnose issue<br>2. Check warranty (needs diagnosis)<br>3. Process claim (needs warranty status) |
| **ParallelAgent** | • Tasks are independent<br>• No shared dependencies<br>• Order doesn't matter | O(max(t))<br>Concurrent | 1. Check technical specs (independent)<br>2. Validate warranty (independent)<br>3. Get billing info (independent)<br>→ Synthesize all results |
| **LoopAgent** | • Trial-and-error needed<br>• Iterative refinement<br>• May succeed early | O(iterations*t)<br>Variable | Try fixes:<br>1. Power cycle (fails)<br>2. Firmware reset (fails)<br>3. Replace battery (succeeds → exit early) |

**Performance Impact** (from chapter examples):

```
Scenario: 3 agents, each takes 5 seconds

SequentialAgent:
Agent A (5s) → Agent B (5s) → Agent C (5s) = 15 seconds total

ParallelAgent:
Agent A (5s) ┐
Agent B (5s) ├→ Synthesis = 5 seconds total (67% faster!)
Agent C (5s) ┘

LoopAgent:
Iteration 1 (5s) → fails
Iteration 2 (5s) → fails
Iteration 3 (5s) → succeeds = 15 seconds (worst case)
                            or 5 seconds (best case if first iteration succeeds)
```

## Sample Dependencies

Some samples work together:

```
+----------------+     +----------------+     +----------------+
| 05_a2a_server  |---->| 06_a2a_client  |---->| 07_hybrid_team |
| (BillingAgent) |     | (Coordinator)  |     | (Full System)  |
+----------------+     +----------------+     +----------------+
        |                                             |
        +---------------------------------------------+

+----------------+
| 04_mcp_agent   |----> Built-in MCP server (mcp_server.py)
| (SupportAgent) |
+----------------+
```

To run the full A2A demo:
```bash
# Terminal 1: Start A2A server
cd 05_a2a_server && uvicorn agent:a2a_app --port 8001

# Terminal 2: Run A2A client
cd 06_a2a_client && adk web .
```

## Production Patterns

### Security Schemes for A2A

Production A2A deployments require authentication. ADK supports multiple security schemes:

| Scheme | Use When | Implementation | Security Level |
|--------|----------|----------------|----------------|
| **API Key** | Simple internal services | `X-API-Key` header | Medium (rotate keys regularly) |
| **HTTP Basic** | Legacy system integration | `Authorization: Basic base64(user:pass)` | Low (use HTTPS only) |
| **Bearer Token** | Modern API authentication | `Authorization: Bearer <token>` | Medium-High |
| **OAuth 2.0** | Enterprise SSO, third-party access | Authorization code flow | High |
| **OpenID Connect** | Identity federation, user auth | OAuth 2.0 + ID tokens | High |
| **Mutual TLS (mTLS)** | Zero-trust networks, high security | Client certificates | Very High |

**Common Pattern: Bearer Token**:
```python
# Server (05_a2a_server)
from google.adk.a2a import to_a2a

a2a_app = to_a2a(
    root_agent,
    security_scheme={
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
)

# Middleware to validate token
@a2a_app.middleware("http")
async def validate_token(request, call_next):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not validate_jwt(auth_header):
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return await call_next(request)
```

**Client Integration**:
```python
# Client (06_a2a_client)
from google.adk.agents import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    url="https://billing-service.example.com",
    headers={"Authorization": f"Bearer {get_jwt_token()}"}
)
```

### AgentCard Mechanism

The **AgentCard** is a JSON document published at `/.well-known/agent-card.json` that describes an A2A agent's capabilities:

**AgentCard Structure**:
```json
{
  "name": "BillingAgent",
  "description": "Handles billing inquiries and refunds",
  "version": "1.2.0",
  "capabilities": ["process_refund", "query_invoices", "update_payment_method"],
  "authentication": {
    "type": "http",
    "scheme": "bearer"
  },
  "extensions": [
    "urn:a2a:ext:priority-routing",
    "urn:a2a:ext:audit-logging"
  ],
  "contact": "billing-team@example.com"
}
```

**Purpose**:
- **Discovery**: Clients learn what the agent can do
- **Negotiation**: Client activates optional extensions
- **Versioning**: Multiple versions can coexist

**Extension Activation**:
```python
# Client requests specific extensions
remote_agent = RemoteA2aAgent(
    url="https://billing-service.example.com",
    headers={
        "Authorization": f"Bearer {token}",
        "X-A2A-Extensions": "urn:a2a:ext:audit-logging"
    }
)
```

### Distributed Tracing with W3C Trace Context

Production multiagent systems need **distributed tracing** to debug flows across services:

**W3C Trace Context Headers**:
- `traceparent`: Single trace ID that flows through all services
  - Format: `00-<trace-id>-<span-id>-<flags>`
  - Example: `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`
- `tracestate`: Vendor-specific trace data

**How ADK Auto-Instruments**:
```python
# ADK automatically propagates trace context
coordinator = Agent(name="Coordinator")
remote_billing = RemoteA2aAgent(url="https://billing.example.com")

# When coordinator calls remote_billing, ADK:
# 1. Reads traceparent from incoming request
# 2. Creates child span
# 3. Passes traceparent to remote_billing
# 4. All operations appear in single trace
```

**Benefits**:
- **Single trace ID** across all services (coordinator → technical → warranty → billing)
- **Latency breakdown** (which agent took longest?)
- **Error attribution** (which service failed?)
- **Service dependencies** (visualize call graph)

**Integration with Observability**:
```python
# Export traces to Google Cloud Trace
from google.adk.observability import configure_tracing

configure_tracing(
    project_id="your-project",
    service_name="smarthome-support"
)
```

### Extension System

A2A supports four types of extensions for backward-compatible evolution:

**1. Data-Only Extensions** (safest):
```json
{
  "extensions": ["urn:example:customer-priority"],
  "priority": "gold"  // New field, ignored by old clients
}
```

**2. Profile Extensions** (behavioral variants):
```json
{
  "extensions": ["urn:a2a:ext:streaming"],
  "supportStreaming": true
}
```

**3. Method Extensions** (new capabilities):
```json
{
  "extensions": ["urn:example:bulk-operations"],
  "methods": ["bulk_refund", "batch_invoice_query"]
}
```

**4. State Machine Extensions** (workflow changes):
```json
{
  "extensions": ["urn:example:approval-workflow"],
  "requiresApproval": true
}
```

**Migration Pattern**:
```
v1.0 (no extensions) → Deploy
    ↓
v1.1 (add optional extension) → Old clients still work
    ↓
v1.2 (more clients adopt extension) → Gradual migration
    ↓
v2.0 (extension becomes required) → All clients upgraded
```

### Versioning Strategy

**Semantic Versioning** for AgentCards:
- **Major** (v1 → v2): Breaking changes (old clients incompatible)
- **Minor** (v1.2 → v1.3): New features (backward compatible)
- **Patch** (v1.2.3 → v1.2.4): Bug fixes

**Versioned URLs**:
```
https://billing.example.com/v1/  # Old clients
https://billing.example.com/v2/  # New clients
https://billing.example.com/     # Redirects to latest
```

**Gradual Migration**:
1. Deploy v2 alongside v1 (both running)
2. Update AgentCard to advertise both versions
3. Clients migrate at their own pace
4. Monitor v1 usage → deprecate when zero traffic

## Chapter Examples Reference

Each sample implements specific examples from the chapter text:

| Sample | Chapter Examples | Description |
|--------|------------------|-------------|
| 01_sequential_agent | Example 4-5 | SequentialAgent workflow |
| 02_parallel_agent | Example 4-6 | ParallelAgent workflow |
| 03_loop_agent | Examples 4-7, 4-8 | LoopAgent with escalate |
| 04_mcp_agent | Example 4-9 | MCPToolset integration |
| 05_a2a_server | Examples 4-10, 4-11 | to_a2a() and uvicorn |
| 06_a2a_client | Example 4-12 | RemoteA2aAgent |
| 07_hybrid_team | Examples 4-13, 4-14 | Full hybrid architecture |
| 08_production_agent | Examples 4-15 to 4-22 | Security, tracing, versioning |

## Next Steps

After completing this chapter:

1. **Chapter 5**: Evaluation and Optimization - Measure and improve agent quality

2. **External Codelabs**:
   - [Build and deploy an ADK agent with MCP on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/use-mcp-server-on-cloud-run-with-an-adk-agent)
   - [Build a Travel Agent using MCP Toolbox for Databases](https://codelabs.developers.google.com/travel-agent-mcp-toolbox-adk)
   - [The Summoner's Concord - Architecting multiagent systems](https://codelabs.developers.google.com/agentverse-architect/instructions)

## Related Resources

### Official Documentation
- [ADK Multi-Agent Documentation](https://google.github.io/adk-docs/agents/multi-agents/) - Workflow agents, state passing
- [ADK A2A Integration](https://google.github.io/adk-docs/a2a/) - Publishing and consuming remote agents
- [ADK MCP Integration](https://google.github.io/adk-docs/mcp/) - External tool integration
- [Workflow Agents Guide](https://google.github.io/adk-docs/agents/workflow-agents/) - Sequential, Parallel, Loop patterns

### Protocol Specifications
- [A2A Protocol Specification](https://a2a-protocol.org/latest/) - Complete protocol reference
- [A2A AgentCard Format](https://a2a-protocol.org/latest/agent-card) - Discovery and capabilities
- [A2A Security Schemes](https://a2a-protocol.org/latest/security) - Authentication patterns
- [A2A Extensions](https://a2a-protocol.org/latest/extensions) - Extensibility mechanism
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) - Tool integration standard
- [MCP Specification](https://modelcontextprotocol.io/docs/specification) - Complete MCP reference

### MCP Toolbox & Integrations
- [MCP Toolbox for Databases](https://cloud.google.com/blog/products/ai-machine-learning/mcp-toolbox-for-databases-now-supports-model-context-protocol) - PostgreSQL, MySQL, BigQuery, Firestore
- [MCP Healthcare Toolbox](https://cloud.google.com/healthcare-api/docs/how-tos/mcp-server) - FHIR and DICOM integration
- [Building Custom MCP Servers](https://modelcontextprotocol.io/docs/tools/building-servers) - Create your own MCP tools

### Video Tutorials
- [Foundations of Multiagent Systems with ADK](https://www.youtube.com/watch?v=ADK_multiagent) - Architecture overview
- [Workflow Agents and Communication](https://www.youtube.com/watch?v=ADK_workflow) - Sequential, Parallel, Loop patterns
- [Building MCP Servers with ADK](https://www.youtube.com/watch?v=ADK_mcp) - Tool integration
- [A2A Protocol Deep Dive](https://www.youtube.com/watch?v=A2A_protocol) - Distributed agent collaboration

### Hands-On Codelabs
- [Build and Deploy an ADK Agent with MCP on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/use-mcp-server-on-cloud-run-with-an-adk-agent) - Production deployment
- [Build a Travel Agent using MCP Toolbox for Databases](https://codelabs.developers.google.com/travel-agent-mcp-toolbox-adk) - Database integration
- [The Summoner's Concord - Architecting Multiagent Systems](https://codelabs.developers.google.com/agentverse-architect/instructions) - Advanced patterns

### Production Guides
- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/) - Distributed tracing standard
- [OAuth 2.0 Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics) - Security patterns
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html) - Identity federation
- [Semantic Versioning 2.0.0](https://semver.org/) - Versioning strategy

### Next Steps
- **Chapter 5**: Evaluation and Optimization - Measure and improve multiagent system quality
- **Chapter 6**: Fine-tuning and Infrastructure - Optimize model performance and deployment
- **Chapter 7**: MLOps for LLM Systems - Production monitoring, CI/CD, and observability

---

[<- Previous Chapter](../chapter-3/) | [Home](../) | [Next Chapter ->](../chapter-5/)
