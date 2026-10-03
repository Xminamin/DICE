# Cross-Model Validation — Phase 2

三模型（deepseek-chat / glm-5.2 / glm-5.3-flash）、同 pack（哈希锁定）、
同问题、同生产 prompt 构造器、temperature 0，共 70 条去重后的实验记录。

- `summary.md` — 完整结果矩阵与 GT 修正记录
- `matrix.json` — 机器可读矩阵
- `raw_outputs.jsonl` — 70 条原始模型输出（已脱敏检查）
- `evidence_export.json` — 冻结 Evidence Pack（复现用）
- `run_experiment.py` — 公开复现脚手架（基于已披露的截断证据摘录；密钥经环境变量注入；不保证逐条复现原始输出）
- `reproducibility.md` — 可复现性细节与已知限制

关键限制：Model-B/C 同属 GLM 家族（原计划 Kimi/DeepSeek-v4 网关无权限），
跨家族泛化 NOT_ESTABLISHED。
