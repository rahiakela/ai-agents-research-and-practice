<div align="center">
  <img src="../images/owl-front.png" alt="Chapter Guide" width="100"/>

  # Chapter 3: Building Multimodal Agents with ADK
</div>

---

## Overview

This chapter introduces the **Agent Development Kit (ADK)**, Google's open-source framework for building production-grade AI agents. Through hands-on examples using a **SmartHome Customer Support** theme, you'll learn:

- **Agent Fundamentals**: Creating agents with instructions, tools, and multi-agent delegation
- **State Management**: Persisting data across sessions with temp, user, and app scopes
- **Semantic Memory**: Using Vertex AI Memory Bank for cross-session personalization
- **Multimodal Capabilities**: Processing images and generating artifacts
- **Real-Time Streaming**: Building voice-enabled agents with the Live API
- **Security & Guardrails**: Implementing callbacks and plugins for enterprise compliance

## Learning Objectives

Upon completing this chapter's exercises, you will be able to:

- Create and run ADK agents with `adk web`
- Build custom tools that extend agent capabilities
- Design multi-agent systems with specialist delegation
- Manage state across different scopes (temp, user, app)
- Integrate Vertex AI Memory Bank for semantic memory
- Process images and store artifacts
- Configure real-time streaming with the Live API
- Implement security callbacks and authorization patterns

## Key Concepts Deep Dive

### ADK Philosophy
The Agent Development Kit handles the complex infrastructure of **multiturn stateful conversations** so you can focus on defining **what your agent does**, not how the runtime works. The framework manages the event loop, state persistence, and multimodal content routing.

### Runtime Architecture
ADK uses an **event loop pattern**:
```
Runner → Execution Logic → Services (LLM, Memory, State)
```
This architecture means you define agents declaratively (name, instruction, tools) while ADK handles all runtime coordination.

### Tools vs Subagents Framework
**When should you use a tool vs. delegate to a subagent?** Use this decision matrix from the chapter:

| Dimension | Tools | Subagents |
|-----------|-------|-----------|
| **Operation Type** | Deterministic (lookup order) | Context-dependent (troubleshoot issue) |
| **Reasoning Required** | None (execute function) | Understanding/empathy needed |
| **Interface** | Fixed parameters | Dynamic conversational flow |
| **Performance** | Fast (single call) | Variable latency (multi-turn) |
| **Frequency** | High-frequency operations | Complex, less frequent tasks |
| **State Needs** | Stateless | Maintains conversational context |

**Examples from SmartHome**:
- **Tools**: `get_order_status(order_id)`, `check_warranty(product_id)` → deterministic lookups
- **Subagents**: TechnicalSupportAgent, BillingSpecialist → require judgment and empathy

### State Management Strategy
ADK provides **three state scopes** with different lifecycles:

| Scope | Lifetime | Use Cases | SmartHome Example |
|-------|----------|-----------|-------------------|
| `temp:` | Single session | Verification codes, search filters | `temp:verification_code` for 2FA |
| `user:` | Cross-session (per user) | Order history, preferences | `user:order_history`, `user:loyalty_tier` |
| `app:` | System-wide (all users) | Business rules, policies | `app:saved_cart_expiry_days` |

**Interaction Pattern**: Agents read from state via `{placeholder}` syntax and write using `output_key`.

### Memory Duality
ADK supports **two complementary memory approaches**:

1. **Structured State** (explicit): Developers define exact keys (`user:order_history`)
   - Use when: You know the structure upfront (shopping cart, loyalty points)

2. **Semantic Memory** (extracted): Memory Bank automatically extracts insights
   - Use when: Conversational context matters ("customer prefers evening appointments")
   - Integrates via `{memory}` placeholder in instructions

### Multimodal Capabilities
ADK's `types.Content` model unifies text, images, and artifacts:
- **Input**: Process images for troubleshooting (`types.Content.from_file()`)
- **Output**: Generate artifacts (repair guides, diagrams) with scoped storage
- **Persistence**: Artifacts can be session-scoped (`temp:`) or user-scoped (`user:`)

### Production Patterns
**Three critical patterns for enterprise deployments**:

1. **Long-Running Operations**: `LongRunningFunctionTool` for operations >30s
   - Pattern: Initiate → Return tracking ID → Status polling

2. **Human-in-the-Loop Safety**: `require_confirmation=True` for sensitive tools
   - Example: Refund processing, account deletion

3. **Enterprise Compliance**: Callbacks (agent-level) vs Plugins (organization-wide)
   - PII redaction via custom `BasePlugin` implementations

## Agent Samples

All samples use a unified **SmartHome Customer Support** theme, matching the code examples from Chapter 3:

| # | Sample | Chapter Examples | Concept | Chapter Concepts | Time |
|---|--------|-----------------|---------|------------------|------|
| 1 | [01_hello_agent](./01_hello_agent/) | 3-1, 3-2 | Basic Agent | **Minimal agent definition** (7-line pattern, runtime event loop) | ~5 min |
| 2 | [02_tool_agent](./02_tool_agent/) | 3-3 | Function Tools | **Tool integration** (seamless orchestration, function calling) | ~10 min |
| 3 | [03_multi_agent](./03_multi_agent/) | 3-5, 3-7 | Hybrid Architecture | **Delegation patterns** (tools vs subagents, specialist routing) | ~10 min |
| 4 | [04_stateful_agent](./04_stateful_agent/) | 3-8, 3-10 | State Scopes | **State lifecycle** (temp/user/app scopes, persistence layers) | ~15 min |
| 5 | [05_memory_agent](./05_memory_agent/) | 3-14, 3-15, 3-16 | Memory Bank | **Semantic memory** (dual-layer approach, conversational insights) | ~15 min |
| 6 | [06_multimodal_agent](./06_multimodal_agent/) | 3-17, 3-19 | Image & Artifacts | **Multimodal processing** (types.Content model, artifact scoping) | ~10 min |
| 7 | [07_streaming_agent](./07_streaming_agent/) | 3-18 | Live API | **Real-time streaming** (WebSocket infrastructure, voice interaction) | ~15 min |
| 8 | [08_guardrails_agent](./08_guardrails_agent/) | 3-20, 3-21, 3-22 | Safety & Compliance | **Production guardrails** (async ops, HITL, PII redaction) | ~10 min |

## Prerequisites

### 1. Python Environment
```bash
# Python 3.10+ required
python --version

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows
```

### 2. Install ADK
```bash
pip install google-adk google-genai python-dotenv
```

### 3. Get API Key
- Visit [Google AI Studio](https://aistudio.google.com/apikey) to get a Gemini API key
- Or use Vertex AI with application default credentials

### 4. Configure Environment
Each agent folder has a `.env.example` file:
```bash
cd 01_hello_agent
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Quick Start

1. **Navigate to any agent folder**:
   ```bash
   cd chapter-3/01_hello_agent
   ```

2. **Set up your API key**:
   ```bash
   cp .env.example .env
   # Edit .env with your key
   ```

3. **Run with ADK Web**:
   ```bash
   adk web .
   ```

4. **Open browser**: Navigate to http://localhost:8000

## Directory Structure

```
chapter-3/
├── README.md                    # This file
├── 01_hello_agent/              # Example 3-1: Basic agent
├── 02_tool_agent/               # Example 3-3: Order lookup tools
├── 03_multi_agent/              # Example 3-7: Hybrid architecture
├── 04_stateful_agent/           # Example 3-10: State with cart expiry
├── 05_memory_agent/             # Example 3-16: Memory placeholder
├── 06_multimodal_agent/         # Example 3-17: Artifact storage
├── 07_streaming_agent/          # Example 3-18: Live API
├── 08_guardrails_agent/         # Example 3-20: LongRunningFunctionTool
└── .plan/
    └── IMPLEMENTATION_PLAN.md   # Development notes
```

## Key ADK Concepts

### Agent Definition (Example 3-1)
```python
from google.adk.agents import Agent

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="You help customers with their SmartHome products.",
    tools=[...],           # Function tools
    sub_agents=[...]       # Specialist agents
)
```

### Running Agents (Example 3-2)
```bash
# Interactive web interface
adk web .

# Command-line interface
adk run .

# API server for integration
adk api_server .
```

### State Scopes (Examples 3-8, 3-10)
- `temp:key` - Session-only, disappears after conversation ends
- `user:key` - Cross-session, persists for specific user
- `app:key` - System-wide, shared across all users (e.g., `app:saved_cart_expiry_days`)

### Memory Placeholder (Example 3-16)
```python
instruction="""...
Before responding, review these memories:
---
Retrieved Memories:
{memory}
---
Use this context to provide personalized support..."""
```

## Design Decision Frameworks

### When to Use Tools vs Subagents

Use this decision matrix to architect your agent system:

```
Need to extend agent capabilities?
├─ Deterministic operation with fixed parameters?
│  └─ Use TOOL (e.g., get_order_status, check_warranty)
└─ Requires reasoning, empathy, or conversational flow?
   └─ Use SUBAGENT (e.g., TechnicalSupportAgent, BillingSpecialist)
```

**Key indicators for tools**:
- ✅ Fast execution required (< 5 seconds)
- ✅ High-frequency operations (called many times)
- ✅ No conversational context needed
- ✅ Stateless (each call independent)

**Key indicators for subagents**:
- ✅ Complex judgment required (troubleshooting, negotiation)
- ✅ Multi-turn conversation needed
- ✅ Domain-specific expertise (technical vs billing mindset)
- ✅ Maintains context across turns

### State Scope Selection Guide

Choose the right scope based on data lifetime and sharing requirements:

| Question | Answer → Scope |
|----------|---------------|
| Does this data persist after the conversation ends? | No → `temp:` |
| Does each user need their own version? | Yes → `user:` |
| Is this a system-wide setting or business rule? | Yes → `app:` |
| Should this survive server restarts? | Yes → `user:` or `app:` |

**SmartHome Examples**:
```python
# Session-only (expires after conversation)
temp:verification_code = "ABC123"
temp:search_filters = {"category": "thermostats"}
temp:session_metrics = {"questions_asked": 5}

# User-specific (persists across sessions)
user:order_history = [{"order_id": "ORD-123", ...}]
user:preferences = {"notification_method": "email"}
user:loyalty_tier = "gold"

# System-wide (shared by all users)
app:saved_cart_expiry_days = 30
app:warranty_policy = {"standard": "1 year", "premium": "3 years"}
app:business_hours = {"open": "9am", "close": "5pm"}
```

### Persistence Backend Comparison

Choose the right session service for your deployment environment:

| Backend | Use When | Pros | Cons |
|---------|----------|------|------|
| **InMemorySessionService** | Development, testing | • Zero configuration<br>• Instant feedback<br>• No external dependencies | • Data lost on restart<br>• Single-server only |
| **DatabaseSessionService** | Self-managed production | • Full control<br>• Standard SQL (PostgreSQL, MySQL, SQLite)<br>• Backup/migration tools | • You manage infrastructure<br>• Schema maintenance |
| **VertexAiSessionService** | Fully managed production | • Lowest ops overhead<br>• Automatic scaling<br>• Built-in redundancy | • Requires Google Cloud<br>• Cost per API call |

**Typical progression**:
```
Development → InMemory (prototype quickly)
    ↓
Staging → Database (test with realistic data)
    ↓
Production → VertexAi (focus on agent logic, not infrastructure)
```

## Troubleshooting

### API Key Issues
```bash
# Verify your key is set
echo $GOOGLE_API_KEY

# Test with a simple request
python -c "from google import genai; client = genai.Client(); print(client.models.list())"
```

### ADK Not Found
```bash
# Ensure ADK is installed
pip install --upgrade google-adk

# Verify installation
adk --version
```

### Port Already in Use
```bash
# Use a different port
adk web . --port 8080
```

## Production Patterns

### Long-Running Operations Pattern

For operations that take >30 seconds (e.g., firmware updates, bulk processing), use `LongRunningFunctionTool`:

```python
from google.adk.toolkits import LongRunningFunctionTool

async def process_firmware_update(device_id: str) -> str:
    """Initiate firmware update (returns tracking ID)"""
    job_id = start_background_job(device_id)
    return f"Update initiated. Track with ID: {job_id}"

async def check_update_status(job_id: str) -> str:
    """Poll update status"""
    status = get_job_status(job_id)
    return f"Status: {status['state']} - {status['progress']}%"

root_agent = Agent(
    tools=[
        LongRunningFunctionTool(process_firmware_update),
        check_update_status  # Regular tool for status checks
    ]
)
```

**Pattern Flow**:
1. User: "Update my thermostat firmware"
2. Agent calls `process_firmware_update()` → returns `job_id`
3. Agent: "Update started (ID: ABC123). I'll check the status..."
4. Agent calls `check_update_status(job_id)` → "85% complete"

### Human-in-the-Loop Safety

For sensitive operations (refunds, account changes), require explicit confirmation:

```python
from google.adk.toolkits import FunctionTool

@FunctionTool(require_confirmation=True)
def process_refund(order_id: str, amount: float) -> str:
    """Process a refund to customer's payment method"""
    # This will pause and ask user: "Confirm: Process refund of $49.99 for order ORD-123?"
    return initiate_refund(order_id, amount)
```

**When to use**:
- ✅ Financial transactions (refunds, payments)
- ✅ Account modifications (delete account, change email)
- ✅ Data deletion (purge order history)
- ✅ External actions (send email to customer, call API)

### Enterprise Compliance: Callbacks vs Plugins

**Callbacks** (agent-level): Custom logic for specific agent behavior
```python
from google.adk.callbacks import BaseCallback

class BillingAuditCallback(BaseCallback):
    async def on_tool_end(self, tool_name: str, result: Any):
        if tool_name == "process_refund":
            await log_to_audit_system(result)

billing_agent = Agent(
    name="BillingAgent",
    callbacks=[BillingAuditCallback()]  # Applied to this agent only
)
```

**Plugins** (organization-wide): Policies applied to all agents
```python
from google.adk.plugins import BasePlugin

class PiiRedactionPlugin(BasePlugin):
    async def on_llm_start(self, messages: list):
        # Redact SSN, credit cards before sending to LLM
        return redact_pii(messages)

# Apply to ALL agents in your organization
root_agent = Agent(plugins=[PiiRedactionPlugin()])
```

**Decision guide**:
- Use **Callbacks** for: Agent-specific logging, custom tool handling
- Use **Plugins** for: Security policies, PII redaction, cost tracking

### Semantic Memory Architecture

Integrate Vertex AI Memory Bank for conversational insights:

**Three-step integration**:

1. **Configure Memory Service** (in root agent):
```python
from google.adk.services.memory import VertexAiMemoryService

root_agent = Agent(
    memory=VertexAiMemoryService(
        memory_id="smarthome-support-memories"
    )
)
```

2. **Add Memory Placeholder** (in instruction):
```python
instruction="""You are a SmartHome customer support agent.

Before responding, review these memories:
---
Retrieved Memories:
{memory}
---

Use this context to personalize your support..."""
```

3. **Memory Bank Auto-Extraction**:
   - ADK automatically extracts insights ("Customer prefers email notifications")
   - Memories retrieved via semantic search on user query
   - No manual memory management required

**Use cases**:
- Customer preferences (communication method, appointment times)
- Previous issues (troubleshooting history)
- Product recommendations based on past conversations

## Related Resources

### Official Documentation
- [ADK Documentation](https://google.github.io/adk-docs/) - Complete framework reference
- [ADK Multi-Agent Guide](https://google.github.io/adk-docs/agents/multi-agents/) - Subagent patterns
- [State Management Guide](https://google.github.io/adk-docs/agents/state/) - Scopes and persistence
- [Memory Bank Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank) - Semantic memory integration

### Language SDKs
- [ADK Python](https://github.com/google/adk-python) - Primary SDK (used in this chapter)
- [ADK Java](https://github.com/google/adk-java) - For JVM environments
- [ADK Go](https://github.com/google/adk-go) - For Go developers
- [ADK TypeScript](https://github.com/google/adk-typescript) - For JavaScript/TypeScript

### Code Examples
- [ADK Samples Repository](https://github.com/google/adk-samples) - Official production-ready examples
- [Agent Garden](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-garden) - Pre-built agent templates

### Video Tutorials
- [Getting Started with Agent Development Kit](https://www.youtube.com/watch?v=ADK_intro) - Framework overview
- [Building Your First ADK Agent](https://www.youtube.com/watch?v=ADK_first_agent) - Hands-on walkthrough
- [ADK State Management Deep Dive](https://www.youtube.com/watch?v=ADK_state) - Advanced state patterns

### Vertex AI Services
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) - Managed runtime
- [Agent Builder Console](https://console.cloud.google.com/vertex-ai/generative/agent-builder) - No-code agent creation
- [Live API Documentation](https://ai.google.dev/api/live) - Real-time streaming reference

### Next Steps
- **Chapter 4**: Learn to orchestrate multi-agent teams with workflow agents, MCP, and A2A protocols

---

[← Previous Chapter](../chapter-2/) | [Home](../) | [Next Chapter →](../chapter-4/)
