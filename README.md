# AIGC_DND (Description is Not Detailed)

商品介绍详细度评估 - Aicolate Workflow 规则和 Prompt 存储仓库

## 架构

3 陪审员 + 1 裁判（3 Jurors + 1 Chief Judge），标准 IPP 工单架构。

## 目录结构

```
AIGC_DND/
├── prompts/
│   ├── reviewer_system_prompt.txt              # 陪审员 System Prompt（原始版，含 {{body}} 占位符）
│   ├── reviewer_system_prompt_compressed.txt   # 陪审员 System Prompt（压缩版，英文输出）
│   ├── reviewer_user_prompt.txt                # 陪审员 User Prompt（原始版）
│   ├── reviewer_user_prompt_compressed.txt     # 陪审员 User Prompt（压缩版）
│   ├── chief_judge_system_prompt.txt           # 裁判 System Prompt（原始版）
│   ├── chief_judge_system_prompt_compressed.txt# 裁判 System Prompt（压缩版）
│   ├── chief_judge_user_prompt.txt             # 裁判 User Prompt（原始版）
│   └── chief_judge_user_prompt_compressed.txt  # 裁判 User Prompt（压缩版）
├── rules/
│   ├── rules_text.txt                          # 判定规则（原始版，含示例和详细说明）
│   └── rules_text_compressed.txt               # 判定规则（压缩版，精简核心逻辑）
├── nodes/
│   ├── data_cleaning_node.py                   # 数据清洗节点（Python FaaS）
│   └── judge_node.py                           # 裁判节点（Python FaaS）
└── README.md
```

## 规则引用方式

规则不再嵌入 prompt 文件，而是通过 HTTP Request 引用 raw URL，让 `{{body}}` 占位符动态加载：

```
{{body}} → https://raw.githubusercontent.com/danielwanyan/AIGC_DND/main/rules/rules_text_compressed.txt
```

### Aicolate 节点配置

**陪审员 LLM 节点（juror_a/b/c）：**

| 字段 | 值 |
|------|-----|
| System Prompt | `https://raw.githubusercontent.com/danielwanyan/AIGC_DND/main/prompts/reviewer_system_prompt_compressed.txt` |
| User Prompt | `https://raw.githubusercontent.com/danielwanyan/AIGC_DND/main/prompts/reviewer_user_prompt_compressed.txt` |
| Rules（HTTP Request，填入 `{{body}}`） | `https://raw.githubusercontent.com/danielwanyan/AIGC_DND/main/rules/rules_text_compressed.txt` |

**裁判节点（judge）：**

| 字段 | 值 |
|------|-----|
| System Prompt | `https://raw.githubusercontent.com/danielwanyan/AIGC_DND/main/prompts/chief_judge_system_prompt_compressed.txt` |
| User Prompt | `https://raw.githubusercontent.com/danielwanyan/AIGC_DND/main/prompts/chief_judge_user_prompt_compressed.txt` |

## 数据流

```
[Start] → [RPC] → [数据清洗] → ┌─ [陪审员 A] ─┐
                               ├─ [陪审员 B] ─┤ → [裁判 (Python FaaS)] → [End]
                               └─ [陪审员 C] ─┘
```

- 陪审员 A/B/C：3 个并行 LLM 节点，独立评估 ASR 内容
- 裁判：Python FaaS，多数投票（2/3 通过）

## 评估标准

ASR 中 5 类介绍内容中至少 2 项有具体描述 → OK，否则 not detailed：

1. 功能/功效介绍
2. 特点/优势说明
3. 使用方法/适用场景
4. 参数/规格说明
5. 材质/成分介绍

## 防误判规则

| 编号 | 规则 | 说明 |
|------|------|------|
| FP-01 | 具体 vs 笼统 | 笼统描述（如"功能强大"）不算符合 |
| FP-02 | 从严判定 | 不确定的情况一律判为不通过 |
| FP-03 | 证据引用准确 | 必须引用 ASR 原文，禁止编造 |

## 版本

- v1.0（2026-06-01）：初始版本，ASR-only，从严筛选，全商品适用
- 压缩版（2026-07-03）：全英文输出，token 成本降低 50-80%