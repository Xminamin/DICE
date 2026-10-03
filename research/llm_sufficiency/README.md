# LLM Evidence Sufficiency Research

English | [中文](README_zh.md)

A controlled research artifact studying how LLMs judge whether **available evidence is sufficient** to answer evidence-grounded questions — focusing on **evidence assembly**, **sufficiency judgment**, **abstention behavior**, and **cross-model comparison**.

> **Status**: RESEARCH ARTIFACT · CONTROLLED STUDY · OFFLINE EXPERIMENT · NOT A LARGE-SCALE BENCHMARK
>
> **LLM RESEARCH = CLOSED** — the research question has been experimentally bounded. No further LLM experimentation is planned unless a new real-world failure provides a new research trigger.

---

## The Problem

Evidence-grounded LLM systems (RAG, document QA, evidence-based agents) do not only need retrieval. They must also answer a question that sits *after* retrieval:

> **"Is the evidence I have enough to answer this question?"**

This seems like a trivial question. It is not. Our research originated from a real productization failure that retrieval quality could not explain:

```
Evidence exists in the document
        ↓
Evidence was retrieved into the candidate set
        ↓
Evidence passed verification and entered the Evidence Pack
        ↓
The LLM still abstained: "evidence insufficient"
```

In a 45-question real-use evaluation, **14 of 15 abstentions occurred while the supporting evidence was verifiably present in the Evidence Pack**. This shifted the research question from *"does the evidence exist?"* to a question that cannot be explained by retrieval quality alone:

> **How does an LLM decide whether available evidence is *sufficient*?**

## One intuitive example

Consider a product datasheet that states:

> *Kit A: store at 15–25°C*  &nbsp;&nbsp; *Kit B: store at –30 to –15°C*

Now ask: **"What is the difference between the storage temperatures of Kit A and Kit B?"**

Both facts are present, verified, and in the evidence pack. But the document never *literally* writes "the difference is X". The answer requires **assembly** — a legitimate comparison of two individually stated facts.

We observed that in such situations, one tested model's own abstention reason acknowledged the evidence was present while still requiring a "direct" statement:

> *"While the storage temperatures are present, the evidence lacks clear linkage that these are the two kits being compared, and no difference value is stated."*

This is the phenomenon this artifact studies under controlled conditions.

## Research Question

When the Evidence Pack is held fixed (hash-locked) and only the question wording varies:

> Does an LLM systematically reject questions whose answers **require assembly of multiple evidence pieces**, while accepting equivalent questions whose answers appear as **direct statements** — and is this behavior model-dependent?

## Experimental Design

| | |
|---|---|
| **Cases** | 4 real cases from a real-use evaluation (B11, A09, C07, A14) |
| **Conditions** | 4 question variants per case: **DIRECT** (answer is stated as-is) · **ASSEMBLY** (answer requires comparison/conversion/combination) · **MIXED** (direct sub-question + assembly sub-question) · **NEGATIVE** (key evidence verifiably absent) |
| **Control** | Evidence Pack fixed per case — byte-identical across all 4 conditions (pack hash locked); only question text varies |
| **Models** | deepseek-chat (A) · glm-5.2 (B) · glm-5.3-flash (C), temperature 0 |
| **Records** | 70 deduplicated experimental records (A: 26, B: 22, C: 22) |
| **Ground truth** | Human-established per case from document forensics; 2 GT corrections applied transparently (below) |

```
Real DICE failure → Evidence present & verified → LLM still abstains
        ↓
Hypothesis: sufficiency judgment requires "ready-made answer statements"
        ↓
Controlled Assembly Probe (pack hash-locked, only question wording varies)
        ↓
Cross-Model Validation (same pack, same prompt, three models)
        ↓
Observed model-dependent behavior
        ↓
Research CLOSED
```

## Main Findings

### Finding 1 — Assembly Aversion observed in deepseek-chat
With the Evidence Pack held byte-identical, `deepseek-chat` judged DIRECT questions SUFFICIENT but judged equivalent ASSEMBLY questions INSUFFICIENT (A09: 3/3 runs; A14: 1/1). The model's own abstention reasons explicitly acknowledged evidence was present while requiring a "direct" statement.

### Finding 2 — Not reproduced in the two GLM-family models tested
Under the same conditions, `glm-5.2` and `glm-5.3-flash` judged the same ASSEMBLY questions SUFFICIENT. Both comparison models belong to the same GLM family, and the intended Kimi / DeepSeek-v4 gateway access was unavailable. **CROSS_FAMILY_GENERALIZATION = NOT_ESTABLISHED.** The tested results support a *model-dependent observation*, not a universal property.

### Finding 3 — Identical-input sufficiency instability in deepseek-chat (B11)
For one case (B11), the same question with the same pack flipped SUFFICIENT ↔ INSUFFICIENT across repeated runs at temperature 0 — in both ASSEMBLY and MIXED conditions. This label-level instability was not reproduced in the GLM-family models.

### Finding 4 — One table-cell-level false sufficiency in glm-5.3-flash
On the C07 negative control, `glm-5.3-flash` judged the evidence SUFFICIENT while citing a table-cell value that does not exist in the evidence. Status: **OBSERVED_ONCE / NOT_GENERALIZED.**

### Ground-truth corrections (part of the methodology)

Two negative-control definitions were corrected after human semantic review. Both are recorded openly:

- **A14-NEGATIVE → reclassified GT_SUFFICIENT (assembly-type)**. The pack contained BERT-TPU and LLaMA-GPU evidence, invalidating the original negative-control definition. Both GLM-family models assembled the correct answer; deepseek-chat abstained — making A14 an additional over-conservatism observation.
- **B11-NEGATIVE → BOUNDARY**. The pack contains component-level "stably stored" duration evidence, so it is not a clean negative control.

## What this artifact contributes

1. **A concrete failure mode**: evidence is present and verified, but a model may still judge assembled evidence as insufficient.
2. **A controlled experimental design**: fixed Evidence Packs allow comparison between DIRECT / ASSEMBLY / MIXED / NEGATIVE conditions.
3. **A reusable research artifact**: released cases, outputs, hashes and a public reproduction scaffold provide a starting point for additional model testing and future benchmark design.

This release does not claim a universal theory of LLM evidence sufficiency.

## What this research teaches beyond this experiment

The following lessons are abstracted from the observed results. Each is labeled by evidence strength: **Observed** (directly seen in this study), **Research implication** (a reasonable transfer suggested by observations, not directly tested here), or **Not established**.

### 1. Retrieval ≠ Evidence Sufficiency
**Observed.** Correct evidence was retrieved, entered the pack, and passed verification — the LLM still returned INSUFFICIENT. Retrieval quality and sufficiency judgment are different problems; fixing the first does not guarantee the second.

### 2. Evidence Presence ≠ Answerability
**Observed.** "Relevant facts exist in the evidence" and "the model judges those facts sufficient to answer" are not the same concept. In our Assembly cases, both component facts were individually present and verified; the judgment failure was about *composition*, not *presence*.

### 3. Direct Evidence ≠ Assembled Evidence
**Observed (model-dependent).** Assembly Aversion was observed in deepseek-chat in this sample, but was not reproduced in the two GLM-family models tested under the same conditions. For evidence-grounded system design, the practical lesson is: **the distinction between "a ready-made answer statement exists" and "the answer can be legitimately assembled" can matter, and it matters differently for different models.**

### 4. Abstention has a system cost
**Research implication.** Abstention is often treated as a free safety mechanism. If a model abstains because "no single sentence contains the complete answer," answerable questions may be routed to human review, additional retrieval, agent retries, or extra LLM calls. Over-conservative sufficiency judgment therefore carries a system-level cost. *(This cost was not measured in this study; it is a design implication supported by the observed abstention pattern.)*

### 5. Evidence sufficiency is itself an evaluable model capability
**Research implication.** Traditional QA pipelines treat Retrieval → Evidence → Answer as the main chain. This study suggests a separate, independently measurable step: Evidence → **Sufficiency Judgment** → Answer/Abstain. "Can the model determine whether the evidence is enough?" can be studied as a capability in its own right.

### 6. Implication for RAG
**Research implication.** RAG systems benefit from distinguishing at least four failure classes: Retrieval Failure · Verification Failure · **Sufficiency Failure** · Answer Generation Failure. This study shows that even when Retrieval and Verification do not fail, Sufficiency can remain an independent bottleneck.

### 7. Implication for Agent systems
**Research implication (not tested here).** An agent deciding "retrieve more? observe more? act now?" implicitly performs an evidence-sufficiency judgment. Evidence acquisition and stopping policies in agentic systems could treat sufficiency judgment as an explicit research dimension. *(No agent behavior was measured in this study.)*

### 8. Implication for Human-in-the-loop systems
**Research implication.** If the model is over-conservative, machine-answerable questions get escalated to human review. The value of a human fallback depends not only on *whether* the model abstains, but on *why*. This connects to the originating project's design principle of routing only genuine exceptions to humans.

### 9. Implication for fine-tuning / model improvement
**Research implication.** Before choosing fine-tuning, prompt calibration, or model replacement, system builders should first localize the failure layer (Retrieval → Candidate → Verification → Evidence Organization → Sufficiency → Reasoning → Binding). Otherwise a system-level evidence problem may be misattributed to model capability.

### 10. Implication for LLM-as-a-Judge / evaluation
**Research implication.** When an LLM is asked "is this evidence sufficient to support this answer?", evaluation designers should distinguish: evidence exists · evidence is sufficient · evidence contains an explicit answer statement · evidence requires legitimate composition · evidence requires unsupported inference. This study shows that "no ready-made complete answer sentence" and "evidence is insufficient" must not be conflated.

## Who may find this useful?

This artifact **may be relevant to** researchers working on: evidence-grounded LLMs and RAG · LLM abstention and selective answering · hallucination and factuality · evidence verification and attribution · multi-hop / compositional QA · long-context reasoning · LLM-as-a-judge · agentic systems that decide "do I have enough information?" · document intelligence and enterprise QA · human-in-the-loop AI.

## Toward a larger benchmark (FUTURE WORK)

The design here is a prototype slice of what a larger evidence-sufficiency benchmark could systematically vary:

- **Evidence structure**: direct / assembled / cross-section / cross-table / cross-document
- **Question structure**: direct lookup / comparison / calculation / multi-constraint / compositional
- **Evaluation dimensions**: correct sufficiency / correct abstention / over-conservative abstention / false sufficiency / stability under identical inputs

No such benchmark is claimed to exist in this release.

## Why not simply fine-tune the model?

This study is **diagnostic first, prescriptive later**. Before proposing fine-tuning, prompt calibration, or model modification, one needs to know: is the failure reproducible under fixed inputs? Is it model-specific? At which layer does it occur? Is the abstention actually wrong? Is assembly the decisive variable? This artifact answers those questions for a small controlled sample.

## Limitations

- Small controlled sample (4 cases × 4 conditions × 3 models)
- Only three tested model configurations
- Model-B and Model-C belong to the same GLM family — cross-family generalization is incomplete
- B11 is a boundary case, not a clean negative control
- A14 required a ground-truth correction
- C07 false sufficiency was observed only once
- No claim of universal model behavior
- No large-scale benchmark claim
- No training effectiveness claim
- No production deployment claim
- Public evidence excerpts are truncated (see Reproduction); original runs used full texts

## Reproduction

The public artifact includes a **public reproduction scaffold using disclosed evidence excerpts** (`run_experiment.py` + `evidence_export.json` + `raw_outputs.jsonl`). Credentials are supplied through environment variables.

The original research used full internal Evidence Packs. The public version retains only the truncated evidence excerpts necessary to reproduce the experiment *structure* and *flow*. Without the original source documents, the scaffold **does not guarantee** per-record reproduction of the original model outputs.

See `cross_model_validation/reproducibility.md` for details.

## Repository layout

```
research/llm_sufficiency/
├── README.md, README_zh.md          # this document (bilingual)
├── research_baseline.md             # Phase 0 casebook & failure taxonomy
├── assembly_probe/                  # Phase 1: controlled probe (deepseek-chat)
│   ├── README.md · phase1_summary.md
│   └── results/ (metrics + 22 raw outputs)
└── cross_model_validation/          # Phase 2: three models, fixed packs
    ├── README.md · summary.md · reproducibility.md
    ├── matrix.json · raw_outputs.jsonl (70 records)
    ├── evidence_export.json         # truncated excerpts for reproduction
    └── run_experiment.py            # public reproduction scaffold
```

## Governance

This artifact is derived from a research question encountered during DICE productization. It does not modify or represent the DICE runtime.

```
FROZEN_BASELINE = INTACT      QA_CORE = UNCHANGED
WEB_MVP = UNCHANGED           REQUIREMENT_ADAPTER = OFF (unchanged)
EVIDENCE_VERIFICATION = UNCHANGED   CLAIM_BINDING = UNCHANGED
RUNTIME_AUTHORITY = ZERO      LLM_RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE            LLM_RESEARCH = CLOSED
```

## Citation

If you use this artifact, please cite the [DICE repository](https://github.com/Xminamin/DICE).
