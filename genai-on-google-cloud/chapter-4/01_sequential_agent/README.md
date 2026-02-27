# Sequential Agent - The Assembly Line Pattern

**Concept**: SequentialAgent for ordered workflow execution
**Estimated Time**: 10-15 minutes
**Theme**: SmartHome Customer Support - Warranty Claim Processing
**Chapter Example**: 4-5

## What You'll Learn

- How `SequentialAgent` executes sub-agents in strict order
- Using `output_key` to save agent output to state
- Reading state values with `{placeholder}` syntax in instructions
- Building dependent workflows where each step relies on previous results

## Prerequisites

- Python 3.10+
- Google Cloud account with Gemini API access
- ADK installed (`pip install google-adk`)

## Quick Start

1. **Set up API key**:
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

- "My smart thermostat is showing a wiring error. Can you check if it's covered under warranty?"
- "I bought a thermostat 3 months ago and the temperature sensor is faulty. Can I get a replacement?"
- "Device THERM-2024-001 is not working properly. Please help."

## Code Walkthrough

### The Workflow Pattern

The warranty claim workflow has three sequential steps:

```
┌──────────────────┐     ┌───────────────────┐     ┌─────────────────┐
│ DiagnosticAgent  │────▶│ WarrantyCheckAgent│────▶│ ClaimProcessor  │
│                  │     │                   │     │                 │
│ output_key:      │     │ reads:            │     │ reads:          │
│ "diagnosis_result"│     │ {diagnosis_result}│     │ {diagnosis_result}│
│                  │     │ output_key:       │     │ {warranty_status}│
│                  │     │ "warranty_status" │     │                 │
└──────────────────┘     └───────────────────┘     └─────────────────┘
```

### Key Code Pattern

```python
# Step 1: Agent saves output to state via output_key
diagnostic_agent = Agent(
    model="gemini-2.5-flash",
    name="DiagnosticAgent",
    instruction="Analyze the issue...",
    output_key="diagnosis_result",  # Saves to state["diagnosis_result"]
    tools=[check_device_logs, analyze_error_patterns]
)

# Step 2: Next agent reads from state via {placeholder}
warranty_check_agent = Agent(
    model="gemini-2.5-flash",
    name="WarrantyCheckAgent",
    instruction="Based on {diagnosis_result}, verify warranty...",  # Reads state
    output_key="warranty_status",
    tools=[lookup_purchase_date, check_coverage_terms]
)

# Step 3: Final agent reads from multiple state values
claim_processor = Agent(
    model="gemini-2.5-flash",
    name="ClaimProcessor",
    instruction="If {warranty_status} indicates coverage, process using {diagnosis_result}...",
    tools=[initiate_replacement, send_confirmation]
)

# Orchestrate in sequence
warranty_claim_workflow = SequentialAgent(
    name="WarrantyClaimWorkflow",
    sub_agents=[diagnostic_agent, warranty_check_agent, claim_processor]
)
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| `SequentialAgent` | Executes sub-agents in strict order, one after another |
| `output_key` | Automatically saves agent's final response to `state[key]` |
| `{placeholder}` | Reads value from `state["placeholder"]` when processing instructions |
| Shared Context | All agents share the same `InvocationContext`, enabling data flow |

## When to Use SequentialAgent

Use SequentialAgent when:
- **Tasks have dependencies**: B needs output from A to proceed
- **Order matters**: Steps must execute in a specific sequence
- **You need predictability**: Deterministic execution order for debugging

Don't use when:
- Tasks are independent (use `ParallelAgent` instead)
- You need dynamic routing (use `LlmAgent` with `sub_agents`)

## What's Next

- [02_parallel_agent](../02_parallel_agent/) - Learn concurrent execution
- [03_loop_agent](../03_loop_agent/) - Learn iterative refinement
- [ADK Sequential Agent Docs](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
