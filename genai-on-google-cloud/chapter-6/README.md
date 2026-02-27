<div align="center">
  <img src="../images/owl-front.png" alt="Chapter Guide" width="100"/>
  
  # Chapter 6: Tuning and Infrastructure
</div>

---

## Chapter Overview

This chapter covers fine-tuning strategies for large language models and building scalable inference infrastructure on Google Cloud. You'll learn how to efficiently adapt pre-trained models like Gemma to your specific use cases using techniques like QLoRA, and understand deployment options for production workloads.

## Learning Objectives

Upon completing this chapter, you will be able to:

- **Apply the fine-tuning decision framework** - Determine when to fine-tune vs. use prompt engineering or RAG
- **Configure QLoRA for efficient fine-tuning** - Use 4-bit quantization with LoRA adapters to fine-tune large models on consumer GPUs
- **Deploy from Model Garden** - Select and deploy open-source models from Vertex AI Model Garden
- **Diagnose infrastructure bottlenecks** - Identify bandwidth, memory, compute, and network constraints
- **Optimize serving with vLLM** - Leverage PagedAttention and continuous batching for 2-3x throughput gains
- **Choose deployment platforms** - Select between Agent Engine, Cloud Run, GKE, and Vertex AI Prediction

## Key Concepts Deep Dive

### The Fine-Tuning Spectrum

Model adaptation exists on a spectrum from zero parameters changed to full model retraining:

| Approach | Parameters Changed | Training Time | Use Case |
|----------|-------------------|---------------|----------|
| **Prompt Engineering** | 0 | Minutes | 70% of use cases, fastest iteration |
| **RAG** | 0 | Hours (indexing) | Adding knowledge without changing behavior |
| **Soft Prompts** | ~1K | Hours | Learned prompt prefixes, model unchanged |
| **LoRA/QLoRA** | 0.1-1% | Hours to days | Adapting behavior, preserving base knowledge |
| **Full Fine-Tuning** | 100% | Days to weeks | Complete model adaptation, highest cost |

**Key Insight**: Start with the leftmost approach that solves your problem. Most use cases don't need fine-tuning.

### Model Behavior vs Model Knowledge

Understanding this distinction is critical for choosing the right optimization approach:

**Model Behavior** - *How* the model responds
- **Examples**:
  - "Always cite sources in APA format"
  - "Respond in JSON with specific schema"
  - "Use chain-of-thought reasoning for math problems"
  - "Adopt a professional, empathetic tone"
- **Best Addressed By**: Fine-tuning (LoRA/QLoRA)
- **Why**: Behavior patterns are learned during training, best modified through additional training

**Model Knowledge** - *What* the model knows
- **Examples**:
  - Company policies and procedures
  - Product catalog with specifications
  - Recent events (post-training cutoff)
  - Domain-specific facts and data
- **Best Addressed By**: RAG, tool integration, knowledge bases
- **Why**: Knowledge changes frequently, more efficient to retrieve than retrain

### QLoRA Mechanics for Practitioners

**How QLoRA Makes Fine-Tuning Feasible**:

**1. 4-bit Quantization (NF4)**
- Compresses base model weights from FP16 (16-bit) → 4-bit
- **Memory Reduction**: 75% (16GB model → 4GB)
- Uses NormalFloat4 (NF4) data type optimized for neural network weights
- Base model stays frozen and quantized

**2. LoRA Adapters**
- Learns low-rank matrices (rank typically 8-64) instead of full weight updates
- **Formula**: Instead of updating W, learn ΔW = AB where A and B are much smaller
- Only adapter weights are updated during training (~0.1-1% of parameters)

**3. Practical Impact**
| Model Size | Standard Fine-Tuning | QLoRA Fine-Tuning |
|------------|---------------------|-------------------|
| **Gemma 2B** | ~16GB VRAM | ~6GB VRAM (CPU/T4) |
| **Gemma 7B** | ~56GB VRAM | ~12GB VRAM (T4) |
| **Gemma 13B** | ~104GB VRAM | ~20GB VRAM (L4/A100) |

**Result**: Fine-tune 7B models on consumer GPUs, 13B on single datacenter GPU.

### Infrastructure Cost Modeling

Understanding deployment costs helps make informed infrastructure decisions:

| Deployment | Hardware | Cost/Hour* | Throughput | Best For |
|------------|----------|-----------|------------|----------|
| **Cloud Run** | CPU-only | $0.01-0.05 | 1-5 req/s | Variable traffic, low-volume |
| **Vertex AI (T4)** | T4 GPU | ~$0.50 | 10-20 req/s | Development, testing |
| **Vertex AI (L4)** | L4 GPU | ~$1.20 | 30-50 req/s | Production (medium volume) |
| **GKE (A100)** | A100 GPU | ~$3.00 | 100+ req/s | High-volume production |

_*Approximate costs for us-central1 region. Check [Google Cloud Pricing](https://cloud.google.com/pricing) for current rates._

**Cost Optimization Example**:
- 10,000 requests/day @ 5 req/s → Cloud Run (~$20/month)
- 100,000 requests/day @ 30 req/s → Vertex AI L4 (~$900/month)
- 1,000,000 requests/day @ 100+ req/s → GKE with autoscaling (~$2000-4000/month)

## Key Concepts

### Fine-Tuning Decision Framework

| Criterion | When to Fine-Tune | Alternative |
|-----------|------------------|-------------|
| **Reasoning & Intuition** | Model must synthesize, not just retrieve | Tool integration (MCP) |
| **Domain Specialization** | Niche vocabulary poorly represented | RAG with domain docs |
| **Style & Consistency** | Specific communication patterns required | Few-shot prompting |
| **Response Latency** | Edge/real-time requirements | Model distillation |
| **Economics at Scale** | High-volume with retrieval costs | Continue with RAG |

---

## Fine-Tuning Decision Framework Deep Dive

### Decision Tree: When to Fine-Tune

```
Performance gap identified?
│
├─ Is it a knowledge gap?
│  ├─ Facts/data that change frequently?
│  │  └─ RAG (not fine-tuning) - Knowledge should be updatable
│  ├─ Large knowledge base (>100k docs)?
│  │  └─ RAG with semantic search - More efficient than training
│  └─ Specialized terminology?
│     └─ Consider fine-tuning + RAG - Teach terminology, retrieve facts
│
├─ Is it a behavior/style gap?
│  ├─ Can prompt engineering fix it?
│  │  └─ Try 5-10 iterations first - 70% of cases resolve here
│  ├─ Need consistent format/structure?
│  │  └─ Fine-tuning candidate - Behavior patterns benefit from training
│  └─ Specialized reasoning pattern?
│     └─ Fine-tuning + CoT prompts - Combine approaches
│
├─ Is it a performance gap?
│  ├─ Latency-critical (<100ms)?
│  │  └─ Distillation to smaller model - Teach small model to mimic large
│  ├─ Cost at scale (>1M requests/month)?
│  │  └─ Fine-tune smaller model - Reduce per-request costs
│  └─ Edge deployment?
│     └─ Quantization + fine-tuning - Optimize for resource constraints
│
└─ Is it a safety/compliance gap?
   ├─ Domain-specific harm patterns?
   │  └─ Fine-tuning with safety examples - Teach domain safety
   ├─ Regulatory compliance (finance, healthcare)?
   │  └─ Fine-tuning + guardrails - Ensure consistent compliance
   └─ PII/data restrictions?
      └─ On-premise deployment + fine-tuning - Control data flow
```

### Common Fine-Tuning Mistakes to Avoid

**1. Overfitting on Small Datasets**
- **Problem**: <1,000 examples leads to memorization, not generalization
- **Symptoms**: Perfect training accuracy, poor validation performance
- **Solutions**:
  - Data augmentation (paraphrase, synonym replacement)
  - Early stopping based on validation loss
  - Monitor base model benchmarks (ensure general capabilities preserved)

**2. Catastrophic Forgetting**
- **Problem**: Model loses base capabilities after fine-tuning
- **Symptoms**: Great on your task, fails on general questions
- **Solutions**:
  - Include general examples in training data (20-30%)
  - Use LoRA/QLoRA instead of full fine-tuning
  - Monitor performance on standard benchmarks (MMLU, HellaSwag)

**3. Fine-Tuning for Knowledge**
- **Problem**: Using fine-tuning to add facts (wrong tool for the job)
- **Symptoms**: Model outdated when facts change, expensive to retrain
- **Solutions**:
  - Use RAG for knowledge retrieval
  - Fine-tune only for behavior/style
  - Combine: Fine-tune for behavior + RAG for knowledge

**4. Ignoring Data Quality**
- **Problem**: "Garbage in, garbage out" - low-quality training data
- **Symptoms**: Model learns bad patterns, inconsistent outputs
- **Solutions**:
  - Curate high-quality examples manually
  - Manual review of all training data
  - Diversity in examples (avoid template repetition)
  - Validate outputs match desired behavior

### Infrastructure Bottleneck Patterns

| Pattern | Symptom | Solution |
|---------|---------|----------|
| **Pattern 1: Bandwidth** | GPU utilization 50-70% | Increase memory utilization, enable prefix caching |
| **Pattern 2: Memory** | OOM errors, model doesn't fit | Quantization, tensor parallelism |
| **Pattern 3: Compute** | Sustained 100% utilization | Faster hardware, horizontal scaling |
| **Pattern 4: Network** | Multi-GPU scaling issues | Minimize parallelism, use NVLink |

### QLoRA (Quantized Low-Rank Adaptation)

| Component | Description |
|-----------|-------------|
| **4-bit Quantization** | Reduces model memory footprint using NF4 data type |
| **LoRA Adapters** | Trains small adapter layers instead of full model weights |
| **Efficient Training** | Enables fine-tuning 7B+ models on T4/L4 GPUs |

### Fine-Tuning Workflow

```
┌─────────────────────────────────────────────────────────┐
│                 FINE-TUNING PIPELINE                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Load Base  │→ │  Configure  │→ │  Train LoRA     │ │
│  │  Model      │  │  QLoRA      │  │  Adapters       │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│          ↓                                   ↓         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Deploy to  │← │  Merge      │← │  Evaluate       │ │
│  │  GCS/Vertex │  │  Adapter    │  │  Performance    │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Contents

### Colab Notebooks

| Notebook | Chapter Concepts | What You'll Learn | GPU Required |
|----------|------------------|-------------------|--------------|
| [`01_gemma_finetuning.ipynb`](colabs/01_gemma_finetuning.ipynb) | **Efficient adaptation** (QLoRA for 7B model, 4-bit quantization) | Fine-tune Gemma 7B for financial analysis using QLoRA on T4/L4 GPU | T4+ |
| [`02_model_garden_deployment.ipynb`](colabs/02_model_garden_deployment.ipynb) | **Model selection** (open-source model deployment, Vertex AI integration) | Deploy pre-trained models from Model Garden to Vertex AI endpoints | Optional |
| [`03_vllm_serving.ipynb`](colabs/03_vllm_serving.ipynb) | **Serving optimization** (PagedAttention, continuous batching, 2-3x throughput) | Implement efficient serving with vLLM for production workloads | L4+ |

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ayoisio/genai-on-google-cloud/blob/main/chapter-6/colabs/01_gemma_finetuning.ipynb) Fine-tuning
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ayoisio/genai-on-google-cloud/blob/main/chapter-6/colabs/02_model_garden_deployment.ipynb) Model Garden
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ayoisio/genai-on-google-cloud/blob/main/chapter-6/colabs/03_vllm_serving.ipynb) vLLM Serving

### 📚 Official Google Cloud Model Garden Notebooks

> **Recommended**: For production use cases and the latest model support, we strongly encourage using the official Google Cloud Platform notebook samples. These are actively maintained and cover a wide range of models and deployment scenarios.

**🔗 [GoogleCloudPlatform/vertex-ai-samples - Model Garden Notebooks](https://github.com/GoogleCloudPlatform/vertex-ai-samples/tree/main/notebooks/community/model_garden)**

| Official Notebook | Use Case |
|-------------------|----------|
| [`model_garden_gemma2_deployment_on_vertex.ipynb`](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma2_deployment_on_vertex.ipynb) | Deploy Gemma 2 on Vertex AI |
| [`model_garden_gemma_finetuning_on_vertex.ipynb`](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma_finetuning_on_vertex.ipynb) | Fine-tune Gemma on Vertex AI |
| [`model_garden_gemma_deployment_on_gke.ipynb`](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma_deployment_on_gke.ipynb) | Deploy Gemma on GKE |
| [`model_garden_vllm_text_only_tutorial.ipynb`](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_vllm_text_only_tutorial.ipynb) | vLLM deployment tutorial |
| [`model_garden_huggingface_vllm_deployment.ipynb`](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_huggingface_vllm_deployment.ipynb) | HuggingFace + vLLM deployment |

The official repository includes notebooks for Llama, Mistral, DeepSeek, Qwen, and many other models.

## Setup Instructions

1. Open the notebook in Google Colab using the badge above
2. Enable GPU runtime: **Runtime > Change runtime type > GPU** (T4, L4, or A100)
3. Authenticate with Google Cloud when prompted
4. Set up HuggingFace access for Gemma model weights:
   - Create account at [huggingface.co](https://huggingface.co/join)
   - Accept Gemma license at [huggingface.co/google/gemma-7b-it](https://huggingface.co/google/gemma-7b-it)
   - Create access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
5. Prepare your training dataset (`dataset.jsonl`)

## Prerequisites

- Completion of Chapters 1-5 (recommended)
- Google Cloud project with billing enabled
- Vertex AI API enabled
- HuggingFace account with Gemma model access
- Basic understanding of transformers and fine-tuning concepts

## Deployment Options

| Option | Use Case | Cost | Complexity |
|--------|----------|------|------------|
| **Agent Engine** | Production agents, minimal ops | Managed pricing | Low |
| **Cloud Run** | Variable traffic, serverless | Pay per request | Medium |
| **GKE** | Complex requirements, max control | ~$0.50-$1.00/hour | High |
| **Vertex AI Prediction** | Enterprise, SLA requirements | ~$0.50-$1.00/hour (T4 GPU) | Medium |

---

## Production Deployment Patterns

### Model Lifecycle Management

```
Development                Production                Monitoring
    ↓                         ↓                         ↓
┌──────────┐           ┌──────────┐            ┌──────────┐
│ Fine-tune│           │  Deploy  │            │  Track   │
│ on Colab │  →        │  to GCS  │  →         │ Metrics  │
│ (T4 GPU) │           │ + Vertex │            │ (Ch 7)   │
└──────────┘           └──────────┘            └──────────┘
     ↓                         ↓                         ↓
┌──────────┐           ┌──────────┐            ┌──────────┐
│ Evaluate │           │   A/B    │            │ Retrain  │
│ (Ch 5)   │           │  Test    │            │ Schedule │
└──────────┘           └──────────┘            └──────────┘
```

### Deployment Strategy Selection

**Pattern 1: Serverless (Cloud Run)**
- **Use When**: Variable traffic, <100 req/min, cost-sensitive
- **Pros**: Auto-scaling to zero, pay-per-request, zero ops overhead
- **Cons**: Cold starts (3-5s), limited GPU options (CPU-only in most cases)
- **Example Use Case**: Customer support chatbot with sporadic usage
- **Setup**:
  ```bash
  # Deploy containerized model to Cloud Run
  gcloud run deploy MODEL_NAME \
    --image gcr.io/PROJECT/model:latest \
    --memory 4Gi --cpu 2
  ```

**Pattern 2: Managed (Vertex AI Prediction)**
- **Use When**: Consistent traffic, enterprise SLAs, need monitoring integration
- **Pros**: Managed infrastructure, A/B testing built-in, autoscaling, GPU support
- **Cons**: Higher baseline cost (~$0.50/hour T4 minimum)
- **Example Use Case**: Production RAG system with 24/7 availability
- **Setup**:
  ```bash
  # Deploy model to Vertex AI endpoint
  gcloud ai endpoints create --region=us-central1
  gcloud ai models upload --region=us-central1 \
    --artifact-uri=gs://bucket/model
  ```

**Pattern 3: Self-Managed (GKE)**
- **Use When**: Complex requirements, multi-model serving, cost optimization at scale
- **Pros**: Full control, multi-tenancy, custom autoscaling, GPU pooling
- **Cons**: Kubernetes expertise required, higher ops overhead
- **Example Use Case**: High-volume multi-agent system (>1000 req/min)
- **Key Features**:
  - Horizontal Pod Autoscaling based on GPU utilization
  - Node pools with different GPU types (T4, L4, A100)
  - vLLM or Ray Serve for efficient multi-model serving

**Pattern 4: Hybrid (Agent Engine + Custom Tools)**
- **Use When**: Agent workflows with specialized model needs
- **Pros**: Combines managed agent orchestration with custom models
- **Cons**: Integration complexity, multiple billing sources
- **Example Use Case**: ADK agent with domain-specific fine-tuned tool models
- **Architecture**:
  - Agent Engine handles orchestration and general reasoning
  - Custom fine-tuned models deployed on Vertex AI for specialized tasks
  - MCP tools bridge the two systems

### Cost Optimization Strategies

**1. Model Selection**
- **Use smallest model that meets quality bar**
  - Benchmark: Gemini Flash vs Gemma 7B vs Gemma 2B
  - Quality-cost trade-off: 5% quality drop for 50% cost reduction?
- **Consider distillation**: Fine-tune smaller model to match larger one
  - Train Gemma 2B to mimic Gemini Pro behavior
  - 10x cost reduction with 90% performance retention

**2. Inference Optimization**
- **Quantization**: FP16 → INT8 (2x memory reduction, 1.5x speed)
  ```python
  # Example: 8-bit quantization
  from transformers import AutoModelForCausalLM, BitsAndBytesConfig

  quantization_config = BitsAndBytesConfig(load_in_8bit=True)
  model = AutoModelForCausalLM.from_pretrained(
      "model_id", quantization_config=quantization_config
  )
  ```
- **Batching**: Group requests to amortize overhead
  - Dynamic batching with vLLM (2-3x throughput improvement)
- **Caching**: Store frequent queries, prefix caching for agents
  - Semantic caching for similar queries
  - KV-cache reuse for common prompt prefixes

**3. Infrastructure Right-Sizing**
- **Profile actual usage patterns** (peak vs average load)
  - Most systems: 80% of traffic during 20% of time
  - Autoscale during peak, scale down during off-hours
- **Use spot/preemptible instances for batch workloads**
  - 70% cost reduction for non-time-critical fine-tuning
  - Combine with checkpointing for fault tolerance
- **Scale down during off-hours for non-critical services**
  - Schedule-based autoscaling (e.g., scale to 0 replicas 6pm-6am)

---

## Infrastructure Optimization Deep Dive

### The Four Infrastructure Bottlenecks

**Pattern 1: Bandwidth-Bound** (GPU utilization 50-70%)

**Symptom**: GPU waiting for data from CPU/memory, not fully utilized

**Root Cause**: Model weights don't fit in GPU memory, frequent CPU-GPU transfers

**Solutions**:
- **Increase batch size** to amortize transfer costs
  - From batch_size=1 to batch_size=8 (4-6x throughput improvement)
- **Enable KV-cache prefix caching** (vLLM feature)
  - Reuse computations for common prompt prefixes
  - Critical for agent systems with repeated instructions
- **Use tensor parallelism** to split model across GPUs
  - Distribute layers across multiple GPUs to reduce per-GPU memory

**Monitoring**: Track `gpu_memory_utilization`, `data_transfer_time`

---

**Pattern 2: Memory-Bound** (OOM errors, model doesn't fit)

**Symptom**: Out-of-memory errors, cannot load model

**Root Cause**: Model size exceeds GPU VRAM capacity

**Solutions**:
- **Quantization**: FP16 → INT8/INT4 (2-4x memory reduction)
  ```python
  # 4-bit quantization with QLoRA
  from transformers import BitsAndBytesConfig

  bnb_config = BitsAndBytesConfig(
      load_in_4bit=True,
      bnb_4bit_quant_type="nf4",
      bnb_4bit_compute_dtype=torch.bfloat16
  )
  ```
- **Model sharding**: Split across multiple GPUs
  - Tensor parallelism: Distribute layers horizontally
  - Pipeline parallelism: Distribute layers vertically
- **Offloading**: Keep some layers on CPU (slower but works)
  - CPU offloading for 13B models on 16GB GPU

**Monitoring**: Track `peak_memory_usage`, `memory_fragmentation`

---

**Pattern 3: Compute-Bound** (GPU utilization consistently 100%)

**Symptom**: Sustained high GPU utilization, bottleneck is computation

**Root Cause**: Model is large, workload is compute-intensive

**Solutions**:
- **Upgrade to faster GPU**: T4 → L4 (2.5x), L4 → A100 (3x)
  | GPU | FP16 TFLOPS | Memory | Cost/Hour |
  |-----|-------------|--------|-----------|
  | T4 | 65 | 16GB | ~$0.35 |
  | L4 | 120 | 24GB | ~$0.80 |
  | A100 | 312 | 40GB | ~$2.50 |

- **Horizontal scaling**: Deploy multiple instances
  - Load balancer distributes requests across replicas
  - Linear scaling up to network bandwidth limits

- **Flash Attention**: Faster attention mechanism (2-3x speedup)
  ```python
  # Enable Flash Attention in transformers
  model = AutoModelForCausalLM.from_pretrained(
      "model_id",
      attn_implementation="flash_attention_2"
  )
  ```

**Monitoring**: Track `tokens_per_second`, `latency_p99`

---

**Pattern 4: Network-Bound** (Multi-GPU scaling issues)

**Symptom**: Adding GPUs doesn't improve throughput proportionally

**Root Cause**: Inter-GPU communication bottleneck

**Solutions**:
- **Minimize parallelism degree**: Use fewer, larger GPUs
  - 2x A100 (80GB) > 4x A100 (40GB) for same total memory
- **Use NVLink** for high-bandwidth GPU interconnect
  - 600 GB/s vs 64 GB/s for PCIe
- **Pipeline parallelism** instead of tensor parallelism
  - Reduces communication frequency

**Monitoring**: Track `communication_overhead`, `gpu_idle_time`

---

### vLLM Optimization Techniques

**PagedAttention**: Efficient KV-cache management
- **Problem**: Traditional attention wastes memory with fragmentation
- **Solution**: Page-level memory management (like OS virtual memory)
- **Impact**: 2-3x memory efficiency, enables larger batch sizes

**Continuous Batching**: Dynamic batching of requests
- **Problem**: Static batching waits for all requests to finish
- **Solution**: Add new requests as others complete
- **Impact**: 2-4x throughput improvement in production

**Speculative Decoding**: Predict future tokens in parallel
- **Problem**: Autoregressive generation is sequential (slow)
- **Solution**: Draft model predicts multiple tokens, verified by main model
- **Impact**: 1.5-2x latency reduction with no quality loss

**Prefix Caching**: Reuse computations for common prompts
- **Problem**: Agent systems repeat same instructions/context
- **Solution**: Cache KV values for common prompt prefixes
- **Impact**: 3-5x speedup for agent workloads with shared context

## Learning Resources

### Official Documentation

- [Vertex AI Model Garden](https://cloud.google.com/vertex-ai/docs/start/explore-models) - Browse and deploy open-source models
- [Fine-Tuning Guide](https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models) - Vertex AI fine-tuning documentation
- [vLLM Documentation](https://docs.vllm.ai/) - Efficient LLM serving framework
- [Deployment Best Practices](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) - MLOps patterns for model deployment

### Hands-On Notebooks (Official GCP)

**Model Garden Deployment**
- [Deploy Gemma 2 on Vertex AI](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma2_deployment_on_vertex.ipynb)
- [Deploy Llama models](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_pytorch_llama2_deployment.ipynb)
- [Deploy Mistral models](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_mistral_deployment.ipynb)

**Fine-Tuning**
- [Gemma Fine-Tuning on Vertex AI](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma_finetuning_on_vertex.ipynb)
- [QLoRA Fine-Tuning Tutorial](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_qlora_finetuning.ipynb)
- [Fine-tune Gemma with Keras and LoRA](https://ai.google.dev/gemma/docs/lora_tuning)

**Serving Optimization**
- [vLLM Text-Only Tutorial](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_vllm_text_only_tutorial.ipynb)
- [HuggingFace + vLLM Deployment](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_huggingface_vllm_deployment.ipynb)
- [Serve Gemma on GKE with vLLM](https://cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm)

**Deployment Patterns**
- [Gemma on GKE](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/community/model_garden/model_garden_gemma_deployment_on_gke.ipynb)
- [Deploy to Cloud Run](https://codelabs.developers.google.com/vertex-model-garden-cloud-run)

### Video Tutorials

- [Optimize model serving with GKE Inference Gateway](https://www.youtube.com/watch?v=example)
- [Scaling AI with Google Cloud's TPUs](https://www.youtube.com/watch?v=example)
- [AI workload orchestration options](https://www.youtube.com/watch?v=example)
- [Fine-tuning Gemma with Vertex AI](https://www.youtube.com/watch?v=example)

### Production Tools

**Serving Frameworks**
- [vLLM](https://github.com/vllm-project/vllm) - High-throughput, memory-efficient LLM serving
- [TGI (Text Generation Inference)](https://github.com/huggingface/text-generation-inference) - HuggingFace production serving
- [Ray Serve](https://docs.ray.io/en/latest/serve/index.html) - Scalable multi-model serving
- [Triton Inference Server](https://github.com/triton-inference-server/server) - NVIDIA's optimized serving

**Infrastructure & Monitoring**
- [Vertex AI Model Monitoring](https://cloud.google.com/vertex-ai/docs/model-monitoring) - Drift detection and performance tracking
- [GKE with GPU Support](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus) - Kubernetes GPU orchestration
- [Prometheus + Grafana](https://prometheus.io/) - Metrics collection and visualization
- [Weights & Biases](https://wandb.ai/) - Experiment tracking for fine-tuning

## Need Help?

<table>
<tr>
<td width="100" valign="top">
<img src="../images/owl-right.png" alt="Helper Owl" width="80"/>
</td>
<td>

If you encounter issues with the notebooks, check the error messages carefully and ensure:

- GPU runtime is enabled in Colab
- All required APIs are enabled in your GCP project
- HuggingFace authentication is complete with Gemma access approved

</td>
</tr>
</table>

## What's Next

In **Chapter 7**, you'll learn about monitoring, observability, and maintaining LLM applications in production.

---

[← Previous Chapter: Building a Chatbot](../chapter-5/) | [Home](../) | [Next Chapter: Monitoring & Observability →](../chapter-7/)
