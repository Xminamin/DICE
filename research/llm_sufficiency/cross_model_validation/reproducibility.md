# Cross-Model Reproducibility Notes（公开版）

- 复现入口：`run_experiment.py`（`--dry-run` / `--models A B C`）；
  Evidence Pack 与问题全部内嵌于本目录（`evidence_export.json` + 脚本常量），
  与已发布研究使用完全相同的固定输入。Credentials are supplied through
  environment variables（`LLM_API_KEY_A/B/C`，见脚本头注释）。
- **实验条件**：temperature=0；同一 case 的四个条件共享同一 Evidence Pack
  （pack hash 见 matrix.json）；prompt 由单一模板生成（生产构造器逐字复刻），
  三模型 prompt_hash 一致。
- **数据规模**：A=deepseek-chat 26 条（21 条复用 Phase 1 + 4 条 B11 重复补齐）、
  B=glm-5.2 22 条、C=glm-5.3-flash 22 条，共 70 条去重后的实验记录。
- **去重**：以 (model, case, condition, repeat, label, raw 前 80 字符) 为键去重。
- **GT 修正**：A14-NEGATIVE 重判 GT_SUFFICIENT（组装型）；B11-NEGATIVE 降 BOUNDARY
  ——详见 README "Ground-truth corrections" 节。
- **Raw 输出**：`raw_outputs.jsonl` 全量 70 条（含模型拒答理由原文），未修改模型
  输出正文。
- **已知限制**：B/C 同属 GLM 家族（原计划异家族模型网关不可用），跨家族泛化
  NOT_ESTABLISHED；N 小；Model-A 数据跨两个日期采集。
- **过程说明（不涉及内部实现细节）**：An initial credential-injection issue
  was corrected before the final run; a data-merge step was re-run to produce
  the deduplicated 70-record file.
- **Evidence 披露**：The public artifact contains only the minimum evidence
  excerpts required for the released experiment; original source documents
  (academic papers and commercial datasheets) are not redistributed.
