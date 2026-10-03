#!/usr/bin/env python3
"""
Cross-Model Validation runner — public, self-contained reproduction script.

Reproduces the Assembly Standard Probe across models with a FIXED evidence
pack, FIXED questions, and a FIXED sufficiency prompt per case.

This script is a cleaned re-packaging of the internal research runner:
  - no private modules, no local absolute paths, no keychain access
  - API credentials are injected via environment variables
  - evidence packs are rebuilt deterministically from the bundled
    `evidence_export.json` (extracted verbatim from the frozen research packs)

Usage:
  export LLM_API_KEY_A=<key>     # Model-A endpoint (OpenAI-compatible)
  export LLM_API_KEY_B=<key>     # Model-B endpoint (optional)
  export LLM_API_KEY_C=<key>     # Model-C endpoint (optional)
  python run_experiment.py --dry-run
  python run_experiment.py --models A
  python run_experiment.py --models A B C

Endpoints/models are configured below; temperature=0 everywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ── model endpoints (OpenAI-compatible chat completions) ────────────────────
MODELS = {
    "A": {"name": "deepseek-chat",
          "url": "https://api.deepseek.com/v1/chat/completions",
          "key_env": "LLM_API_KEY_A"},
    "B": {"name": "glm-5.2",
          "url": os.environ.get("MODEL_B_URL", ""),
          "key_env": "LLM_API_KEY_B"},
    "C": {"name": "glm-5.3-flash",
          "url": os.environ.get("MODEL_C_URL", ""),
          "key_env": "LLM_API_KEY_C"},
}
TEMPERATURE = 0
MAX_TOKENS = 6000

# ── fixed questions (verbatim from the Assembly Standard Probe) ─────────────
VARIANTS = {
 "B11": {
   "DIRECT":    "What is the storage temperature of the DC201 kit?",
   "ASSEMBLY":  "What is the difference between the storage temperatures of "
                "the DC201 kit and the C216 kit?",
   "MIXED":     "What is the storage temperature of the DC201 kit, and how "
                "does it differ from that of the C216 kit?",
   "NEGATIVE":  "What is the shelf life of the DC201 kit?"},
 "A09": {
   "DIRECT":    "What are BERT's pre-training objectives?",
   "ASSEMBLY":  "What is the difference between the pre-training objectives "
                "of BERT and T5?",
   "MIXED":     "What are BERT's pre-training objectives, and how do they "
                "differ from T5's pre-training objective?",
   "NEGATIVE":  "How many citations do the BERT paper and the T5 paper each "
                "have?"},
 "C07": {
   "DIRECT":    "What is the volume of RNase A Solution in the table?",
   "ASSEMBLY":  "Which is larger in volume, RNase A Solution or Buffer AP1, "
                "and by how much?",
   "MIXED":     "What is the volume of RNase A Solution, and how much larger "
                "is Buffer AP1 than RNase A Solution?",
   "NEGATIVE":  "What is the volume of the Binding Plate in the table?"},
 "A14": {
   "DIRECT":    "What is the size of BERT's pre-training data?",
   "ASSEMBLY":  "How much does the training data scale differ between BERT "
                "and LLaMA?",
   "MIXED":     "What is the size of BERT's pre-training data, and how does "
                "it compare to LLaMA's training data scale?",
   "NEGATIVE":  "How many GPUs were used to train each of BERT and LLaMA?"},
}
GT = {"DIRECT": "GT_SUFFICIENT", "ASSEMBLY": "GT_SUFFICIENT",
      "MIXED": "GT_SUFFICIENT", "NEGATIVE": "GT_INSUFFICIENT"}
# GT corrections discovered during the study (see README §GT corrections)
GT_CORRECTIONS = {
    ("B11", "NEGATIVE"): "BOUNDARY",          # component-level duration in pack
    ("A14", "NEGATIVE"): "GT_SUFFICIENT",     # GPU/TPU evidence present (assembly)
}

# ── sufficiency prompt (verbatim production constructor, evidence slots ─────
# filled from evidence_export.json at runtime; identical to the study)
PROMPT_TEMPLATE = """You are an evidence sufficiency evaluator. You must determine if the provided evidence is SUFFICIENT to answer the question.

CRITICAL DISTINCTION:
- "Relevant" means the evidence mentions topics related to the question. This is NOT sufficient.
- "Sufficient" means the evidence actually CONTAINS the information needed to answer the question.

STRICT RULES:
1. You may ONLY evaluate based on the provided evidence below.
2. Do NOT use your own knowledge to fill gaps.
3. If the evidence mentions related topics but does NOT contain the specific answer, return INSUFFICIENT.
4. If two or more evidence pieces give mutually EXCLUSIVE information about the same proposition (not just contrasting descriptions), return CONFLICT.
5. Contrasting descriptions (e.g., "left-to-right" vs "bidirectional" where the paper explains the difference) are NOT conflicts.
6. If you cannot reliably determine, return INDETERMINATE.

IMPORTANT — INDIRECT ANSWERS:
- Evidence can answer a question indirectly. For example, if asked "What GPU was used?" and the evidence says "Training was performed on Cloud TPUs", the evidence IS sufficient — it answers by stating that TPUs (not GPUs) were used.
- If asked "What is X?" and the evidence says "X was not used; Y was used instead", that IS sufficient.
- The key question is: "Could a reader answer the question after reading this evidence?" If yes, return SUFFICIENT.
- Do NOT return INSUFFICIENT merely because the exact word from the question does not appear in the evidence. Evaluate whether the information content answers the question.

MULTI-EVIDENCE:
- Multiple evidence pieces may collectively answer a question even if no single piece does.
- Evaluate the COMBINED content of ALL evidence pieces together.
- If the combined evidence contains enough information to answer, return SUFFICIENT.

QUESTION: {question}

EVIDENCE:
{evidence}

Evaluate whether this evidence (considered collectively) is sufficient to answer the question.

OUTPUT FORMAT (JSON only):
{{
  "sufficiency": "SUFFICIENT" | "INSUFFICIENT" | "CONFLICT" | "INDETERMINATE",
  "reason": "Brief explanation of why this evidence is or is not sufficient",
  "missing_info": "What specific information is missing (if INSUFFICIENT), or empty string"
}}

Answer:"""


def _h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True,
                                     ensure_ascii=False).encode()) \
        .hexdigest()[:16]


def load_packs():
    exp = json.loads((HERE / "evidence_export.json").read_text())
    packs = {}
    for case, evs in exp.items():
        pack_hash = _h([e["evidence_id"] for e in evs])
        packs[case] = {"evidence": evs, "pack_hash": pack_hash}
    return packs


def build_prompt(question, evidence):
    lines = []
    for i, e in enumerate(evidence, 1):
        lines.append(f"[Evidence {i}] (ID: {e['evidence_id']}, Page: "
                     f"{e['page']})")
        lines.append(f"  {e['text']}")
        lines.append("")
    return PROMPT_TEMPLATE.format(question=question,
                                  evidence="\n".join(lines))


def parse_sufficiency(raw):
    import re
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            d = json.loads(m.group(0))
            s = d.get("sufficiency", "INDETERMINATE").upper()
            if s in ("SUFFICIENT", "INSUFFICIENT", "CONFLICT",
                     "INDETERMINATE"):
                return s, d.get("reason", "")
        except json.JSONDecodeError:
            pass
    t = raw.upper()
    if "INSUFFICIENT" in t:
        return "INSUFFICIENT", raw[:200]
    if "SUFFICIENT" in t:
        return "SUFFICIENT", raw[:200]
    return "INDETERMINATE", raw[:200]


def call_model(url, key, model, prompt):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": TEMPERATURE,
                       "max_tokens": MAX_TOKENS}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())["choices"][0]["message"]["content"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["A"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    packs = load_packs()
    jobs = []
    for case in VARIANTS:
        for variant in VARIANTS[case]:
            reps = 3 if (case == "B11" and variant != "NEGATIVE") else 1
            for rep in range(1, reps + 1):
                jobs.append((case, variant, rep))

    if args.dry_run:
        print(f"planned calls per model: {len(jobs)} "
              f"(4 cases × 4 variants + B11 repeats)")
        return

    out_path = HERE / "reproduction_results.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        pass
    for mk in args.models:
        cfg = MODELS[mk]
        key = os.environ.get(cfg["key_env"], "")
        if not key or not cfg["url"]:
            print(f"[{mk}] {cfg['name']}: missing {cfg['key_env']} or URL — "
                  "skipped")
            continue
        for case, variant, rep in jobs:
            q = VARIANTS[case][variant]
            prompt = build_prompt(q, packs[case]["evidence"])
            try:
                raw = call_model(cfg["url"], key, cfg["name"], prompt)
            except Exception as e:
                print(f"[{mk}] {case}/{variant}/r{rep} ERROR {e}")
                continue
            status, reason = parse_sufficiency(raw)
            rec = {"model": mk, "model_name": cfg["name"], "case_id": case,
                   "condition": variant, "repeat_id": rep,
                   "question_hash": _h(q),
                   "evidence_pack_hash": packs[case]["pack_hash"],
                   "prompt_hash": _h(prompt),
                   "model_config": {"temperature": TEMPERATURE,
                                    "max_tokens": MAX_TOKENS},
                   "raw_output": raw, "parsed_status": status,
                   "final_sufficiency_status": status,
                   "llm_reason": reason[:300],
                   "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with open(out_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[{mk}] {case:4} {variant:9} r{rep} → {status}")


if __name__ == "__main__":
    main()
