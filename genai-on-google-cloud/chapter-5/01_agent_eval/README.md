# 01_agent_eval: Agent Tool Usage and Trajectory Evaluation

This sample demonstrates how to evaluate an ADK agent's tool usage and action trajectories using the evaluation framework.

**Chapter Reference**: Example 5-2 - Agent Tool Usage Evaluation

## What This Sample Demonstrates

- **Tool Usage Metrics**: Evaluate if the agent calls the right tools with correct parameters
- **Trajectory Metrics**: Assess if the agent follows the expected sequence of actions
- **Programmatic Evaluation**: Run evaluations from Python code
- **Evaluation Sets**: Define test cases in JSON format

## Key Concepts

### Tool Usage Metrics

| Metric | Description |
|--------|-------------|
| `tool_call_valid` | Are tool calls syntactically correct? |
| `tool_name_match` | Did the agent select the correct tools? |
| `tool_parameter_key_match` | Are parameter names correct? |
| `tool_parameter_kv_match` | Are parameter names AND values correct? |

### Trajectory Metrics

| Metric | Description |
|--------|-------------|
| `trajectory_exact_match` | Sequence matches golden path exactly |
| `trajectory_in_order_match` | Correct sequence with possible extra steps |
| `trajectory_any_order_match` | Required actions in any order |
| `trajectory_precision` | Necessary actions / total actions |
| `trajectory_recall` | Required actions completed / required actions |

## Files

```
01_agent_eval/
├── agent.py         # SmartHome support agent with tools
├── eval_set.json    # Evaluation test cases
├── run_eval.py      # Programmatic evaluation script
├── .env.example     # Environment template
└── README.md        # This file
```

## Quick Start

### 1. Set Up Environment

```bash
cd chapter-5/01_agent_eval
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY
```

### 2. Run Evaluation

```bash
# Programmatic evaluation
python run_eval.py
```

### 3. View Results

The script outputs:
- Aggregate metrics across all test cases
- Individual case results
- JSON file with detailed results

## Evaluation Set Structure

The `eval_set.json` defines test cases:

```json
{
  "eval_set_id": "smarthome_support_eval_v1",
  "eval_cases": [
    {
      "eval_case_id": "case_001",
      "name": "Check thermostat status",
      "conversation": [
        {
          "user_content": {"parts": [{"text": "What's the status of my thermostat?"}]},
          "expected_tool_calls": [
            {"tool_name": "check_device_status", "args": {"device_type": "thermostat"}}
          ],
          "expected_response_contains": ["thermostat", "status"]
        }
      ]
    }
  ]
}
```

## Test Cases Included

| Case | Description | Expected Tools |
|------|-------------|----------------|
| case_001 | Check thermostat status | `check_device_status` |
| case_002 | Set temperature | `set_device_setting` |
| case_003 | Troubleshoot offline camera | `check_device_status`, `troubleshoot_device` |
| case_004 | Get thermostat history | `get_device_history` |
| case_005 | Multi-step workflow | `check_device_status`, `set_device_setting` |
| case_006 | Check doorbell | `check_device_status` |
| case_007 | Troubleshoot cooling issue | `check_device_status`, `troubleshoot_device` |
| case_008 | Disable camera recording | `set_device_setting` |

## Sample Output

```
======================================================================
SmartHome Support Agent Evaluation
======================================================================

Evaluation Set: SmartHome Support Agent Evaluation
Number of test cases: 8

Running case 1/8: Check thermostat status
  ✓ Completed
Running case 2/8: Set thermostat temperature
  ✓ Completed
...

======================================================================
EVALUATION RESULTS
======================================================================

AGGREGATE METRICS:
----------------------------------------

Tool Usage Metrics:
  tool_call_valid: 100.00%
  tool_name_match: 87.50%
  tool_parameter_key_match: 75.00%
  tool_parameter_kv_match: 68.75%

Trajectory Metrics:
  trajectory_exact_match: 50.00%
  trajectory_in_order_match: 75.00%
  trajectory_any_order_match: 87.50%
  trajectory_precision: 85.00%
  trajectory_recall: 87.50%

Results saved to: eval_results_20250114_120000.json
```

## Extending the Evaluation

### Add New Test Cases

Edit `eval_set.json` to add more scenarios:

```json
{
  "eval_case_id": "case_new",
  "name": "Your new test case",
  "conversation": [
    {
      "user_content": {"parts": [{"text": "Your test query"}]},
      "expected_tool_calls": [
        {"tool_name": "expected_tool", "args": {"param": "value"}}
      ]
    }
  ]
}
```

### Custom Metrics

Extend `run_eval.py` to add custom metrics:

```python
def compute_custom_metric(expected, actual):
    # Your custom logic
    return score
```

## Related Resources

- [ADK Evaluation Documentation](https://google.github.io/adk-docs/evaluation/)
- [GCP ADK Agent Evaluation Notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/evaluation/evaluating_adk_agent.ipynb)
- [Chapter 5: Evaluation and Optimization Strategies](../README.md)
