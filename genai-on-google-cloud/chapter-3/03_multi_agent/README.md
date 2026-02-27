# Multi-Agent - Tools vs Subagents

**Concept**: Hybrid architecture with tools AND sub-agents (Examples 3-5, 3-7)
**Estimated Time**: 10 minutes
**Theme**: SmartHome Customer Support

## What You'll Learn

- The difference between tools and sub-agents
- Creating agent hierarchies with `sub_agents=[]`
- Hybrid architecture: root agent with BOTH tools and sub-agents
- How the root agent delegates to specialists
- Observing agent handoffs in ADK web

## Prerequisites

- Python 3.10+
- ADK installed (`pip install google-adk`)
- Gemini API key

## Quick Start

1. **Set up your API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

2. **Run with ADK Web**:
   ```bash
   adk web .
   ```

3. **Open browser**: Navigate to http://localhost:8000

## Try These Prompts

- "What's the status of order ORD-12345?"
- "Track my package with number 1Z999AA10123456784"
- "I want to return order ORD-12346 because it's defective"
- "Can I get a refund for my smart thermostat?"
- "I changed my mind about order ORD-12345, can I return it?"

## Tools vs Sub-Agents: Decision Framework

| Use Tools When | Use Sub-Agents When |
|---------------|---------------------|
| Deterministic operations | Complex reasoning needed |
| Single API calls | Multi-step workflows |
| Calculations | Specialized knowledge |
| Fast, predictable | Context-dependent decisions |
| No reasoning required | Nuanced judgment needed |

### Example Comparison

**Tool** (simple lookup - Example 3-3):
```python
def look_up_order(order_id: str) -> dict:
    # Deterministic: always returns the same data for same input
    return database.query(order_id)
```

**Sub-Agent** (complex workflow - Example 3-5):
```python
returns_agent = Agent(
    name="ReturnsSpecialist",
    instruction="Guide customers through the return process with empathy...",
    tools=[check_return_eligibility, calculate_refund_amount, create_return_label]
)
```

## Code Walkthrough

### Creating a Sub-Agent (Example 3-5)

Sub-agents are agents with their own tools and instructions:

```python
returns_agent = Agent(
    name="ReturnsSpecialist",
    model="gemini-2.5-flash",
    description="Specialist for handling product returns and refunds",
    instruction="""You are a returns specialist. Guide customers through
    the return process with empathy and policy awareness...""",
    tools=[check_return_eligibility, calculate_refund_amount, create_return_label]
)
```

### Hybrid Architecture (Example 3-7)

The root agent has BOTH simple tools for common tasks AND sub-agents for complex workflows:

```python
root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="You help customers with their SmartHome products...",
    tools=[
        look_up_order,            # Simple tools for common tasks
        check_shipping_status
    ],
    sub_agents=[returns_agent]    # Specialist for complex workflows
)
```

### How Delegation Works

1. User sends message to root agent
2. Root agent handles simple queries with tools
3. For complex returns, control transfers to ReturnsSpecialist
4. Sub-agent uses its workflow tools
5. Control returns to root agent when done

## Observing Agent Handoffs

In the ADK web UI:

1. **Events Panel**: Watch for agent transfer events
2. **Agent Name**: Changes when delegation occurs
3. **Tool Calls**: Sub-agents use their own tools

### Event Sequence Example

```
[CustomerSupportAgent] User: "I want to return ORD-12346"
[CustomerSupportAgent] → Delegating to ReturnsSpecialist
[ReturnsSpecialist] Calling check_return_eligibility(...)
[ReturnsSpecialist] Calling calculate_refund_amount(...)
[ReturnsSpecialist] Response: "Your refund of $149.99..."
```

## Architecture

```
┌─────────────────────────────────────────┐
│        CustomerSupportAgent             │
│  (Root Agent - Hybrid Architecture)     │
├─────────────────────────────────────────┤
│  Tools: look_up_order, check_shipping   │
│  Sub-Agents: ReturnsSpecialist          │
└───────────────┬─────────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │  ReturnsSpecialist    │
    ├───────────────────────┤
    │  Tools:               │
    │  - check_eligibility  │
    │  - calculate_refund   │
    │  - create_return_label│
    └───────────────────────┘
```

## Key Concepts

### The `description` Parameter

Sub-agents should have a `description` that helps the root agent decide when to delegate:

```python
Agent(
    name="ReturnsSpecialist",
    description="Specialist for handling product returns and refunds",  # Important!
    ...
)
```

### Why Hybrid Architecture?

- **Simple queries stay fast**: Order lookups don't need sub-agent overhead
- **Complex workflows get attention**: Returns involve multi-step reasoning
- **Clear separation of concerns**: Each agent has focused responsibility
- **Better user experience**: Right tool for the right job

## What's Next?

Now that you understand multi-agent patterns:

- **[04_stateful_agent](../04_stateful_agent/)**: State management across conversations
- **[08_guardrails_agent](../08_guardrails_agent/)**: Security in multi-agent systems

## Related Resources

- [ADK Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [Agent Orchestration](https://google.github.io/adk-docs/agents/workflow-agents/)
- [Tools vs Subagents](https://google.github.io/adk-docs/tools/function-tools/)
