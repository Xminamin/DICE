# LLM Evidence Sufficiency Research

English | [中文](README_zh.md)

A controlled research artifact studying how LLMs judge whether **available evidence is sufficient** to answer evidence-grounded questions — with a focus on **evidence assembly**, **sufficiency judgment**, **abstention behavior**, and **cross-model comparison**.

> **Status**: RESEARCH ARTIFACT · CONTROLLED STUDY · OFFLINE EXPERIMENT · NOT A LARGE-SCALE BENCHMARK
>
> **LLM RESEARCH = CLOSED** — the research question has been experimentally bounded. No further LLM experimentation is planned unless a new real-world failure provides a new research trigger.

---

## Why does this research exist?

This research emerged from a real productization problem, not from benchmark design.

During the productization of [DICE](https://github.com/Xminamin/DICE) — an evidence-intelligence prototype that converts enterprise documents into verified, human-validated, reusable knowledge — we observed a recurring failure pattern that retrieval quality could not explain:

```
Evidence exists in the document
        ↓
Evidence was retrieved into the candidate set
        ↓
Evidence passed verification and entered the Evidence Pack
        ↓
The LLM still abstained: "evidence insufficient"
```

In a 45-question real-use evaluation, **14 of 15 abstentions occurred while the supporting evidence was verifiably present in the Evidence Pack**. This shifted the research question from *"does the evidence exist?"* to something the retrieval literature answers poorly:

> **How does an LLM decide whether available evidence is *sufficient* to answer a question?**

## The core distinction: direct statements vs. evidence assembly

Many real questions are not answered by a single, ready-made sentence in the document:

```
DIRECT:      Evidence A  →  the answer is already stated

ASSEMBLY:    Evidence A + Evidence B  →  answer requires a
             legitimate composition (comparison / conversion / combination)
```

Our Phase 0 failure analysis (see `research_baseline.md`) found that the abstention reasons shared a striking linguistic pattern — *"the evidence does not **explicitly** state…"* — suggesting the sufficiency judgment behaved more like **"does a complete, direct, citable answer statement exist?"** than **"can the answer be legitimately assembled from the evidence at hand?"**

This artifact tests that hypothesis under controlled conditions.

## What did we find?

Four findings, stated at exactly the strength the data supports:

### Finding 1 — Assembly Aversion observed in deepseek-chat
With the Evidence Pack held byte-identical (hash-locked), `deepseek-chat` judged DIRECT questions SUFFICIENT but judged equivalent ASSEMBLY questions INSUFFICIENT (A09: 3/3 runs; A14: 1/1). We observed the model's own abstention reasons explicitly acknowledge the evidence was present while requiring a "direct" statement.

### Finding 2 — Not reproduced in the two GLM-family models tested
Under the same conditions, `glm-5.2` and `glm-5.3-flash` judged the same ASSEMBLY questions SUFFICIENT. **Cross-family generalization is NOT established** — both comparison models belong to the same GLM family, and the intended Kimi / DeepSeek-v4 gateway access was unavailable. The tested results support a *model-dependent observation*, not a universal property.

### Finding 3 — Identical-input sufficiency instability in deepseek-chat (B11)
For one case (B11), the same question with the same pack flipped SUFFICIENT ↔ INSUFFICIENT across repeated runs at temperature 0 — in both the ASSEMBLY and MIXED conditions. This label-level instability was not reproduced in the GLM-family models.

### Finding 4 — One table-cell-level false sufficiency in glm-5.3-flash
On the C07 negative control, `glm-5.3-flash` judged the evidence SUFFICIENT while citing a table-cell value ("Binding Plate — corresponding value") **that does not exist in the evidence**. Status: **OBSERVED_ONCE / NOT_GENERALIZED**. One false-sufficiency observation involving an unsupported table-cell value was observed in the tested C07 condition.

## Experimental overview

| | |
|---|---|
| Design | 4 real cases × 4 question variants (DIRECT / ASSEMBLY / MIXED / NEGATIVE), Evidence Pack fixed per case (hash-verified) |
| Models | deepseek-chat (A), glm-5.2 (B), glm-5.3-flash (C) — temperature 0 |
| Records | **70 unique experimental records** (A: 26, B: 22, C: 22) — a prototype research artifact, not a benchmark |
| Prompt | A single sufficiency-assessment prompt (verbatim from the production constructor), identical across models |
| Ground truth | Human-established per case from document forensics; two GT corrections applied transparently (below) |

```
Real DICE failure
        ↓
Evidence exists → Retrieval / Verification passed → LLM still abstains
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

### Ground-truth corrections (part of the methodology, not hidden failures)

Two negative-control definitions were corrected after human semantic review of the packs. Both corrections are recorded openly:

- **A14-NEGATIVE → reclassified GT_SUFFICIENT (assembly-type)**. The pack was found to contain BERT-TPU and LLaMA-GPU evidence, invalidating the original negative-control definition. Notably, both GLM-family models *assembled the correct answer* on this case, while deepseek-chat abstained — making A14 an additional over-conservatism observation rather than a control.
- **B11-NEGATIVE → BOUNDARY**. The pack contains component-level "stably stored" duration evidence, so it is not a clean negative control.

## Why does evidence sufficiency matter?

Evidence-grounded LLM systems (RAG, document QA, evidence-based agents) do not only need retrieval. They must also decide: **is the evidence I have enough to answer?** That decision separates several very different situations that are routinely conflated:

1. evidence is missing from the document
2. evidence exists but was not retrieved
3. evidence was retrieved but failed verification
4. evidence is sufficient as-is
5. evidence is insufficient even though related content exists
6. the model incorrectly abstains (over-conservatism)
7. the model incorrectly claims sufficiency (false sufficiency / hallucinated support)

This artifact isolates one slice of that boundary — the difference between (4) "a ready-made answer statement exists" and "the answer can be legitimately assembled" — under controlled conditions.

## Who may find this useful?

The artifact **may be relevant to** researchers working on:

- Evidence-grounded LLMs and RAG
- LLM abstention and selective answering
- Hallucination and factuality (especially *supported-answer* verification)
- Evidence verification and attribution
- Multi-hop / compositional QA
- Long-context reasoning
- LLM-as-a-judge (sufficiency judging is a judging task)
- Agentic systems that must decide "do I have enough information?"
- Document intelligence and enterprise QA
- Human-in-the-loop AI

## Where could these findings matter?

- **RAG / Enterprise Document QA**: a system that cannot distinguish "evidence missing" from "evidence exists but requires assembly" will systematically under-answer compositional questions while appearing *safe*.
- **Evidence-grounded Agents**: an agent's stop/act decision depends on sufficiency judgment; model-dependent assembly aversion directly changes agent behavior under identical observations.
- **LLM Evaluation**: sufficiency-style judgments are increasingly used as automated gates; instability at temperature 0 (Finding 3) is directly relevant to evaluation reliability.
- **Human-in-the-loop systems**: over-conservative abstention routes *answerable* questions to humans, silently inflating review load.

## Why not simply fine-tune the model?

This study is **diagnostic first, prescriptive later**. Before proposing fine-tuning, prompt calibration, or model modification, one needs to know:

- is the failure reproducible under fixed inputs?
- is it model-specific or general?
- at which layer does it occur?
- is the abstention actually wrong (evidence verifiably sufficient)?
- is assembly the decisive variable?

This artifact answers those questions for a small controlled sample. Prescriptive work is future research.

## What can others use from this release?

- **Reproduce** the observed behavior with the bundled self-contained runner (`run_experiment.py` + `evidence_export.json`)
- **Inspect** 70 raw model outputs with abstention reasons (`raw_outputs.jsonl`)
- **Study** evidence-assembly sufficiency with hash-locked packs and pre-registered variants
- **Evaluate** abstention behavior of new models against the same fixed inputs
- **Design** follow-up experiments or larger benchmarks (direction below)

This is **not** a training dataset, and it should not be described as one.

## Toward a larger benchmark (FUTURE WORK)

The design here is a prototype slice of what a larger evidence-sufficiency benchmark could systematically vary:

- **Evidence structure**: direct / assembled / cross-section / cross-table / cross-document
- **Question structure**: direct lookup / comparison / calculation / multi-constraint / compositional
- **Evaluation dimensions**: correct sufficiency / correct abstention / over-conservative abstention / false sufficiency / stability under identical inputs

No such benchmark is claimed to exist in this release.

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
    ├── evidence_export.json         # frozen packs for reproduction
    └── run_experiment.py            # self-contained runner (env-injected keys)
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
