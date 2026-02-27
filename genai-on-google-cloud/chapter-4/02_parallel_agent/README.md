# Parallel Agent Sample - The Independent Taskforce Pattern

This sample demonstrates **ParallelAgent** for concurrent execution of independent tasks.
Based on Chapter 4, Example 4-6: Concurrent Information Gathering.

## Overview

The ParallelAgent pattern is perfect when you have multiple independent tasks that can
run simultaneously. This dramatically improves response time for operations that don't
depend on each other.

```
                    ┌─────────────────────┐
                    │   Customer Query    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  ParallelAgent      │
                    │  (InformationGathering)
                    └──────────┬──────────┘
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │ PurchaseHistory│   │ ManualLookup  │   │ UsageAnalysis │
   │     Agent     │   │     Agent     │   │     Agent     │
   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
           │                   │                   │
           │ output_key:       │ output_key:       │ output_key:
           │ purchase_data     │ manual_content    │ usage_data
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   SynthesisAgent    │
                    │ Uses: {purchase_data}│
                    │ {manual_content}     │
                    │ {usage_data}         │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Unified Response   │
                    └─────────────────────┘
```

## Key Concepts

### 1. ParallelAgent for Concurrent Execution

```python
from google.adk.agents import ParallelAgent

info_gathering_taskforce = ParallelAgent(
    name="InformationGathering",
    sub_agents=[purchase_history_agent, manual_lookup_agent, usage_analysis_agent]
)
```

All three agents run **concurrently**, not sequentially. This means if each agent
takes 1 second, total time is ~1 second instead of 3 seconds.

### 2. Output Keys for Race-Free State

Each agent writes to a **distinct output_key** to avoid race conditions:

```python
purchase_history_agent = Agent(..., output_key="purchase_data")
manual_lookup_agent = Agent(..., output_key="manual_content")
usage_analysis_agent = Agent(..., output_key="usage_data")
```

### 3. Combining ParallelAgent with SequentialAgent

The complete workflow uses SequentialAgent to first gather data in parallel,
then synthesize:

```python
support_workflow = SequentialAgent(
    name="ComprehensiveSupport",
    sub_agents=[info_gathering_taskforce, synthesis_agent]  # First parallel, then synthesis
)
```

## Theme: SmartHome Customer Support

This sample implements a comprehensive device support system that:

1. **Fetches purchase history** - Customer's order data and loyalty tier
2. **Retrieves documentation** - Product manuals and troubleshooting guides
3. **Analyzes usage** - Device telemetry and energy metrics
4. **Synthesizes response** - Combines all data into personalized support

## Quick Start

```bash
# Navigate to this sample
cd chapter-4/02_parallel_agent

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run with ADK web interface
adk web .
```

## Sample Queries to Try

1. **"I need help with my Smart Thermostat Pro"**
   - Triggers all three agents to gather purchase history, manual, and usage data
   - Synthesis agent combines into comprehensive response

2. **"What's my device's energy efficiency?"**
   - Usage analysis agent provides energy metrics
   - Purchase history confirms device ownership
   - Synthesis recommends optimizations

3. **"Show me my purchase history and troubleshooting tips"**
   - Parallel gathering of order data and documentation
   - Personalized based on loyalty tier

## Code Walkthrough

### Simulated Tools

Each agent has specialized tools:

```python
# Purchase history tools
def query_order_database(customer_id: str) -> dict:
    """Query the order database for customer purchase history."""
    return {
        "customer_id": customer_id or "CUST-12345",
        "orders": [...],
        "loyalty_tier": "Gold"
    }

# Documentation tools
def fetch_product_manual(product_name: str) -> dict:
    """Fetch the product manual for a specific product."""
    return {"product": product_name, "manual_sections": [...]}

# Usage analysis tools
def calculate_energy_metrics(device_id: str) -> dict:
    """Calculate energy usage metrics for a device."""
    return {"monthly_energy_kwh": 145.3, "efficiency_rating": "A"}
```

### Complete Workflow

```python
# 1. Define specialist agents with output_keys
purchase_history_agent = Agent(
    model="gemini-2.5-flash",
    name="PurchaseHistoryAgent",
    instruction="Fetch and summarize the customer's purchase history.",
    output_key="purchase_data",  # Stores result for later use
    tools=[query_order_database]
)

# 2. Create parallel taskforce
info_gathering_taskforce = ParallelAgent(
    name="InformationGathering",
    sub_agents=[purchase_history_agent, manual_lookup_agent, usage_analysis_agent]
)

# 3. Synthesis agent uses all gathered data
synthesis_agent = Agent(
    model="gemini-2.5-flash",
    name="SynthesisAgent",
    instruction="""Combine information from {purchase_data}, {manual_content},
    and {usage_data} to provide comprehensive support."""
)

# 4. Complete workflow
support_workflow = SequentialAgent(
    name="ComprehensiveSupport",
    sub_agents=[info_gathering_taskforce, synthesis_agent]
)
```

## Performance Benefits

| Approach | Time (3 agents @ 1s each) |
|----------|---------------------------|
| Sequential | ~3 seconds |
| **Parallel** | **~1 second** |

The ParallelAgent pattern provides significant speedup for independent operations.

## When to Use ParallelAgent

✅ **Good Use Cases:**
- Gathering data from multiple independent sources
- Running parallel validations
- Fetching information that doesn't depend on other results

❌ **Avoid When:**
- Operations depend on each other's results
- You need guaranteed execution order
- Results from one agent affect another's behavior

## Key Takeaways

1. **ParallelAgent runs sub-agents concurrently** - major performance benefit
2. **Use distinct output_keys** - prevents race conditions in state
3. **Combine with SequentialAgent** - gather-then-synthesize pattern
4. **State placeholders** - `{variable}` syntax accesses previous results

## Next Steps

- **03_loop_agent**: Learn iterative refinement with LoopAgent
- **04_mcp_agent**: Connect to external tools via MCP
- **07_hybrid_team**: Combine local, remote, and MCP in one workflow
