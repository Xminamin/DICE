# Research Baseline — Phase 0 Failure Casebook & Taxonomy

> 本文档是 Phase 0 失败分析的完整案例册（源自 DICE 真实使用评测的 9 个
> sufficiency 失败案例，含 3 例人审翻案）。它构成 Assembly Probe（Phase 1）
> 与跨模型验证（Phase 2）的研究基线。所有 GT 修正已在原文中透明记录。

---

# 02 — Sufficiency Casebook（9 例，每例含 LLM 自述关键句）

## LLM Over-Conservative（Human=SUFFICIENT / LLM=INSUFFICIENT）×6

**SF-A05**（LLaMA 数据来源）：pack 实含 6/8 来源词+百分比行（Table 1 内容大部分在手）。
LLM 自述："does not list all sources… Table 1 presumably contains the full list but its
contents are not included"——**与 pack 事实不符**（Gutenberg/CommonCrawl 等就在证据里）。

**SF-A09**（BERT vs T5 目标）：两侧证据在 pack。LLM 自述："does not explicitly state
T5's specific objective (span corruption) or **directly compare** the two"。
与历史 Q04（A/B B 臂找回）同构。

**SF-A14**（数据规模差）：LLM 自述："these are in **different units** (words vs. tokens)
and **no conversion or direct comparison is given**"——两侧数值它都看到了。

**SF-B10**（文档章节）：章节标题在 pack。LLM 自述："No table of contents, headings, or
section structure is provided"——**小节标题散在证据里而它要求 TOC 式陈述**。

**SF-B11**（两 kit 温度差）★最典型：LLM 自述："**While the storage temperatures are
present**, the evidence lacks clear linkage **that these are the two kits being
compared**, and **no difference value is stated**"——证据在手的直接承认 + 三重额外要求。

**SF-C07**（体积微升）：全部体积在 pack（对子 C03 同表 ANSWERED）。LLM 自述："volumes
are given in milliliters… **no conversion** or complete microliter values"。

## 人审翻案（LLM 正确）×3

**SF-C08**（zero-shot MMLU）：LLaMA 的 MMLU 仅 five-shot（Table 9/10/16 实证均标 5-shot；
zero-shot 表为 Table 3/6 且不含 MMLU）。LLM 的表级区分**完全准确**。人审原取证只查了
"MMLU 在文档"——过粗。→ REASONABLE_ABSTENTION（修正）。

**SF-C13**（Table 4 GLUE）：BERT 论文 Table 4 = SWAG（实证）；GLUE test 在 Table 1
（82.1 在 pack 且 LLM 引用了）。问题表号指涉错误；LLM 字面拒绝"Table 4 里的 GLUE"
**正确**。→ BOUNDARY（问题措辞错误）。

**SF-C14**（RNase-free 条件）：DC201 全文 "RNase-free" **出现 0 次**（实证；只有 RNase A
组分）。LLM 否定式检查**完全准确**。人审把 RNase A 命中误当 RNase-free 存在。→ REASONABLE_ABSTENTION（修正）。

## 对子 pack 重放（§九归因链）
- C07↔C03：pack **不同**（C03=7 条 ⊂ C07=13 条）——措辞→检索词→pack 构成变化（C 层）
  **叠加** LLM 单位换算标准（A 层）：复合成因。
- C13↔A08：pack 不同但高度重叠（14/17 共享）——差异主要在问题锚定（表号）与 LLM 字面标准。
