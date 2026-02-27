# Hello Agent - From Zero to Agent in 7 Lines

**Concept**: The simplest possible ADK agent (Example 3-1)
**Estimated Time**: 5 minutes
**Theme**: SmartHome Customer Support

## What You'll Learn

- The minimal configuration for an ADK agent
- Understanding the `Agent` class parameters
- Running agents with `adk web` and `adk run`
- How ADK handles session management automatically

## Prerequisites

- Python 3.10+
- ADK installed (`pip install google-adk`)
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Quick Start

1. **Set up your API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

2. **Run with ADK Web** (recommended):
   ```bash
   adk web .
   ```

3. **Or run with ADK CLI** (Example 3-2):
   ```bash
   adk run .
   ```

4. **Open browser**: Navigate to http://localhost:8000

## Try These Prompts

- "Hello, I need help with my SmartHome doorbell"
- "How do I set up my smart thermostat?"
- "My smart light isn't connecting"
- "What SmartHome products do you support?"

## Code Walkthrough

The entire agent is defined in just 7 lines (Example 3-1):

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="You help customers with their SmartHome products."
)
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Unique identifier for the agent (used in logs and UI) |
| `model` | The Gemini model to use (e.g., `gemini-2.5-flash`) |
| `instruction` | The system prompt that defines the agent's personality and behavior |

### What ADK Handles Automatically

When you run this simple agent, ADK provides:

1. **Session Management**: Each conversation gets its own isolated session
2. **Conversation History**: Previous messages are automatically included in context
3. **State Persistence**: Session state survives across interactions
4. **Event Streaming**: Real-time token streaming for responsive UX
5. **Error Handling**: Graceful handling of API errors

## The `root_agent` Convention

ADK looks for a variable named `root_agent` in your `agent.py` file. This is the entry point for your agent application. You can use a factory function if you need more complex initialization:

```python
def create_root_agent():
    return Agent(
        name="CustomerSupportAgent",
        model="gemini-2.5-flash",
        instruction="You help customers with their SmartHome products."
    )

root_agent = create_root_agent()
```

## Key Concepts

### The Agent Class

The `Agent` class (also available as `LlmAgent`) is the foundation of all ADK agents. It encapsulates:

- **Identity**: Name and description
- **Reasoning**: The LLM model and instructions
- **Capabilities**: Tools and sub-agents (covered in later samples)
- **Behavior**: Callbacks and configuration

### Instructions Best Practices

Good instructions should:
- Define a clear persona/role
- Specify the agent's capabilities and limitations
- Set the tone and style of responses
- Provide guidance for edge cases

### Running Your Agent

ADK provides several ways to interact with your agent:

```bash
# Web UI with full debugging
adk web .

# Simple CLI interface
adk run .

# API server for integration
adk api_server .
```

## What's Next?

Now that you understand the basics, move on to:

- **[02_tool_agent](../02_tool_agent/)**: Add custom tools to extend capabilities
- **[03_multi_agent](../03_multi_agent/)**: Create specialist sub-agents

## Related Resources

- [ADK Quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [Agent Configuration](https://google.github.io/adk-docs/agents/llm-agents/)
- [Model Selection](https://google.github.io/adk-docs/agents/models/)
