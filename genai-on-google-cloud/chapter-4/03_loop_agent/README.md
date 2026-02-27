# Loop Agent Sample - The Iterative Refiner Pattern

This sample demonstrates **LoopAgent** for iterative execution with escalation.
Based on Chapter 4, Examples 4-7 and 4-8: Progressive Troubleshooting.

## Overview

The LoopAgent pattern is ideal for tasks that require progressive refinement or
repeated attempts until success. The loop continues until either a maximum
iteration count is reached or an agent explicitly terminates via escalation.

```
                    ┌─────────────────────┐
                    │ Customer Issue      │
                    │ "WiFi not connecting"│
                    └──────────┬──────────┘
                               │
           ┌───────────────────▼───────────────────┐
           │           LoopAgent                   │
           │     (TroubleshootingLoop)             │
           │       max_iterations=5                │
           │                                       │
           │  ┌──────────────────────────────┐    │
           │  │ Iteration 1                  │    │
           │  │ ┌────────────────────────┐   │    │
           │  │ │ SolutionAgent          │   │    │
           │  │ │ "Try power cycling"    │   │    │
           │  │ └──────────┬─────────────┘   │    │
           │  │            ▼                  │    │
           │  │ ┌────────────────────────┐   │    │
           │  │ │ ValidationAgent        │   │    │
           │  │ │ "Still not working"    │   │    │
           │  │ └──────────┬─────────────┘   │    │
           │  └────────────┼─────────────────┘    │
           │               │ Not resolved         │
           │               ▼                      │
           │  ┌──────────────────────────────┐    │
           │  │ Iteration 2                  │    │
           │  │ ┌────────────────────────┐   │    │
           │  │ │ SolutionAgent          │   │    │
           │  │ │ "Reset network settings"│  │    │
           │  │ └──────────┬─────────────┘   │    │
           │  │            ▼                  │    │
           │  │ ┌────────────────────────┐   │    │
           │  │ │ ValidationAgent        │   │    │
           │  │ │ "That worked!"         │   │    │
           │  │ │ escalate=True ──────────────────────► EXIT
           │  │ └────────────────────────┘   │    │
           │  └──────────────────────────────┘    │
           └──────────────────────────────────────┘
```

## Key Concepts

### 1. LoopAgent for Iterative Execution (Example 4-7)

```python
from google.adk.agents import LoopAgent

troubleshooting_loop = LoopAgent(
    name="TroubleshootingLoop",
    sub_agents=[solution_agent, validation_agent],
    max_iterations=5  # Safety limit
)
```

The loop executes all sub_agents in sequence, then repeats until termination.

### 2. Early Termination via Escalate (Example 4-8)

```python
def check_resolution(solution_status: str, tool_context) -> dict:
    """Check if issue is resolved and escalate to terminate loop."""
    if "resolved" in solution_status.lower():
        # Set escalate to True to terminate the loop early
        tool_context.actions.escalate = True
        return {"status": "resolved", "loop_terminated": True}
    return {"status": "ongoing", "loop_terminated": False}
```

Setting `tool_context.actions.escalate = True` immediately terminates the loop.

### 3. Progressive State Accumulation

Each iteration can access state from previous iterations:
- `{suggested_solution}` - Last solution tried
- `{solution_status}` - Result of last validation
- `{previous_attempts}` - History of what was tried

## Theme: SmartHome Progressive Troubleshooting

This sample implements an iterative troubleshooting system that:

1. **Suggests solutions** - Starting simple, progressing to complex
2. **Validates results** - Gets user feedback on each attempt
3. **Escalates when resolved** - Terminates loop on success
4. **Limits iterations** - Maximum 5 attempts before human escalation

## Quick Start

```bash
# Navigate to this sample
cd chapter-4/03_loop_agent

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run with ADK web interface
adk web .
```

## Sample Queries to Try

1. **"My thermostat won't connect to WiFi"**
   - Loop suggests progressively advanced solutions
   - Simulates user feedback until resolved or max iterations

2. **"The display on my thermostat is flickering"**
   - Known issue detection triggers
   - May resolve early via known issue workaround

3. **"Temperature readings are way off"**
   - Calibration suggestions
   - HVAC system checks

## Code Walkthrough

### Simulated Tools

The sample includes realistic troubleshooting tools:

```python
# Knowledge base lookup
def lookup_troubleshooting_steps(product_type: str, issue_category: str) -> dict:
    """Look up troubleshooting steps from the knowledge base."""
    # Returns ordered steps from simple to complex
    return {"steps": ["Step 1: Check power", "Step 2: Restart", ...]}

# Known issue matching
def check_known_issues(product_type: str, symptoms: str) -> dict:
    """Check for known issues matching the symptoms."""
    # Returns known bugs and their workarounds
    return {"known_issues_found": 1, "issues": [...]}

# User feedback simulation
def prompt_user_for_feedback(suggested_solution: str) -> dict:
    """Prompt the user to test the suggested solution."""
    # Simulates user testing and reporting results
    return {"user_feedback": {"result": "still_broken"}}
```

### The Escalation Tool (Example 4-8)

```python
def check_resolution(solution_status: str, tool_context) -> dict:
    """Check if issue is resolved and escalate to terminate loop if so."""
    resolved_keywords = ["resolved", "fixed", "working", "success"]
    is_resolved = any(kw in solution_status.lower() for kw in resolved_keywords)

    if is_resolved:
        # KEY: This terminates the loop immediately
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
```

### Complete Loop Structure

```python
# Agent 1: Suggests solutions (gets progressively advanced)
solution_agent = Agent(
    model="gemini-2.5-flash",
    name="SolutionAgent",
    instruction="""Based on {issue_description} and {previous_attempts},
    suggest the next troubleshooting step.
    Start simple, progress to complex.""",
    output_key="suggested_solution",
    tools=[lookup_troubleshooting_steps, check_known_issues]
)

# Agent 2: Validates if solution worked
validation_agent = Agent(
    model="gemini-2.5-flash",
    name="ValidationAgent",
    instruction="""Test {suggested_solution} and determine if issue is resolved.
    If resolved, call check_resolution to terminate the loop.""",
    output_key="solution_status",
    tools=[prompt_user_for_feedback, check_resolution]
)

# The loop itself
troubleshooting_loop = LoopAgent(
    name="TroubleshootingLoop",
    sub_agents=[solution_agent, validation_agent],
    max_iterations=5
)
```

## Loop Termination Conditions

The LoopAgent terminates when ANY of these occur:

| Condition | How It Works |
|-----------|--------------|
| **Max iterations reached** | `max_iterations=5` limits attempts |
| **Escalate action set** | `tool_context.actions.escalate = True` |
| **Agent explicitly exits** | Return indicates completion |

## When to Use LoopAgent

✅ **Good Use Cases:**
- Progressive troubleshooting with increasing complexity
- Iterative refinement (drafting, editing, improving)
- Retry logic with different strategies
- Polling until a condition is met

❌ **Avoid When:**
- Fixed number of steps (use SequentialAgent)
- Independent parallel tasks (use ParallelAgent)
- No clear termination condition exists

## Troubleshooting Levels

The sample implements 5 escalation levels:

| Level | Name | Description |
|-------|------|-------------|
| 1 | Basic | Simple restarts and checks |
| 2 | Intermediate | Settings and configuration |
| 3 | Advanced | System diagnostics and resets |
| 4 | Expert | Hardware checks and replacements |
| 5 | Escalation | Technician visit or replacement |

## Key Takeaways

1. **LoopAgent repeats until termination** - Natural fit for iterative tasks
2. **max_iterations is a safety net** - Prevents infinite loops
3. **escalate=True exits immediately** - Use in any tool to terminate
4. **State accumulates across iterations** - Each pass can see previous results
5. **Combine solution + validation** - Common pattern for iterative refinement

## Next Steps

- **04_mcp_agent**: Connect to external tools via MCP protocol
- **05_a2a_server**: Expose agents as services via A2A
- **07_hybrid_team**: Combine local, remote, and MCP in one workflow
