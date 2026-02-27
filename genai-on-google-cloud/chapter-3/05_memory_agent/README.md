# Memory Agent - Long-Term Memory with Vertex AI Memory Bank

**Concept**: Persistent semantic memory beyond simple state
**Estimated Time**: 15 minutes

## What You'll Learn

- Setting up Vertex AI Memory Bank
- Using `VertexAiMemoryBankService`
- `PreloadMemoryTool` for automatic memory retrieval
- Memory scopes and semantic search
- Fallback to state-based memory

## Prerequisites

- Python 3.10+
- ADK installed (`pip install google-adk`)
- Google Cloud project with Vertex AI enabled
- `gcloud` CLI configured

## Quick Start

### Option 1: Full Memory Bank (Recommended)

1. **Set up Google Cloud**:
   ```bash
   # Authenticate
   gcloud auth application-default login

   # Set your project
   export GOOGLE_CLOUD_PROJECT=your-project-id

   # Enable Vertex AI
   gcloud services enable aiplatform.googleapis.com
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set GOOGLE_CLOUD_PROJECT
   ```

3. **Run with ADK Web**:
   ```bash
   adk web .
   ```

### Option 2: Demo Mode (No GCP Required)

Without `GOOGLE_CLOUD_PROJECT` set, the agent runs in demo mode using
state-based memory (still persistent, but without semantic search).

```bash
# Just run without configuration
adk web .
```

## Try These Prompts

- "Remember that I love Italian food"
- "My dog's name is Luna and she's a golden retriever"
- "What food do I like?"
- "Add a note about my project: need to finish by Friday"
- "What notes do I have about my project?"
- "What do you remember about me?"

## Memory Bank vs State

| Feature | State (`user:`) | Memory Bank |
|---------|-----------------|-------------|
| Persistence | Session/User level | Long-term cloud |
| Search | Key-value lookup | Semantic search |
| Scale | Limited by session | Scalable storage |
| Context | Must know the key | Finds relevant memories |

### When Memory Bank Shines

```
User: "I'm planning a dinner party"

State-based: Needs exact key "user:preferences.food"
Memory Bank: Semantically recalls "loves Italian food", "allergic to nuts"
```

## Code Walkthrough

### Setting Up Memory Bank

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools import PreloadMemoryTool

# Initialize the service
memory_service = VertexAiMemoryBankService(
    project="your-project-id",
    location="us-central1"
)

# Create the preload tool (auto-retrieves relevant memories)
preload_memory = PreloadMemoryTool(memory_service=memory_service)
```

### Adding Memory Tools to Agent

```python
root_agent = Agent(
    name="MemoryAssistant",
    model="gemini-2.0-flash",
    instruction="...",
    tools=[
        save_preference,       # Custom tool
        get_preferences,       # Custom tool
        preload_memory         # Memory Bank tool
    ]
)
```

### Using Memory in a Runner

```python
from google.adk.runners import Runner

runner = Runner(
    agent=root_agent,
    app_name="memory_agent",
    session_service=session_service,
    memory_service=memory_service  # Enables Memory Bank
)
```

## Memory Scopes

Memory Bank organizes memories by scope:

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory Bank Scopes                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  User Memories  │  │ Session Facts   │                  │
│  │                 │  │                 │                  │
│  │ - Preferences   │  │ - Current topic │                  │
│  │ - Past interact │  │ - Recent queries│                  │
│  │ - Learned facts │  │ - Context       │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                             │
│  Semantic Search: "What does user like?" →                 │
│    Returns: [Italian food, Jazz music, Hiking]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Memory Agent                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Message: "What's my favorite food?"                   │
│                     │                                       │
│                     ▼                                       │
│         ┌─────────────────────┐                            │
│         │   PreloadMemory     │                            │
│         │   (Semantic Search) │                            │
│         └──────────┬──────────┘                            │
│                    │                                        │
│                    ▼                                        │
│    ┌───────────────────────────────┐                       │
│    │   Vertex AI Memory Bank       │                       │
│    │   (Cloud Storage)             │                       │
│    └───────────────┬───────────────┘                       │
│                    │                                        │
│                    ▼                                        │
│         ┌─────────────────────┐                            │
│         │ Retrieved Memories: │                            │
│         │ - User loves Italian│                            │
│         │ - Allergic to nuts  │                            │
│         └──────────┬──────────┘                            │
│                    │                                        │
│                    ▼                                        │
│    Agent Response: "Based on what I remember,              │
│    you love Italian food!"                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Fallback Behavior

This agent gracefully handles missing Memory Bank:

```python
if PROJECT_ID:
    try:
        memory_service = VertexAiMemoryBankService(...)
        memory_tools = [PreloadMemoryTool(memory_service=memory_service)]
    except Exception:
        print("Running in demo mode without persistent memory.")
else:
    print("GOOGLE_CLOUD_PROJECT not set. Running in demo mode.")
```

In demo mode:
- Preferences and notes still saved in `user:` state
- State persists across sessions in ADK web
- Just no semantic search capability

## What's Next?

Now that you understand memory:

- **[06_multimodal_agent](../06_multimodal_agent/)**: Agents that see images
- **[08_guardrails_agent](../08_guardrails_agent/)**: Securing agent behavior

## Related Resources

- [ADK Memory Bank](https://google.github.io/adk-docs/sessions/memory/)
- [Vertex AI Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)
- [PreloadMemoryTool](https://google.github.io/adk-docs/tools/built-in-tools/#memory-tools)
