# LLM 证据充分性研究

[English](README.md) | 中文

一个受控研究工件（Research Artifact），研究 LLM 如何判断**已有证据是否足以**回答基于证据的问题——重点关注**证据组装（Evidence Assembly）**、**充分性判断（Sufficiency Judgment）**、**拒答行为（Abstention）**与**跨模型行为对比**。

> **定位**：RESEARCH ARTIFACT · 受控研究 · 离线实验 · **不是**大规模 benchmark
>
> **LLM RESEARCH = CLOSED** —— 研究问题已在实验上被界定边界。除非出现新的真实失败触发新的研究问题，否则不再进行后续 LLM 实验。

---

## 这项研究为什么存在？

本研究来自真实的工程化问题，而非 benchmark 设计。

在 [DICE](https://github.com/Xminamin/DICE)（一个把企业文档转化为"经验证、人工确认、可复用知识"的证据智能原型）的工程化过程中，我们观察到一种检索质量无法解释的失败模式：

```
证据存在于文档中
        ↓
证据被检索进入候选集
        ↓
证据通过验证、进入 Evidence Pack
        ↓
LLM 仍然拒答："证据不充分"
```

在一次 45 题的真实使用评测中，**15 次拒答里有 14 次的支持性证据可以核实确实存在于 Evidence Pack 中**。这使研究问题从"证据存在吗？"转变为检索文献很少回答的问题：

> **LLM 是如何判断"现有证据是否足以回答问题"的？**

## 核心区分：现成陈述 vs. 证据组装

许多真实问题并不由文档中某句现成的话直接回答：

```
DIRECT（直接）：  证据 A  →  答案已被原文直接陈述

ASSEMBLY（组装）：证据 A + 证据 B  →  答案需要一次合法的
                 组合（比较 / 换算 / 合并）才能得出
```

我们的 Phase 0 失败分析（见 `research_baseline.md`）发现，这些拒答理由共享一个醒目的语言模式——*"the evidence does not **explicitly** state…"*（证据并未**明确**陈述……）——这提示充分性判断的行为更接近**"是否存在一句完整、直接、可引用的答案陈述？"**，而不是**"答案能否由现有证据合法组装出来？"**

本工件在受控条件下检验了这一假设。

## 我们发现了什么？

四项发现，措辞严格限定在数据支持的强度内：

### 发现 1 —— 在 deepseek-chat 中观察到组装厌恶（Assembly Aversion）
在 Evidence Pack 逐字节固定（哈希锁定）的条件下，`deepseek-chat` 对 DIRECT 问题判 SUFFICIENT，却对等价的 ASSEMBLY 问题判 INSUFFICIENT（A09：3/3 次运行；A14：1/1）。我们观察到模型自己的拒答理由明确承认证据在场、同时要求"直接"陈述。

### 发现 2 —— 未能在两个 GLM 家族模型中复现
在相同条件下，`glm-5.2` 与 `glm-5.3-flash` 对同样的 ASSEMBLY 问题判 SUFFICIENT。**跨家族泛化并未确立（NOT_ESTABLISHED）**——两个对照模型同属 GLM 家族，且原计划的 Kimi / DeepSeek-v4 网关权限不可用。实验结果支持的是*依赖模型的观察*，而不是普遍属性。

### 发现 3 —— deepseek-chat 出现同输入充分性不稳定（B11）
在同一案例（B11）上，同一问题、同一 pack 在 temperature 0 的重复运行中出现 SUFFICIENT ↔ INSUFFICIENT 翻转——ASSEMBLY 与 MIXED 两种条件下均出现。这种标签级不稳定未在 GLM 家族模型中复现。

### 发现 4 —— glm-5.3-flash 出现一次表格单元格级虚假充分（C07）
在 C07 负控制上，`glm-5.3-flash` 判 SUFFICIENT，其理由引用了一个**证据中并不存在**的表格单元格值（"Binding Plate — corresponding value"）。状态：**OBSERVED_ONCE / NOT_GENERALIZED**（在受测的 C07 条件下观察到一次涉及无依据表格单元格值的虚假充分）。

## 实验概览

| | |
|---|---|
| 设计 | 4 个真实案例 × 4 种问题变体（DIRECT / ASSEMBLY / MIXED / NEGATIVE），每案例 Evidence Pack 固定（哈希校验） |
| 模型 | deepseek-chat（A）、glm-5.2（B）、glm-5.3-flash（C）—— temperature 0 |
| 记录 | **70 条唯一实验记录**（A：26，B：22，C：22）——原型级研究工件，不是 benchmark |
| Prompt | 单一充分性评估 prompt（逐字取自生产构造器），三模型完全一致 |
| Ground truth | 每案例由文档取证人工确立；两次 GT 修正均透明记录（见下） |

```
真实 DICE 失败
        ↓
证据存在 → 检索/验证通过 → LLM 仍拒答
        ↓
假设：充分性判断要求"现成答案陈述"
        ↓
受控组装探针（pack 哈希锁定，仅问题措辞变化）
        ↓
跨模型验证（同 pack、同 prompt、三个模型）
        ↓
观察到依赖模型的行为
        ↓
研究关闭（CLOSED）
```

### Ground Truth 修正（方法学的一部分，而非需要隐藏的失败）

两个负控制定义在人工语义复核后被修正，均公开记录：

- **A14-NEGATIVE → 重判为 GT_SUFFICIENT（组装型）**。复核发现 pack 实际包含 BERT-TPU 与 LLaMA-GPU 证据，原负控制定义无效。值得注意的是，两个 GLM 家族模型在该案例上**组装出了正确答案**，而 deepseek-chat 拒答——因此 A14 实际上构成又一例过度保守观察，而非对照组。
- **B11-NEGATIVE → BOUNDARY**。pack 含组分级 "stably stored" 时长证据，故不是干净的负控制。

## 证据充分性为什么重要？

基于证据的 LLM 系统（RAG、文档问答、证据型 Agent）不仅需要检索，还必须判断：**我手里的证据够不够回答？** 这个判断要区分若干经常被混为一谈的情形：

1. 证据在文档中缺失
2. 证据存在但未被检索到
3. 证据被检索到但未通过验证
4. 证据本身已经充分
5. 证据不足（尽管存在相关内容）
6. 模型错误拒答（过度保守）
7. 模型错误声称充分（虚假充分 / 臆造支撑）

本工件在受控条件下隔离了这条边界的一个切片——(4) "存在现成答案陈述"与"答案可合法组装"之间的区别。

## 谁可能觉得它有用？

本工件**可能与**以下方向的研究相关：

- 基于证据的 LLM 与 RAG
- LLM 拒答与选择性回答
- 幻觉与事实性（尤其是"答案是否有据"验证）
- 证据验证与归因
- 多跳 / 组合式问答
- 长上下文推理
- LLM-as-a-judge（充分性判断本身就是一种评判任务）
- 需要决定"信息是否足够"的 Agent 系统
- 文档智能与企业问答
- 人机协同 AI

## 这些发现可能在哪里产生影响？

- **RAG / 企业文档问答**：无法区分"证据缺失"与"证据存在但需组装"的系统，会系统性地对组合式问题少答，同时表面上显得"安全"。
- **证据型 Agent**：Agent 的停止/行动决策依赖充分性判断；依赖模型的组装厌恶会直接改变 Agent 在相同观察下的行为。
- **LLM 评测**：充分性式判断日益被用作自动化闸门；temperature 0 下的不稳定（发现 3）与评测可靠性直接相关。
- **人机协同系统**：过度保守的拒答会把*本可回答*的问题转给人工，悄悄推高审查负担。

## 为什么不直接微调模型？

本研究**先诊断、后处方**。在提出微调、prompt 校准或模型修改之前，需要先知道：

- 失败在固定输入下是否可复现？
- 是模型特有还是普遍现象？
- 失败发生在哪一层？
- 拒答是否真的错了（证据可核实为充分）？
- 组装是否是决定性变量？

本工件在一个小规模受控样本上回答了这些问题。处方性工作是未来研究。

## 其他人可以从本次发布中使用什么？

- 用捆绑的自包含运行器**复现**观察到的行为（`run_experiment.py` + `evidence_export.json`）
- 检查 70 条含拒答理由的原始模型输出（`raw_outputs.jsonl`）
- 用哈希锁定的 pack 与预注册变体**研究**证据组装充分性
- 用相同固定输入**评估**新模型的拒答行为
- 为后续实验或更大规模 benchmark 提供**设计起点**（方向见下）

这**不是**训练数据集，不应如此描述。

## 迈向更大的 benchmark（未来工作）

本设计是一个更大证据充分性 benchmark 可系统变化维度的原型切片：

- **证据结构**：直接 / 组装 / 跨章节 / 跨表格 / 跨文档
- **问题结构**：直接查找 / 比较 / 计算 / 多条件 / 组合式
- **评估维度**：正确充分 / 正确拒答 / 过度保守拒答 / 虚假充分 / 同输入稳定性

本次发布不声称该 benchmark 已经存在。

## 目录结构

```
research/llm_sufficiency/
├── README.md, README_zh.md          # 本文档（双语）
├── research_baseline.md             # Phase 0 案例册与失败分类学
├── assembly_probe/                  # Phase 1：受控探针（deepseek-chat）
│   ├── README.md · phase1_summary.md
│   └── results/（指标 + 22 条原始输出）
└── cross_model_validation/          # Phase 2：三模型、固定 pack
    ├── README.md · summary.md · reproducibility.md
    ├── matrix.json · raw_outputs.jsonl（70 条记录）
    ├── evidence_export.json         # 冻结 pack（复现用）
    └── run_experiment.py            # 自包含运行器（环境变量注入密钥）
```

## 治理

本工件源自 DICE 工程化过程中遇到的研究问题。它不修改、也不代表 DICE 运行时。

```
FROZEN_BASELINE = INTACT      QA_CORE = UNCHANGED
WEB_MVP = UNCHANGED           REQUIREMENT_ADAPTER = OFF（未变更）
EVIDENCE_VERIFICATION = UNCHANGED   CLAIM_BINDING = UNCHANGED
RUNTIME_AUTHORITY = ZERO      LLM_RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE            LLM_RESEARCH = CLOSED
```

## 引用

如使用本工件，请引用 [DICE 仓库](https://github.com/Xminamin/DICE)。
