# Stateful Agent - State Management with Three Scopes

**Concept**: Managing state across different scopes using ToolContext (Examples 3-8, 3-10)
**Estimated Time**: 10 minutes
**Theme**: SmartHome Customer Support

## What You'll Learn

- The three state scopes: `temp:`, `user:`, `app:`
- Using `ToolContext` to access and modify state
- When to use each scope
- State persistence across sessions
- Policy-based cart expiry with `app:saved_cart_expiry_days`

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

- "Show me your security products"
- "Add the smart doorbell to my cart"
- "What's in my cart?"
- "Save my cart for later"
- "Is my saved cart still valid?"
- "Restore my saved cart"
- "I want to checkout"

## State Scopes Explained

| Scope | Prefix | Persistence | Use Case |
|-------|--------|-------------|----------|
| **Temp** | `temp:` | Current session only | Browse counts, last action |
| **User** | `user:` | Across sessions (same user) | Shopping cart, order history |
| **App** | `app:` | Across all users | Store statistics, inventory |

### Scope Examples in This Agent (Example 3-8)

```python
# TEMP - Lost when session ends
tool_context.state["temp:browse_count"] = count
tool_context.state["temp:last_action"] = "Added to cart"
tool_context.state["temp:validation_status"] = "success"

# USER - Persists for this user across sessions
tool_context.state["user:cart"] = {"items": [], "total": 0.0}
tool_context.state["user:cart_saved"] = True
tool_context.state["user:cart_saved_date"] = cart["saved_at"]

# APP - Shared across all users (policy settings)
tool_context.state["app:saved_cart_expiry_days"] = 30  # Example 3-10
```

## Code Walkthrough

### Accessing State with ToolContext

Tools receive state access through the `tool_context` parameter:

```python
def add_to_cart(product_id: str, tool_context: ToolContext = None) -> dict:
    # Read from user state (with default)
    cart = tool_context.state.get("user:cart", {"items": {}, "total": 0.0})

    # Modify the cart...
    cart["items"][product_id] = {"name": "...", "price": 99.99}

    # Write back to user state
    tool_context.state["user:cart"] = cart

    # Track in temp state (session only)
    tool_context.state["temp:last_action"] = "Added item"
```

### When to Use Each Scope

**Use `temp:` for:**
- Session counters
- Recent activity tracking
- Temporary preferences
- Anything that should reset each visit

**Use `user:` for:**
- Shopping carts
- User preferences
- Order history
- Saved items / wishlists

**Use `app:` for:**
- Global statistics
- Shared configuration
- Inventory counts
- System-wide settings

## State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      State Scopes                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   temp:     │  │   user:     │  │    app:     │         │
│  │             │  │             │  │             │         │
│  │ browse_cnt  │  │   cart      │  │ total_orders│         │
│  │ last_action │  │ order_count │  │ total_revenue│        │
│  │             │  │ last_order  │  │ items_added │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│        │                │                │                  │
│        ▼                ▼                ▼                  │
│   Session End      User Returns     All Users              │
│   = CLEARED        = PERSISTS       = SHARED               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Testing State Persistence

1. **Test temp state**:
   - Browse products several times
   - Ask "How many times have I browsed?"
   - Close the session, reopen
   - Browse count resets to 0

2. **Test user state**:
   - Add items to cart
   - Close the session, reopen (same user ID in ADK web)
   - Ask "What's in my cart?"
   - Cart items persist!

3. **Test app state**:
   - Complete a checkout
   - Ask "What are the store statistics?"
   - Open another session (different user)
   - Ask for store stats - same numbers!

## Key Concepts

### The ToolContext Object

ADK automatically injects `ToolContext` when your function signature includes it:

```python
# ADK detects tool_context parameter and provides it
def my_tool(param1: str, tool_context: ToolContext = None) -> dict:
    # Access state through tool_context.state
    value = tool_context.state.get("user:key", default_value)
    tool_context.state["user:key"] = new_value
```

### State Key Naming

Always use the prefix to specify scope:

```python
tool_context.state["temp:my_key"]   # ✓ Correct
tool_context.state["user:my_key"]   # ✓ Correct
tool_context.state["app:my_key"]    # ✓ Correct
tool_context.state["my_key"]        # ✗ Ambiguous - avoid!
```

## What's Next?

Now that you understand state management:

- **[05_memory_agent](../05_memory_agent/)**: Long-term memory with Memory Bank
- **[08_guardrails_agent](../08_guardrails_agent/)**: Validating state in callbacks

## Related Resources

- [ADK State Management](https://google.github.io/adk-docs/sessions/state/)
- [ToolContext Reference](https://google.github.io/adk-docs/tools/function-tools/#tool-context)
- [Session Management](https://google.github.io/adk-docs/sessions/)
