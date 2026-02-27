# Tool Agent - Adding Intelligence Through Tools

**Concept**: Extending agent capabilities with custom function tools (Example 3-3)
**Estimated Time**: 10 minutes
**Theme**: SmartHome Customer Support

## What You'll Learn

- Creating custom function tools for your agent
- Writing effective tool docstrings (ADK uses these!)
- Type hints for parameter validation
- Observing tool execution in ADK web UI
- When and how agents decide to use tools

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
- "Check the warranty for product SH-DOORBELL-001"
- "Tell me about your smart thermostat"
- "I need to track my order ORD-12346"
- "Is my smart lock SH-LOCK-003 still under warranty?"

## Code Walkthrough

### Defining a Tool Function (Example 3-3)

Tools are regular Python functions with:
1. **Type hints** - For parameter validation
2. **Docstrings** - ADK uses these to describe the tool to the LLM

```python
def look_up_order(order_id: str) -> dict:
    """Retrieves order information from our database.

    Args:
        order_id: The customer's order number

    Returns:
        Order details including status, items, and tracking info
    """
    # Your implementation here
    return {
        "order_id": order_id,
        "status": "shipped",
        "tracking_number": "1Z999AA10123456784"
    }
```

### Adding Tools to an Agent

Simply pass functions to the `tools` parameter:

```python
root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="You help customers with their SmartHome products.",
    tools=[look_up_order, check_warranty_status, get_product_info]
)
```

## Observing Tool Execution

When you run `adk web`, you can see tool execution in real-time:

1. **Chat Panel**: Shows the conversation
2. **Events Panel**: Shows the sequence of events including tool calls
3. **Tool Calls**: Indicated with input/output details

### Event Flow

```
1. User message received
2. Agent reasoning (decides to use tool)
3. Tool call: look_up_order(order_id="ORD-12345")
4. Tool response: {status: "shipped", tracking_number: "1Z999..."}
5. Agent generates response using tool data
```

## Key Concepts

### How ADK Converts Functions to Tools

ADK automatically:
1. **Extracts the function signature** from type hints
2. **Generates a description** from the docstring
3. **Validates parameters** before calling the function
4. **Handles errors** gracefully

### Docstring Best Practices

The docstring is critical - it's what the LLM sees:

```python
def my_tool(param1: str, param2: int = 10) -> dict:
    """Brief description of what the tool does.

    Args:
        param1: Clear description of this parameter
        param2: Description with default value noted

    Returns:
        Description of the return value structure
    """
```

### Return Type Guidelines

- Return **dictionaries** for structured data
- Include all relevant information
- Add timestamps for time-sensitive data
- Keep keys descriptive and consistent

## Tools in This Sample

| Tool | Purpose | Parameters |
|------|---------|------------|
| `look_up_order` | Get order status and tracking | `order_id: str` |
| `check_warranty_status` | Check product warranty | `product_id: str` |
| `get_product_info` | Get product details | `product_name: str` |

## What's Next?

Now that you understand tools, explore:

- **[03_multi_agent](../03_multi_agent/)**: When to use sub-agents instead of tools
- **[04_stateful_agent](../04_stateful_agent/)**: Tools that modify state

## Related Resources

- [ADK Function Tools](https://google.github.io/adk-docs/tools/function-tools/)
- [Built-in Tools](https://google.github.io/adk-docs/tools/built-in-tools/)
- [Tool Context](https://google.github.io/adk-docs/tools/function-tools/#tool-context)
