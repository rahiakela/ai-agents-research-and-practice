# MCP Agent Sample - The Language of Tools

This sample demonstrates **MCPToolset** for connecting to external tool servers
via the Model Context Protocol (MCP).
Based on Chapter 4, Example 4-9: MCP Tool Integration.

## Overview

MCP (Model Context Protocol) is an open standard for connecting AI models to
external tools and data sources. ADK's `MCPToolset` allows you to seamlessly
integrate any MCP-compatible server into your agents.

```
┌─────────────────────────────────────────────────────────────┐
│                      ADK Agent                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                MCPSupportAgent                       │   │
│  │                                                      │   │
│  │  Tools:                                              │   │
│  │  ├── MCPToolset (customer_db_tools)                 │   │
│  │  │   ├── lookup_customer_by_email                   │   │
│  │  │   ├── get_order_history                          │   │
│  │  │   ├── get_registered_devices                     │   │
│  │  │   └── search_customers                           │   │
│  │  ├── check_warranty_status (local)                  │   │
│  │  └── create_support_ticket (local)                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           │ MCP Protocol                    │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MCP Server (mcp_server.py)             │   │
│  │                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │   │
│  │  │  Customers   │  │   Orders     │  │ Devices  │  │   │
│  │  │   Database   │  │   Database   │  │ Database │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. McpToolset for Tool Integration (Example 4-9)

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Connect to MCP server via SSE (Server-Sent Events)
customer_db_tools = McpToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse"
    )
)
```

### 2. Using MCP Tools in an Agent

```python
support_agent = Agent(
    model="gemini-2.5-flash",
    name="MCPSupportAgent",
    instruction="You help customers using the database...",
    tools=[
        customer_db_tools,       # MCP tools (automatically discovered)
        check_warranty_status,   # Local tools
        create_support_ticket
    ]
)
```

### 3. Connection Types

| Type | Use Case | Example |
|------|----------|---------|
| `SseConnectionParams` | HTTP-based servers | Remote APIs, cloud services |
| `StdioConnectionParams` | Local processes | CLI tools, local scripts |

## Theme: Database-Connected Support Agent

This sample implements a support agent that combines:

1. **MCP Database Tools** - Customer lookup, order history, device info
2. **Local Tools** - Warranty checking, ticket creation
3. **Seamless Integration** - Agent uses both transparently

## Quick Start

### Step 1: Start the MCP Server

```bash
cd chapter-4/04_mcp_agent

# Install dependencies if needed
pip install mcp starlette uvicorn

# Start the MCP server
python mcp_server.py
```

You should see:
```
============================================================
MCP Customer Database Server
============================================================

Starting server on http://localhost:8080

Available tools:
  - lookup_customer_by_email: Find customer by email
  - get_order_history: Get customer's order history
  - get_registered_devices: Get customer's devices
  - search_customers: Search customers by name

Sample customers in database:
  - John Doe (john@example.com)
  - Jane Smith (jane@example.com)
  - Bob Johnson (bob@example.com)
```

### Step 2: Run the Agent

In a new terminal:

```bash
cd chapter-4/04_mcp_agent

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run with ADK web interface
adk web .
```

## Sample Queries to Try

1. **"Look up customer john@example.com"**
   - Uses MCP tool: `lookup_customer_by_email`
   - Returns customer profile with loyalty tier

2. **"What has Jane Smith ordered?"**
   - First searches by name, then gets order history
   - Uses: `search_customers` → `get_order_history`

3. **"Check if John's thermostat is still under warranty"**
   - Combines MCP (order lookup) with local tool (warranty check)
   - Uses: `lookup_customer_by_email` → `get_order_history` → `check_warranty_status`

4. **"Create a support ticket for Jane's camera issue"**
   - Local tool creates ticket
   - Uses: `create_support_ticket`

## Code Walkthrough

### MCP Server (mcp_server.py)

The sample includes a self-contained MCP server:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

mcp_server = Server("customer-database-server")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="lookup_customer_by_email",
            description="Look up customer by email...",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Customer email"}
                },
                "required": ["email"]
            }
        ),
        # ... more tools
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "lookup_customer_by_email":
        email = arguments.get("email")
        customer = CUSTOMERS_DB.get(email)
        return [TextContent(type="text", text=json.dumps(customer))]
```

### Agent Integration (agent.py)

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Connect to MCP server
customer_db_tools = McpToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse"
    )
)

# Agent uses MCP tools alongside local tools
support_agent = Agent(
    model="gemini-2.5-flash",
    name="MCPSupportAgent",
    instruction="...",
    tools=[
        customer_db_tools,       # All tools from MCP server
        check_warranty_status,   # Local tool
        create_support_ticket    # Local tool
    ]
)
```

## MCP Connection Options

### SSE (Server-Sent Events) - For HTTP Servers

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

McpToolset(
    connection_params=SseConnectionParams(
        url="http://localhost:8080/sse",
        headers={"Authorization": "Bearer token"}  # Optional
    )
)
```

### Stdio - For Local Processes

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["my_mcp_server.py"]
        )
    )
)
```

## Sample Database Contents

### Customers

| Email | Name | Loyalty Tier |
|-------|------|--------------|
| john@example.com | John Doe | Gold |
| jane@example.com | Jane Smith | Platinum |
| bob@example.com | Bob Johnson | Silver |

### Orders

| Customer | Products |
|----------|----------|
| John Doe | Smart Thermostat Pro, Smart Light Bulbs |
| Jane Smith | Security Cameras (3), Smart Doorbell Pro |
| Bob Johnson | Smart Plug (2-pack) |

## When to Use McpToolset

✅ **Good Use Cases:**
- Connecting to existing MCP-compatible services
- Integrating databases, APIs, or external systems
- Reusing tools across multiple agents
- Accessing third-party MCP tool providers

❌ **Consider Alternatives When:**
- Simple functions (use regular Python functions)
- Tools only used by one agent (overhead not worth it)
- Real-time/streaming requirements (MCP is request-response)

## Key Takeaways

1. **MCP is a standard protocol** - Works with any MCP-compatible server
2. **MCPToolset wraps MCP servers** - Exposes tools to ADK agents
3. **Automatic tool discovery** - Tools are listed from the server
4. **Mix MCP and local tools** - Combine as needed in one agent
5. **SSE for HTTP, Stdio for local** - Choose connection type appropriately

## Dependencies

```
google-adk>=1.0.0
mcp>=1.0.0
starlette>=0.32.0
uvicorn>=0.23.0
```

## Next Steps

- **05_a2a_server**: Expose your agents as services via A2A
- **06_a2a_client**: Consume remote agents in your workflows
- **07_hybrid_team**: Combine MCP, A2A, and local agents
