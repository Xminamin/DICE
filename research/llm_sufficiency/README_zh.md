# LLM 证据充分性研究

[English](README.md) | 中文

一个受控研究工件（Research Artifact），研究 LLM 如何判断**已有证据是否足以**回答基于证据的问题——重点关注**证据组装（Evidence Assembly）**、**充分性判断（Sufficiency Judgment）**、**拒答行为（Abstention）**与**跨模型行为对比**。

> **定位**：RESEARCH ARTIFACT · 受控研究 · 离线实验 · **不是**大规模 benchmark
>
> **LLM RESEARCH = CLOSED** —— 研究问题已在实验上被界定边界。除非出现新的真实失败触发新的研究问题，否则不再进行后续 LLM 实验。

---

## 问题

基于证据的 LLM 系统（RAG、文档问答、证据型 Agent）不仅需要检索，还必须回答一个*位于检索之后*的问题：

> **"我手里的证据够不够回答这个问题？"**

这个问题看似简单，实则不然。本研究起源于一个仅靠检索质量无法直接解释的工程化失败：

```
证据存在于文档中
        ↓
证据被检索进入候选集
        ↓
证据通过验证、进入 Evidence Pack
        ↓
LLM 仍然拒答："证据不充分"
```

在最初的 45 题真实使用评测中，**15 次拒答里有 14 次的支持性证据可以核实确实存在于 Evidence Pack 中**。这使研究问题从"证据存在吗？"转变为：

> **LLM 是如何判断"现有证据是否充分"的？**

## 一个直观例子

假设一份产品说明书里写着：

> *DC201：15–25°C 保存*  &nbsp;&nbsp; *C216：–30 至 –15°C 保存*

现在问：**"DC201 和 C216 的保存温度相差多少？"**

两个事实都在证据包里、都已验证（它们来自两份不同的产品说明书——即本研究中的真实案例 B11）。但没有任何一份文档*逐字*写出"相差 X"。答案需要**组装（Assembly）**——对两个分别陈述的事实做一次合法比较。

我们观察到，在这种情况下，一个被测模型自己的拒答理由承认证据在场、却仍要求"直接"陈述：

> *"虽然两侧保存温度都在证据中，但证据缺少'这就是被比较的两份试剂盒'的明确关联，也没有陈述差值。"*

本工件在受控条件下研究这一现象。

## 研究问题

当 Evidence Pack 固定不变（哈希锁定）、仅问题措辞变化时：

> LLM 是否会系统性地拒绝那些**需要组装多条证据才能回答**的问题，同时接受等价的、答案以**直接陈述**形式出现的问题——这种行为是否依赖模型？

## 实验设计

| | |
|---|---|
| **案例** | 4 个来自真实使用评测的案例（B11、A09、C07、A14） |
| **条件** | 每案例 4 种问题变体：**DIRECT**（答案原样在文中）· **ASSEMBLY**（答案需比较/换算/合并）· **MIXED**（直接子问题 + 组装子问题）· **NEGATIVE**（关键证据可核实缺失） |
| **控制** | 每案例 Evidence Pack 固定——四种条件下逐字节一致（pack 哈希锁定）；唯一变量是问题文本 |
| **模型** | deepseek-chat（A）· glm-5.2（B）· glm-5.3-flash（C），temperature 0 |
| **记录** | 70 条去重后的实验记录（A：26，B：22，C：22） |
| **Ground truth** | 每案例由文档取证人工确立；2 次 GT 修正透明记录（见下） |

```
真实 DICE 失败 → 证据在场且已验证 → LLM 仍拒答
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

## 主要发现

### 发现 1 —— 在 deepseek-chat 中观察到组装厌恶（Assembly Aversion）
在 Evidence Pack 逐字节固定的条件下，`deepseek-chat` 对 DIRECT 问题判 SUFFICIENT，却对等价的 ASSEMBLY 问题判 INSUFFICIENT（A09：3/3 次运行；A14：1/1）。模型自己的拒答理由明确承认证据在场、同时要求"直接"陈述。

### 发现 2 —— 未能在两个 GLM 系列模型中复现
在相同条件下，`glm-5.2` 与 `glm-5.3-flash` 对同样的 ASSEMBLY 问题判 SUFFICIENT。两个对照模型同属 GLM 家族，且原计划的 Kimi / DeepSeek-v4 网关权限不可用。**CROSS_FAMILY_GENERALIZATION = NOT_ESTABLISHED**。实验结果支持的是*依赖模型的观察*，而非普遍属性。

### 发现 3 —— deepseek-chat 出现同输入充分性不稳定（B11）
在同一案例（B11）上，同一问题、同一 pack 在 temperature 0 的重复运行中出现 SUFFICIENT ↔ INSUFFICIENT 翻转——ASSEMBLY 与 MIXED 两种条件下均出现。这种标签级不稳定未在 GLM 系列模型中复现。

### 发现 4 —— glm-5.3-flash 出现一次表格单元格级虚假充分（C07）
在 C07 负控制上，`glm-5.3-flash` 判 SUFFICIENT，其理由引用了一个证据中不存在的表格单元格值。状态：**OBSERVED_ONCE / NOT_GENERALIZED**。

### Ground Truth 修正（方法学的组成部分）

两个负控制定义在人工语义复核后被修正，均公开记录：

- **A14-NEGATIVE → 重判为 GT_SUFFICIENT（组装型）**。pack 实际包含 BERT-TPU 与 LLaMA-GPU 证据，原负控制定义无效。两个 GLM 系列模型组装出了正确答案；deepseek-chat 拒答——因此 A14 构成又一例过度保守观察。
- **B11-NEGATIVE → BOUNDARY**。pack 含组分级"stably stored"时长证据，故不是干净的负控制。

## 本工件的贡献

1. **一个具体的失败模式**：证据在场且已通过验证，但模型仍可能将"需组装的证据"判为不充分。
2. **一个受控实验设计**：固定的 Evidence Pack 使 DIRECT / ASSEMBLY / MIXED / NEGATIVE 四种条件可以互相比较。
3. **一个可复用的研究工件**：公开的案例、输出、哈希与公开复现脚手架，为进一步测试其他模型与未来 benchmark 设计提供起点。

本次发布不声称提出了关于 LLM 证据充分性的普遍理论。

## 本研究在实验之外的启示

以下启示由观察到的结果归纳而来。每条标注证据强度：**Observed**（本研究直接观察到）、**Research implication**（由观察合理推演的研究/工程启示，本研究未直接测试）、或 **Not established**（未确立）。

### 1. 检索 ≠ 证据充分性
**Observed。** 正确证据被检索出来、进入 pack、通过验证——LLM 仍返回 INSUFFICIENT。检索质量与充分性判断是不同问题；修好前者不保证后者。

### 2. 证据在场 ≠ 可回答性
**Observed。** "证据中存在相关事实"与"模型判断这些事实足以回答问题"不是同一概念。在我们的组装案例中，两个组件事实分别在场且已验证；判断失败在于*组合*而非*在场*。

### 3. 直接证据 ≠ 组装证据
**Observed（依赖模型）。** Assembly Aversion 在 deepseek-chat 中被观察到，但在相同实验条件下测试的两个 GLM 系列模型中未被复现。对证据型系统设计的实践启示：**"存在现成答案陈述"与"答案可合法组装"之间的区别可能产生影响，且对不同模型影响不同。**

### 4. 拒答有系统成本
**Research implication。** 拒答常被视为零成本的安全机制。若模型因"没有一句完整答案"而拒答，本可回答的问题可能被转给人工审查、追加检索、Agent 重试或额外 LLM 调用。过度保守的充分性判断因此产生系统级成本。*（本研究未测量该成本；这是由观察到的拒答模式支持的设计启示。）*

### 5. 证据充分性本身就是一种可评估的模型能力
**Research implication。** 传统 QA 管线把 检索 → 证据 → 回答 视为主链。本研究提示存在一个可独立测量的步骤：证据 → **充分性判断** → 回答/拒答。"模型能否判断证据够不够"本身可以作为一个独立能力来研究。

### 6. 对 RAG 的启示
**Research implication。** RAG 系统受益于区分至少四类失败：检索失败 · 验证失败 · **充分性失败** · 答案生成失败。本研究表明：即使检索与验证都没有失败，充分性仍可能成为独立瓶颈。

### 7. 对 Agent 系统的启示
**Research implication（本研究未测试）。** Agent 决定"再检索？再观察？还是现在行动？"时，隐含地做了一次证据充分性判断。Agent 的证据获取与停止策略可以把充分性判断作为显式研究维度。*（本研究未测量任何 Agent 行为。）*

### 8. 对人机协同系统的启示
**Research implication。** 若模型过度保守，本可由机器回答的问题会被升级到人工审查。人工兜底的价值不仅取决于模型*是否*拒答，还取决于模型*为何*拒答。这与源头项目"只把真正的异常交给人"的设计原则相关联。

### 9. 对微调 / 模型改进的启示
**Research implication。** 在选择微调、prompt 校准或换模型之前，系统构建者应先定位失败层（检索 → 候选 → 验证 → 证据组织 → 充分性 → 推理 → 绑定）。否则系统级证据问题可能被错误归因为模型能力问题。

### 10. 对 LLM-as-a-Judge / 评测的启示
**Research implication。** 当 LLM 被要求判断"这些证据是否足以支持该答案"时，评测设计者应区分：证据存在 · 证据充分 · 证据含有显式答案陈述 · 证据需要合法组合 · 证据需要无依据推断。本研究表明："没有现成完整答案句"与"证据不充分"不能简单等价。

## 谁可能觉得它有用？

本工件**可能与**以下方向的研究相关：基于证据的 LLM 与 RAG · LLM 拒答与选择性回答 · 幻觉与事实性 · 证据验证与归因 · 多跳 / 组合式问答 · 长上下文推理 · LLM-as-a-judge · 需要判断"信息是否足够"的 Agent 系统 · 文档智能与企业问答 · 人机协同 AI。

## 迈向更大的 benchmark（未来工作）

本设计是一个更大证据充分性 benchmark 可系统变化维度的原型切片：

- **证据结构**：直接 / 组装 / 跨章节 / 跨表格 / 跨文档
- **问题结构**：直接查找 / 比较 / 计算 / 多条件 / 组合式
- **评估维度**：正确充分 / 正确拒答 / 过度保守拒答 / 虚假充分 / 同输入稳定性

本次发布不声称该 benchmark 已经存在。

## 为什么不直接微调模型？

本研究**先诊断、后处方**。在提出微调、prompt 校准或模型修改之前，需要先知道：失败在固定输入下是否可复现？是否模型特有？发生在哪一层？拒答是否真的错了？组装是否是决定性变量？本工件在一个小规模受控样本上回答了这些问题。

## 限制

- 小规模受控样本（4 案例 × 4 条件 × 3 模型）
- 仅三个受测模型配置
- Model-B 与 Model-C 同属 GLM 家族——跨家族泛化不完整
- B11 是边界案例，非干净负控制
- A14 经历了一次 ground-truth 修正
- C07 虚假充分仅观察到一次
- 不声称普遍模型行为
- 不声称大规模 benchmark
- 不声称训练有效性
- 不声称生产部署
- 公开证据摘录已截断（见"复现"节）；原始实验使用全文

## 复现

公开工件包含一个**基于已披露证据摘录的公开复现脚手架**（`run_experiment.py` + `evidence_export.json` + `raw_outputs.jsonl`）。凭证通过环境变量注入。

原始研究使用完整内部 Evidence Pack。公开版本仅保留复现实验*结构*与*流程*所必需的截断证据摘录。在没有原始来源文档的情况下，该脚手架**不保证**逐条复现原始模型输出。

详见 `cross_model_validation/reproducibility.md`。

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
    ├── evidence_export.json         # 截断摘录（复现用）
    └── run_experiment.py            # 公开复现脚手架
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
