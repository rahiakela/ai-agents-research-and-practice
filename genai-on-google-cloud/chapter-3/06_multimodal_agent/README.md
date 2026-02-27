# Multimodal Agent - Image Analysis and Accessibility

**Concept**: Working with images and multimodal inputs
**Estimated Time**: 10 minutes

## What You'll Learn

- How ADK agents handle image inputs
- Leveraging Gemini's vision capabilities
- Combining image understanding with tools
- Building practical multimodal workflows

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

### With Images (use the upload button in ADK web)
- Upload an image and ask: "Analyze this image for accessibility"
- "Generate alt text for this image"
- "Are there any color contrast issues?"
- "Check the text readability in this screenshot"

### Without Images
- "What makes good alt text?"
- "Explain WCAG color contrast requirements"
- "What are the four principles of accessibility?"
- "Show me my analysis history"

## How Multimodal Works in ADK

Gemini models are natively multimodal - they understand images alongside text.
ADK makes this seamless:

```
┌─────────────────────────────────────────────────────────────┐
│                    ADK Multimodal Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Input                                                │
│   ┌─────────────────────────────────────────────┐          │
│   │  📷 Image + 💬 "Analyze accessibility"       │          │
│   └────────────────────┬────────────────────────┘          │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────────────┐          │
│   │  Gemini 2.0 Flash (Vision + Language)       │          │
│   │  - Understands image content                │          │
│   │  - Processes text prompt                    │          │
│   │  - Decides which tools to call              │          │
│   └────────────────────┬────────────────────────┘          │
│                        │                                    │
│                        ▼                                    │
│   ┌─────────────────────────────────────────────┐          │
│   │  Tools receive image descriptions           │          │
│   │  - generate_alt_text()                      │          │
│   │  - check_color_contrast()                   │          │
│   │  - create_accessibility_report()            │          │
│   └────────────────────┬────────────────────────┘          │
│                        │                                    │
│                        ▼                                    │
│   📋 Comprehensive Accessibility Report                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Code Walkthrough

### Agent Setup

The agent uses the same `Agent` class - Gemini handles multimodal natively:

```python
root_agent = Agent(
    name="AccessibilityChecker",
    model="gemini-2.0-flash",  # Multimodal model
    instruction="You are an accessibility expert...",
    tools=[generate_alt_text, check_color_contrast, ...]
)
```

### Image Analysis Pattern

When the model sees an image, it can:
1. Describe what it sees
2. Extract relevant details (colors, text, layout)
3. Call tools with extracted information

```python
# The model extracts this from the image and calls our tool:
generate_alt_text(
    description="A woman typing on a laptop in a coffee shop",
    context="Hero image for remote work blog post"
)
```

### Combining Vision with Tools

Tools receive text descriptions extracted by the model:

```python
def check_color_contrast(
    foreground_description: str,  # "Light gray text"
    background_description: str,  # "White background"
    tool_context: ToolContext = None
) -> dict:
    # Analyze based on model's color descriptions
    ...
```

## Accessibility Tools

| Tool | Purpose | Input |
|------|---------|-------|
| `generate_alt_text` | Create screen reader text | Image description |
| `check_color_contrast` | Identify contrast issues | Color descriptions |
| `analyze_text_readability` | Check text accessibility | Text details |
| `create_accessibility_report` | Full WCAG report | All findings |
| `get_analysis_history` | Review past analyses | None |

## WCAG Quick Reference

The agent checks against WCAG 2.1 guidelines:

### The Four Principles (POUR)

1. **Perceivable** - Information must be presentable
2. **Operable** - Interface must be usable
3. **Understandable** - Content must be clear
4. **Robust** - Works with assistive tech

### Key Checks

- **Color Contrast**: 4.5:1 for normal text, 3:1 for large text
- **Alt Text**: All non-decorative images need text alternatives
- **Text Size**: Minimum 16px recommended for body text
- **Focus Indicators**: Interactive elements need visible focus

## Tips for Multimodal Agents

1. **Be specific in prompts**: "Analyze the button colors" > "Look at this"
2. **Combine with context**: "This is for a banking app" helps the agent
3. **Iterate**: Ask follow-up questions about specific elements
4. **Use tools**: The agent combines vision with tools for detailed analysis

## What's Next?

Now that you understand multimodal:

- **[07_streaming_agent](../07_streaming_agent/)**: Real-time streaming responses
- **[08_guardrails_agent](../08_guardrails_agent/)**: Validating inputs and outputs

## Related Resources

- [Gemini Vision Capabilities](https://ai.google.dev/gemini-api/docs/vision)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ADK Input Types](https://google.github.io/adk-docs/agents/)
