# Cross-Model Validation — Summary

模型：A=deepseek-chat（生产，Phase1 数据复用+补齐）/ B=glm-5.2 / C=glm-5.3-flash
（千帆网关；kimi-k2.6 与 deepseek-v4 无权限——B/C 为同家族不同版本，已列限制）。
输入恒定：同 pack（hash 锁定）+ 同问题 + 生产 prompt 构造器 + temperature=0。

## 1. 实验完整性
A 26 行（21 复用 Phase1 + 4 补齐 B11 重复）/ B 22 / C 22 = 70 条记录，
raw 全量存档 cross_model_raw_outputs.jsonl；中途 401 事故（key 引用未展开）已由
keychain 直取修复，重跑后数据完整。

## 2-3. Pack/Prompt hash 一致性
每 case 的 evidence_pack_hash 三模型完全一致（同表构建）；prompt 由生产
_build_sufficiency_prompt 对同一 pack+问题生成，逐字节一致（Model-A 复用行
prompt_hash 为重建核验）。

## 4. 每模型矩阵
见 cross_model_matrix.json。速览（S=SUFFICIENT，I=INSUFFICIENT）：

| | B11-D | B11-A | B11-M | B11-N | A09-D/A/M | A09-N | C07-D/A/M | C07-N | A14-D/A/M | A14-N |
|---|---|---|---|---|---|---|---|---|---|---|
| A | S(3) | **S/I(3)** | **S/I(3)** | I | S / **I(3)** / I | I | S / S(3) / S | I | S / **I** / S | I* |
| B | S(3) | S(3) | S(3) | I | S / S / S | I | S / S / S | I | S / S / S | S* |
| C | S(3) | S(3) | S(3) | I | S / S / S | I | S / S / S | **S** | S / S / S | S* |
(*=GT 修正后见下)

## 5. 四条件观察（§六）
A. DIRECT：三模型全部 SUFFICIENT——跨模型稳定（OBSERVED）。
B. ASSEMBLY vs DIRECT：**差异仅出现在 Model-A**（A09 稳定拒、A14 拒、B11 概率拒）；
   B/C 上 ASSEMBLY 全 SUFFICIENT（含 A09——Model-A 最稳厌恶案例）。
C. NEGATIVE（修正后有效项）：A09-NEG 三模型全 I ✓；C07-NEG A/B 拒、**C 误放**；
   B11-NEG 降 BOUNDARY（三模型一致拒）；A14-NEG 作废（GT 重判，见 6）。
D. 同输入翻转：**仅 Model-A**（B11-ASSEMBLY S/I/I、补齐后 B11-MIXED 亦 S/I/I）；
   B/C 的 B11 三条件 ×3 全稳。

## 6. GT 修正（本轮最重要的方法学事件）
- **A14-NEGATIVE → GT_INVALID 重判 GT_SUFFICIENT（组装型）**：pack 实含 BERT-TPU
  与 LLaMA-GPU 证据（p11 GPU 表、p13 TPU 行——Phase1 probe 的字面 marker 核验漏检）；
  glm 两模型据此**组装出正确答案**（"BERT=0 GPU/TPU、LLaMA=2048 A100"）。
  → 该格不是 FALSE_SUFFICIENCY，而是 Model-A 的又一例 over-conservative（对照 B/C）。
- B11-NEGATIVE → BOUNDARY（pack 含组分级 "stably stored" 时长）。
- 诚实记录：与 Phase 0 人审翻案同款错误（字面核验 ≠ 语义核验），GT 必须语义级复核。

## 7. Assembly Aversion 是否跨模型出现
**NOT_SUPPORTED（本样本）**——A09/A14/B11 的厌恶与不稳定在 glm-5.2/5.3-flash 上
零复现；组装厌恶是 Model-A（deepseek-chat）特有行为，非任务必然。
限制：B/C 同家族；N 小；仅 OBSERVED 级。

## 8. False Sufficiency
- **真 FALSE_SUFFICIENCY 1 例**：C(C07-NEG)——reason 声称表格含 Binding Plate 的
  "corresponding value"（实际该行无数值）——**表格单元格级幻觉**（OBSERVED，新现象）。
- A14 两例为 GT 重判所致，非误放；B/A 的负控制（有效项）全对。

## 9. 限制
B/C 同 GLM 家族不同版本（网关仅此可用）；每格 N≤3；Model-A 复用行跨日期
（Phase1 于前日运行——其不稳定性可能含时段因素）；无模型优劣评价（规格禁止）。

## 10. 下一步建议（只列不实施）
1. 组装厌恶按"模型相关"重新定位：缓解工程对当前生产模型（A）仍有充分依据
   （A 的厌恶在本轮再次复现且扩展到 B11-MIXED）；
2. 表格单元格幻觉（C 模型）登记为新观察，纳入未来跨模型研究清单；
3. 如需跨家族验证：待网关获得 kimi/deepseek-v4 权限后补 C'，设计已就绪可复跑。
