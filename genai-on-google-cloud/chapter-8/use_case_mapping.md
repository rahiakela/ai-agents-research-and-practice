# AI Use Case Prioritization Template

This template helps organizations map and prioritize AI use cases based on business value and ease of execution. Based on Figure 8-8 from Chapter 8.

## The 2x2 Matrix Framework

```
                        HIGH BUSINESS VALUE
                              |
        +-----------------+---+---+-----------------+
        |                 |       |                 |
        |  STRATEGIC      |       |  QUICK WINS     |
        |  BETS           |       |  (Low-Hanging   |
        |                 |       |   Fruit)        |
        |  High value,    |       |  High value,    |
        |  hard to do     |       |  easy to do     |
        |                 |       |                 |
 HARD   +-----------------+-------+-----------------+ EASY
 TO DO  |                 |       |                 | TO DO
        |  AVOID          |       |  FILL-INS       |
        |  (Money Pits)   |       |                 |
        |                 |       |  Low value,     |
        |  Low value,     |       |  easy to do     |
        |  hard to do     |       |                 |
        |                 |       |                 |
        +-----------------+---+---+-----------------+
                              |
                        LOW BUSINESS VALUE
```

---

## Scoring Criteria

### Business Value (Y-Axis)

Rate each use case from 1 (Low) to 5 (High) on these factors:

| Factor | Description | Weight |
|--------|-------------|--------|
| **Revenue Impact** | Direct contribution to revenue growth or new monetization | 30% |
| **Cost Reduction** | Efficiency gains, automation of manual tasks | 25% |
| **Customer Experience** | Improvement in customer satisfaction, retention | 20% |
| **Competitive Advantage** | Differentiation in the market | 15% |
| **Risk Mitigation** | Reduction in compliance, security, or operational risk | 10% |

**Business Value Score** = (Revenue x 0.30) + (Cost x 0.25) + (CX x 0.20) + (Competitive x 0.15) + (Risk x 0.10)

### Ease of Execution (X-Axis)

Rate each use case from 1 (Hard) to 5 (Easy) on these factors:

| Factor | Description | Weight |
|--------|-------------|--------|
| **Data Readiness** | Is the required data available, clean, and accessible? | 30% |
| **Technical Complexity** | Complexity of the AI/ML solution required | 25% |
| **Talent Availability** | Do we have the skills in-house? | 20% |
| **Integration Effort** | Effort to integrate with existing systems | 15% |
| **Regulatory/Compliance** | Regulatory hurdles or approval requirements | 10% |

**Ease Score** = (Data x 0.30) + (Technical x 0.25) + (Talent x 0.20) + (Integration x 0.15) + (Regulatory x 0.10)

---

## Quadrant Guidance

### Quick Wins (High Value, Easy)

**Characteristics:**
- Immediate, measurable impact
- Low risk, high confidence
- Often involve search, summarization, or content generation

**Strategy:** Prioritize first. Use to build momentum, generate quick ROI, and secure executive buy-in for larger initiatives.

**Common Examples:**
- Document search and summarization
- Customer inquiry routing
- Report generation automation
- FAQ chatbots

### Strategic Bets (High Value, Hard)

**Characteristics:**
- Transformative potential
- Significant investment required
- May require new capabilities or data

**Strategy:** Plan carefully. Break into phases, establish clear milestones, and ensure executive sponsorship before starting.

**Common Examples:**
- Autonomous customer service agents
- Predictive maintenance systems
- Personalization engines
- Supply chain optimization

### Fill-Ins (Low Value, Easy)

**Characteristics:**
- Incremental improvements
- Low-risk experiments
- Good for learning and capability building

**Strategy:** Pursue opportunistically when resources allow. Good for training teams on new technologies.

**Common Examples:**
- Internal tool productivity enhancements
- Meeting summarization
- Email drafting assistance
- Code review automation

### Avoid (Low Value, Hard)

**Characteristics:**
- Disproportionate effort for minimal return
- Often "shiny object" projects without clear business case
- May be technically interesting but not strategically valuable

**Strategy:** Deprioritize. If stakeholders push for these, require clear justification of expected ROI.

**Red Flags:**
- "Let's use AI because competitors are"
- No clear success metrics defined
- Complex dependencies on unavailable data

---

## Use Case Mapping Worksheet

### Step 1: List Use Cases

| ID | Use Case | Description | Sponsor |
|----|----------|-------------|---------|
| UC1 | | | |
| UC2 | | | |
| UC3 | | | |
| UC4 | | | |
| UC5 | | | |

### Step 2: Score Business Value

| ID | Revenue (1-5) | Cost (1-5) | CX (1-5) | Competitive (1-5) | Risk (1-5) | **Weighted Score** |
|----|---------------|------------|----------|-------------------|------------|-------------------|
| UC1 | | | | | | |
| UC2 | | | | | | |
| UC3 | | | | | | |
| UC4 | | | | | | |
| UC5 | | | | | | |

### Step 3: Score Ease of Execution

| ID | Data (1-5) | Technical (1-5) | Talent (1-5) | Integration (1-5) | Regulatory (1-5) | **Weighted Score** |
|----|------------|-----------------|--------------|-------------------|------------------|-------------------|
| UC1 | | | | | | |
| UC2 | | | | | | |
| UC3 | | | | | | |
| UC4 | | | | | | |
| UC5 | | | | | | |

### Step 4: Plot and Prioritize

| ID | Use Case | Value Score | Ease Score | Quadrant | Priority |
|----|----------|-------------|------------|----------|----------|
| UC1 | | | | | |
| UC2 | | | | | |
| UC3 | | | | | |
| UC4 | | | | | |
| UC5 | | | | | |

**Priority Legend:**
- P1: Immediate (Quick Wins)
- P2: Planned (Strategic Bets with roadmap)
- P3: Opportunistic (Fill-Ins)
- P4: Deprioritized (Avoid)

---

## Design Thinking Integration

Use case mapping should be combined with Design Thinking to ensure solutions address genuine human needs:

### 1. Empathize

Before mapping:
- Conduct observational interviews with intended end users
- Understand pain points and existing workflows
- Identify unmet needs (not just stated wants)

### 2. Define

During mapping:
- Frame each use case as a problem to solve
- Define success from the user's perspective
- Establish measurable outcomes

### 3. Ideate

After mapping:
- For each prioritized use case, brainstorm solution approaches
- Consider multiple AI/non-AI alternatives
- Challenge assumptions

---

## Critical User Journeys (CUJs)

For each prioritized use case, define the Critical User Journey:

| Element | Description |
|---------|-------------|
| **User Persona** | Who is the primary user? |
| **Goal** | What is the single most important outcome? |
| **Steps** | What sequence of actions achieves the goal? |
| **Pain Points** | Where does the current process break down? |
| **Success Criteria** | How do we measure improvement? |

---

## Worked Example: Cymbal Media

*A fictional global content and advertising platform mapping GenAI use cases.*

### Use Cases Identified

| ID | Use Case | Description |
|----|----------|-------------|
| UC1 | Content Summarization | Auto-summarize long-form articles for social distribution |
| UC2 | Ad Targeting Agent | Multi-agent system for personalized ad placement |
| UC3 | Video Transcription | Automated transcription and captioning |
| UC4 | Predictive Trending | Predict content virality before publication |
| UC5 | Internal Doc Search | Enterprise search for policy documents |

### Scoring

| ID | Use Case | Value | Ease | Quadrant |
|----|----------|-------|------|----------|
| UC1 | Content Summarization | 4.2 | 4.5 | Quick Win |
| UC2 | Ad Targeting Agent | 4.8 | 2.3 | Strategic Bet |
| UC3 | Video Transcription | 3.5 | 4.2 | Quick Win |
| UC4 | Predictive Trending | 4.0 | 1.8 | Strategic Bet |
| UC5 | Internal Doc Search | 2.5 | 4.8 | Fill-In |

### Visual Mapping

```
        HIGH VALUE
            |
    UC2*    |     *UC1
            |     *UC3
    UC4*    |
            |
  ----------+---------- EASY
            |
            |     *UC5
            |
        LOW VALUE
```

### Prioritization

| Priority | Use Case | Rationale |
|----------|----------|-----------|
| **P1** | UC1: Content Summarization | High value, proven technology, immediate ROI |
| **P1** | UC3: Video Transcription | Quick win to build AI credibility |
| **P2** | UC2: Ad Targeting Agent | High value but requires multi-agent expertise; phase over 12 months |
| **P2** | UC4: Predictive Trending | Strategic but needs data pipeline investment |
| **P3** | UC5: Internal Doc Search | Nice to have; implement if time allows |

---

## Workshop Facilitation Tips

When running a use case mapping workshop:

1. **Participants**: Include business stakeholders, technical leads, and end users
2. **Preparation**: Pre-work to gather use case ideas from each stakeholder
3. **Calibration**: Score 2-3 use cases together to calibrate scoring approach
4. **Debate**: Encourage healthy disagreement on scores
5. **Output**: Leave with prioritized list and next steps for top use cases

---

## Next Steps

After completing use case mapping:

1. **For Quick Wins**: Create 30-day execution plans
2. **For Strategic Bets**: Develop detailed roadmaps with [roadmap_template.md](./roadmap_template.md)
3. **Reassess Quarterly**: As capabilities grow, previously "hard" use cases may become easier
