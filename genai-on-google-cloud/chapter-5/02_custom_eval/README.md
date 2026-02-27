# 02_custom_eval: Custom Evaluation Metrics

This sample demonstrates how to create custom evaluation metrics for specialized quality criteria that built-in metrics don't capture.

**Chapter References**:
- Example 5-3: Custom LLM-as-Judge Metric
- Example 5-4: Custom Computation-Based Metric

## What This Sample Demonstrates

- **LLM-as-Judge Metrics**: Use an LLM to evaluate qualitative aspects like helpfulness
- **Computation-Based Metrics**: Use code to validate business rules and compliance
- **Combined Evaluation**: Aggregate multiple custom metrics for comprehensive assessment

## Two Types of Custom Metrics

### 1. LLM-as-Judge (Example 5-3)

Use an LLM to evaluate subjective qualities that are hard to quantify:

```python
from vertexai.evaluation import PointwiseMetricPromptTemplate

helpfulness_metric = PointwiseMetricPromptTemplate(
    name="helpfulness",
    prompt="""Evaluate the helpfulness of the response.
    Query: {query}
    Response: {response}
    Rate: 1.0 (exceptional), 0.75 (good), 0.5 (adequate), 0.25 (poor), 0.0 (unhelpful)""",
    rubric={"1.0": "Exceptional", "0.75": "Good", "0.5": "Adequate", ...}
)
```

**When to Use:**
- Evaluating tone, style, and appropriateness
- Assessing helpfulness and user satisfaction
- Checking for compliance language
- Qualitative comparisons

### 2. Computation-Based (Example 5-4)

Use deterministic code for precise business rule validation:

```python
def evaluate_portfolio_compliance(recommendation: dict, context: dict) -> dict:
    violations = []

    # Check risk tolerance
    if recommendation["risk_score"] > context["max_risk_tolerance"]:
        violations.append("Risk score exceeds tolerance")

    # Check concentration limits
    for holding in recommendation["holdings"]:
        if holding["percentage"] > 25:
            violations.append(f"Concentration exceeded: {holding['symbol']}")

    return {"compliant": len(violations) == 0, "score": 1.0 if not violations else 0.0}
```

**When to Use:**
- Validating regulatory compliance
- Checking data format and structure
- Enforcing business rules
- Auditable, deterministic validation

## Files

```
02_custom_eval/
├── agent.py          # Financial advisor agent
├── custom_metrics.py # LLM-as-judge + computation-based metrics
├── run_evaluation.py # Demonstration script
├── .env.example      # Environment template
└── README.md         # This file
```

## Quick Start

### 1. Set Up Environment

```bash
cd chapter-5/02_custom_eval
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY
```

### 2. Run Custom Metrics Demo

```bash
python run_evaluation.py
```

### 3. Use in Your Code

```python
from custom_metrics import (
    evaluate_helpfulness_llm,
    evaluate_portfolio_compliance,
    evaluate_diversification,
    run_full_evaluation
)

# LLM-as-judge evaluation
result = await evaluate_helpfulness_llm(
    query="What's a good retirement portfolio?",
    response="Based on your 30-year timeline..."
)
print(f"Helpfulness: {result['score']}")

# Computation-based evaluation
compliance = evaluate_portfolio_compliance(
    recommendation={"risk_score": 7, "holdings": [...], "disclosure_included": True},
    client_context={"max_risk_tolerance": 6}
)
print(f"Compliant: {compliance['compliant']}")
```

## Custom Metrics Included

### LLM-as-Judge Metrics

| Metric | Description |
|--------|-------------|
| `helpfulness` | How helpful and actionable is the response? |
| `compliance_language` | Does it include required disclaimers? |

### Computation-Based Metrics

| Metric | Description |
|--------|-------------|
| `portfolio_compliance` | Does recommendation meet SEC rules? |
| `diversification` | How well-diversified is the portfolio? |
| `risk_appropriateness` | Is risk level suitable for client? |

## Sample Output

```
======================================================================
Custom Metrics Evaluation Demo
======================================================================

Query: I'm 35 and want to retire at 65. What's a good portfolio allocation?

Response: Based on your 30-year timeline, I recommend a growth-focused...

EVALUATION RESULTS:
----------------------------------------

LLM-as-Judge Metrics:
  helpfulness: 0.75
    Reasoning: Good advice with clear recommendations, could be more specific...
  compliance_language: 1.0
    Reasoning: All required disclosures present...

Computation-Based Metrics:
  portfolio_compliance: 1.0
    Compliant: True
    Violations: []
  diversification: 0.85
    Analysis: 4 asset classes, no concentration issues
  risk_appropriateness: 1.0
    Status: appropriate
    Risk in acceptable range: 5-8

AGGREGATE SCORE: 0.92

Results saved to: custom_eval_results_20250114.json
```

## Extending the Metrics

### Add a New LLM-as-Judge Metric

```python
TONE_PROMPT = """Evaluate the tone of this financial advice.
Response: {response}
Is it: professional, empathetic, clear, and appropriate?
Rate: 1.0 (excellent), 0.5 (adequate), 0.0 (poor)"""

async def evaluate_tone(response: str) -> dict:
    # Similar to evaluate_helpfulness_llm
    ...
```

### Add a New Computation-Based Metric

```python
def evaluate_expense_ratios(holdings: list) -> dict:
    """Check if expense ratios are reasonable."""
    high_expense = [h for h in holdings if h.get("expense_ratio", 0) > 0.5]
    return {
        "metric": "expense_ratios",
        "score": 1.0 if not high_expense else 0.5,
        "high_expense_funds": high_expense
    }
```

## Related Resources

- [Vertex AI PointwiseMetricPromptTemplate](https://cloud.google.com/vertex-ai/docs/generative-ai/evaluate/custom-metrics)
- [GCP Custom Metrics Notebooks](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/evaluation/evaltask_approach)
- [Chapter 5: Evaluation and Optimization Strategies](../README.md)
