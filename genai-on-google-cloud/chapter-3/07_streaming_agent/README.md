# Streaming Agent - Real-Time Response Generation

**Concept**: Token-by-token streaming with Gemini Live API
**Estimated Time**: 10 minutes

## What You'll Learn

- How streaming works in ADK
- Using `run_async()` for streaming responses
- Event iteration patterns
- When to use streaming vs batch responses

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

2. **Run with ADK Web** (auto-streaming):
   ```bash
   adk web .
   ```

3. **Or run the streaming demo directly**:
   ```bash
   python agent.py
   ```

4. **Open browser**: Navigate to http://localhost:8000

## Try These Prompts

- "Tell me a fantasy story about a dragon"
- "Start a mystery story set in a library"
- "Add a plot twist!"
- "Make the mood more tense"
- "Continue the story with more action"
- "How many stories have we created?"

## Why Streaming Matters

```
Traditional (Batch)                 Streaming
─────────────────                   ─────────
User: Tell a story                  User: Tell a story

[Waiting... 5 seconds]              Once upon a time...
                                    [tokens arriving]
                                    in a land far away...
                                    [more tokens]
                                    there lived a...
                                    [continues flowing]

Response: Once upon a time,         [Complete - same content
in a land far away...               but user saw it build!]
```

Benefits:
- **Faster perceived response** - Users see content immediately
- **Better UX for long content** - Stories, explanations, code
- **Interruptible** - Users can stop generation if off-track
- **Engagement** - Watching text appear is more engaging

## Streaming Modes in ADK

ADK supports multiple streaming approaches:

| Mode | Use Case | How It Works |
|------|----------|--------------|
| **ADK Web** | Interactive chat | Automatic SSE streaming |
| **run_async()** | Programmatic | Async iterator over events |
| **Live API** | Real-time audio/video | Bidirectional WebSocket |

## Code Walkthrough

### Standard Agent (ADK Web Streaming)

The agent works normally - ADK web handles streaming automatically:

```python
root_agent = Agent(
    name="StoryWeaver",
    model="gemini-2.0-flash",
    instruction="...",
    tools=[get_story_prompt, add_plot_twist, ...]
)
```

When you run `adk web`, responses stream to the browser via SSE.

### Programmatic Streaming with run_async()

For custom applications, use `run_async()`:

```python
async for event in runner.run_async(
    user_id="demo_user",
    session_id=session.id,
    new_message="Tell me a story"
):
    # Each event contains partial content
    if hasattr(event, 'content') and event.content:
        for part in event.content.parts:
            if hasattr(part, 'text'):
                print(part.text, end='', flush=True)
```

### Event Types

Streaming yields different event types:

```python
async for event in runner.run_async(...):
    match event:
        case TextEvent():
            # Partial text content
            print(event.text, end='')

        case ToolCallEvent():
            # Agent is calling a tool
            print(f"Calling {event.tool_name}...")

        case ToolResultEvent():
            # Tool returned a result
            print(f"Tool result: {event.result}")

        case EndEvent():
            # Response complete
            print("Done!")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streaming Flow                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Input: "Tell me a story about space"                │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────────────┐          │
│   │            Gemini 2.0 Flash                 │          │
│   │         (generates tokens)                  │          │
│   └────────────────────┬────────────────────────┘          │
│                        │                                    │
│        ┌───────────────┼───────────────┐                   │
│        ▼               ▼               ▼                    │
│   [Token 1]       [Token 2]       [Token 3]  ...           │
│   "The"           "stars"          "twinkled"               │
│        │               │               │                    │
│        └───────────────┼───────────────┘                   │
│                        ▼                                    │
│   ┌─────────────────────────────────────────────┐          │
│   │         SSE / Async Iterator                │          │
│   │    (delivers tokens as they're generated)   │          │
│   └────────────────────┬────────────────────────┘          │
│                        │                                    │
│                        ▼                                    │
│   User sees: "The stars twinkled..." (building up)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Storytelling Tools

This agent includes tools for interactive storytelling:

| Tool | Purpose |
|------|---------|
| `get_story_prompt` | Generate a creative story opener |
| `add_plot_twist` | Insert dramatic plot twists |
| `set_story_mood` | Adjust tone (tense, humorous, etc.) |
| `get_story_stats` | Check generation statistics |

## Running the Streaming Demo

The `agent.py` file includes a runnable streaming example:

```bash
python agent.py
```

This demonstrates:
1. Creating a session programmatically
2. Sending a message
3. Iterating over streaming events
4. Printing tokens as they arrive

## Best Practices for Streaming

1. **Use streaming for long content**: Stories, explanations, code
2. **Handle interruptions**: Users may stop mid-stream
3. **Show typing indicators**: While waiting for first token
4. **Buffer appropriately**: Don't update UI on every character
5. **Consider mobile**: Streaming can be choppy on slow connections

## When NOT to Use Streaming

- Short, quick responses (weather, time)
- Responses requiring full context (summaries)
- Background processing (user not watching)
- Limited bandwidth scenarios

## What's Next?

Now that you understand streaming:

- **[08_guardrails_agent](../08_guardrails_agent/)**: Add safety callbacks
- Explore the [Live API](https://ai.google.dev/gemini-api/docs/live) for audio/video

## Related Resources

- [ADK Streaming](https://google.github.io/adk-docs/streaming/)
- [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
