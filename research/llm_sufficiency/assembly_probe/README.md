# Assembly Standard Probe — Phase 1

受控实验：4 个真实案例（B11/A09/C07/A14）× hash 锁定 Evidence Pack ×
DIRECT/ASSEMBLY/MIXED/NEGATIVE 四种问题变体 + B11 重复 = 22 次调用（deepseek-chat，
temperature 0）。生产 assess_sufficiency 零修改；原始输出全量存档。

结果：DIRECT 4/4 SUFFICIENT · ASSEMBLY case 级 1/4 · 负控制 4/4 正确拒答 ·
FALSE_SUFFICIENCY = 0。7/7 次组装类拒绝全部命中 "does not explicitly" 句式。
详细结论见 phase1_summary.md；数据见 results/。
