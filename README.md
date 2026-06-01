# AIGC_DND (Description is Not Detailed)

商品介绍详细度评估规则库 - Aicolate Workflow 规则和 Prompt 存储仓库

## 项目说明

本仓库存储"Description is not detailed//内容中商品介绍不详细"评估 Workflow 的所有规则和 Prompt。

采用 IPP 标准架构：**3 个陪审员 + 1 个裁判**（3 Jurors + 1 Chief Judge）。

## 版本信息

- 当前版本：v1.0（2026-06-01）
- 版本特点：从严筛选，仅用 ASR 判断，全商品适用，不分类目

## 目录结构

```
AIGC_DND/
├── prompts/
│   ├── reviewer_system_prompt.txt      # 陪审员 System Prompt（含 {{body}} 占位符）
│   ├── reviewer_user_prompt.txt        # 陪审员 User Prompt
│   ├── chief_judge_system_prompt.txt   # 裁判 System Prompt
│   └── chief_judge_user_prompt.txt     # 裁判 User Prompt
├── rules/
│   └── rules_text.txt                  # 判定规则（插入到 {{body}} 中）
├── nodes/
│   ├── data_cleaning_node.py           # 数据清洗节点代码（Python FaaS）
│   └── judge_node.py                   # 裁判节点代码（Python FaaS）
└── README.md                           # 本文档
```

## 架构说明

```
[Start] → [RPC] → [数据清洗] → ┌─ [陪审员 A] ─┐
                               ├─ [陪审员 B] ─┤ → [裁判] → [End]
                               └─ [陪审员 C] ─┘
```

### 节点说明

| 节点 | 类型 | 说明 |
|------|------|------|
| 数据清洗 | Python FaaS | 提取 ASR、OCR、商品类目、图片、视频帧等字段，保留全部字段供后续使用 |
| 陪审员 A/B/C | LLM 节点 | 3 个完全相同的 GPT-5.1 节点，独立并行评估 |
| 裁判 | Python FaaS | 多数投票（2/3 通过），验证输出格式，聚合结果 |

## 评估标准

ASR 中包含以下 5 类内容中的**至少 2 项**，且每项都有**具体描述**，即判定为 ✅ OK：

1. **功能/功效介绍**：如"支持主动降噪，降噪深度可达 40dB"
2. **特点/优势说明**：如"采用最新款 A17 处理器，性能提升 30%"
3. **使用方法/适用场景**：如"适合运动时佩戴，防水防汗"
4. **参数/规格说明**：如"6.7 英寸 OLED 屏幕，分辨率 2796×1290"
5. **材质/成分介绍**：如"100% 纯棉材质，柔软透气"

否则判定为 ❌ Description is not detailed。

## Prompt 模板使用说明

### 陪审员 System Prompt 结构

`prompts/reviewer_system_prompt.txt` 采用 IPP 模板格式，包含 `{{body}}` 占位符：

```
## 角色定义
...
## 核心原则
...
## 判定规则

{{body}}

## 输出格式
...
```

实际使用时，将 `rules/rules_text.txt` 的内容插入到 `{{body}}` 位置。

### 优势

- **规则可独立更新**：修改判定规则不需要改动 System Prompt
- **便于添加豁免规则**：后续添加类目豁免、场景豁免等规则时，只需修改 `rules/rules_text.txt`
- **版本管理清晰**：规则变更有独立的变更日志

## 防误判规则

| 编号 | 规则名称 | 说明 |
|------|---------|------|
| FP-01 | 具体描述 vs 笼统描述 | 只有具体描述才算符合，笼统描述（如"功能强大"）不算 |
| FP-02 | 从严判定边界情况 | 不确定或模棱两可的情况，一律判定为"无" |
| FP-03 | 证据引用必须准确 | 引用的内容必须是 ASR 中真实存在的原文 |

## 版本规划

### v1.0（当前版本）
- 3 陪审员 + 1 裁判架构
- 只基于 ASR 判断
- 从严筛选（2/3 多数通过）
- 全商品适用，不分类目

### v1.1（后续版本）
- 加入 OCR 文本判断
- 加入商品类目豁免规则

### v1.2（后续版本）
- 加入视频帧视觉判断
- 检查视频帧中是否有清晰展示商品

## 变更日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2026-06-01 | 初始版本，基于 ASR 的商品介绍详细度评估规则 |
