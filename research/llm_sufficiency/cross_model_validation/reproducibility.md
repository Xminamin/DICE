# Cross-Model Reproducibility Notes
- 可复现入口：cross_model.py（dry-run/run [A|B|C]）；pack/prompt/问题全部来自
  Phase1 probe 模块导入（无重定义）；网关 key 经 macOS keychain（codex-qianfan-token-plan）。
- 复用规则：Model-A 优先匹配 Phase1 同 (case,variant,rep) 行；本轮补齐的 4 次
  B11 DIRECT/MIXED 重复为新调用（已标 non-reused）。
- 已修复的工程事故（如实记录）：①初版从代理脚本读 key 得到 "$(security…)"
  未展开字符串 → 401，改为 keychain 直取；②reused 行首次未落盘 → 合并重建；
  ③一次中途 crash 把 raw 写成 JSON 数组 → 格式兼容读取并重写为标准 jsonl + 去重。
  最终文件 70 行、(model,case,condition,repeat,label,raw前80字符) 唯一。
- 已知偏差源：Model-A 数据跨两个日期（Phase1 前日 + 本轮补齐）；B 的 B11-NEGATIVE
  存在 1 次重复运行（去重保留首条，结果一致均为 I）。
