# Production Agent Sample - Enterprise-Ready Patterns

This sample demonstrates production concerns for enterprise agent systems:
- **Security schemes** in Agent Cards (Example 4-15)
- **A2A extensions** for custom capabilities (Examples 4-16, 4-17)
- **Distributed tracing** for observability (Examples 4-18, 4-19, 4-20)
- **Agent versioning** for compatibility (Examples 4-21, 4-22)

Based on Chapter 4, Examples 4-15 to 4-22: Production Realities.

## Overview

Moving agents to production requires addressing security, observability, and
evolution concerns. This sample demonstrates patterns for enterprise deployment.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Production Agent Architecture                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Security Layer                               │   │
│  │  • OAuth2 with scopes (billing:read, billing:refund)                │   │
│  │  • API Key authentication                                            │   │
│  │  • Extension activation via headers                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         BillingAgent v2.0                            │   │
│  │                                                                      │   │
│  │  Capabilities:              Extensions:                              │   │
│  │  • query_billing            • audit-logging/v1 (required)           │   │
│  │  • process_refund           • pii-masking/v1 (optional)             │   │
│  │  • process_partial_refund                                            │   │
│  │  • resolve_dispute                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Observability Layer                             │   │
│  │  • Distributed tracing (W3C Trace Context)                          │   │
│  │  • Correlated logs with trace IDs                                   │   │
│  │  • Audit trails for financial operations                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Security Schemes in Agent Card (Example 4-15)

```json
{
  "name": "BillingAgent",
  "url": "https://billing-service.company.com",
  "securitySchemes": {
    "oauth": {
      "type": "oauth2",
      "flows": {
        "clientCredentials": {
          "tokenUrl": "https://auth.company.com/oauth/token",
          "scopes": {
            "billing:read": "Read billing information",
            "billing:refund": "Process refunds and credits"
          }
        }
      }
    }
  },
  "security": [{ "oauth": ["billing:read", "billing:refund"] }]
}
```

### 2. Extensions Configuration (Example 4-16)

```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "https://company.com/ext/audit-logging/v1",
        "description": "Detailed audit trails for financial transactions",
        "required": true
      },
      {
        "uri": "https://company.com/ext/pii-masking/v1",
        "description": "Masks PII in logs",
        "required": false
      }
    ]
  }
}
```

### 3. Extension Activation via Headers (Example 4-17)

```http
POST /agents/billing HTTP/1.1
Host: billing-service.company.com
X-A2A-Extensions: https://company.com/ext/audit-logging/v1

{"message": "Process refund for INV-2024-001"}
```

### 4. Distributed Tracing (Examples 4-18, 4-19, 4-20)

**Problem: Fragmented Logs (Example 4-18)**
```
2025-01-13 10:15:32 [INFO] coordinator - Received customer request
2025-01-13 10:15:33 [INFO] technical - Running diagnostics
2025-01-13 10:15:34 [INFO] billing - Processing refund
# Which request do these belong to?
```

**Solution: Trace Spans (Example 4-19)**
```
TRACE: 4bf92f3577b34da6a3ce929d0e0e4736
├─ Span: CustomerServiceCoordinator.process_request (2.1s)
│  ├─ Span: TechnicalAgent.diagnose (0.8s)
│  │  └─ Span: LLM.call (0.6s)
│  └─ Span: BillingAgent.analyze (1.2s) [Remote via A2A]
│     ├─ Span: query_billing_history (0.4s)
│     └─ Span: LLM.call (0.7s)
```

**Correlated Logs (Example 4-20)**
```python
def log_with_trace(level: str, message: str, **kwargs):
    trace = get_trace_context()
    logger.info(f"[trace:{trace['trace_id'][:8]}] {message} | context={kwargs}")
```

### 5. Agent Versioning (Examples 4-21, 4-22)

**Version Declaration (Example 4-21)**
```json
{
  "name": "BillingAgent",
  "version": "2.0.0",
  "description": "Handles billing, refunds, partial refunds, and disputes"
}
```

**Referencing Versioned Agents (Example 4-22)**
```python
# v1 client
billing_v1 = RemoteA2aAgent(
    agent_card="https://billing-service.company.com/v1/.well-known/agent-card.json"
)

# v2 client
billing_v2 = RemoteA2aAgent(
    agent_card="https://billing-service.company.com/v2/.well-known/agent-card.json"
)
```

## Quick Start

```bash
cd chapter-4/08_production_agent

# Set up environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run with ADK web interface
adk web .

# Or start as A2A server
uvicorn agent:a2a_app --host 0.0.0.0 --port 8001
```

## Sample Queries to Try

1. **"Show billing history for customer CUST-001 including disputes"**
   - Demonstrates audit logging with trace context

2. **"Process a 50% partial refund for INV-2024-003"**
   - Uses v2 partial refund capability

3. **"Resolve dispute DSP-2024-001 with a $25 credit"**
   - Uses v2 dispute resolution capability

## Agent Card Files

This sample includes two Agent Card examples:

### agent_card_v1.json (Basic)

```json
{
  "name": "BillingAgent",
  "version": "1.0.0",
  "skills": [
    {"name": "query_billing"},
    {"name": "process_refund"}
  ]
}
```

### agent_card_v2.json (Enterprise)

```json
{
  "name": "BillingAgent",
  "version": "2.0.0",
  "skills": [
    {"name": "query_billing"},
    {"name": "process_refund"},
    {"name": "process_partial_refund"},  // NEW
    {"name": "resolve_dispute"}           // NEW
  ],
  "securitySchemes": { ... },
  "extensions": [ ... ]
}
```

## Code Walkthrough

### Logging with Trace Context

```python
def log_with_trace(level: str, message: str, **kwargs):
    """Log with trace context for distributed tracing."""
    trace = get_trace_context()
    log_entry = {
        "message": message,
        "trace_id": trace["trace_id"],
        "span_id": trace["span_id"],
        **kwargs
    }
    logger.info(f"[trace:{trace['trace_id'][:8]}] {message} | context={kwargs}")
```

### Tool with Audit Trail

```python
def process_refund(invoice_id: str, reason: str, approved_by: Optional[str] = None) -> dict:
    """Process a full refund with audit trail."""
    log_with_trace("info", "Processing refund", invoice_id=invoice_id, reason=reason)

    result = {
        "refund_id": refund_id,
        "audit_trail": {
            "action": "refund_processed",
            "actor": "BillingAgent",
            "approved_by": approved_by,
            "timestamp": datetime.now().isoformat()
        }
    }

    log_with_trace("info", "Refund processed", refund_id=refund_id)
    return result
```

### Extension Check

```python
def check_extension_activated(extension_uri: str, headers: dict) -> bool:
    """Check if an extension is activated via headers."""
    activated = headers.get("X-A2A-Extensions", "").split(",")
    return extension_uri.strip() in [ext.strip() for ext in activated]
```

## Production Patterns Summary

| Pattern | Example | Purpose |
|---------|---------|---------|
| **Security Schemes** | 4-15 | Define auth requirements in Agent Card |
| **Extensions** | 4-16 | Declare optional capabilities |
| **Extension Activation** | 4-17 | Client activates via headers |
| **Fragmented Logs** | 4-18 | Problem: Uncorrelated log entries |
| **Trace Spans** | 4-19 | Solution: Hierarchical trace view |
| **Correlated Logs** | 4-20 | Include trace_id in all logs |
| **Version Declaration** | 4-21 | Semantic versioning in Agent Card |
| **Versioned References** | 4-22 | Clients specify version in URL |

## Security Best Practices

1. **Use OAuth2 for production** - Scoped access control
2. **Require audit logging extension** - Compliance requirements
3. **Mask PII in logs** - Privacy protection
4. **Version your Agent Cards** - Breaking change management

## Observability Best Practices

1. **Propagate trace context** - W3C Trace Context headers
2. **Log with trace IDs** - Every log includes trace_id
3. **Create spans for operations** - Tool calls, LLM calls
4. **Export to Cloud Trace** - Centralized trace analysis

## Versioning Best Practices

1. **Use semantic versioning** - major.minor.patch
2. **Version in URL path** - /v1/, /v2/
3. **Maintain backward compatibility** - v1 keeps working
4. **Document breaking changes** - New capabilities in v2

## Key Takeaways

1. **Security in Agent Cards** - Define auth before deployment
2. **Extensions add flexibility** - Optional capabilities per-request
3. **Tracing is essential** - Distributed systems need correlation
4. **Version from day one** - Evolution is inevitable
5. **Audit everything** - Financial operations need trails

## Dependencies

```
google-adk>=1.0.0
uvicorn>=0.23.0
```

## Next Steps

You've completed all Chapter 4 samples! You now understand:

- **01-03**: Local orchestration patterns (Sequential, Parallel, Loop)
- **04**: MCP for external tool integration
- **05-06**: A2A for agent-to-agent communication
- **07**: Hybrid architecture combining all approaches
- **08**: Production patterns for enterprise deployment

Continue to Chapter 5 for evaluation and optimization techniques.
