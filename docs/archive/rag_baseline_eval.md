# RAG Baseline 测试记录

## 1. 测试目标

验证 EdgeTalk 是否能从工业设备维护知识库中检索相关资料，为后续 Embedding RAG 升级提供 baseline。

## 2. 当前检索方式

当前版本使用 TF-IDF 作为基础检索方案，仅作为第一阶段 baseline。

TF-IDF 能够根据关键词重合度进行检索，但缺点是缺乏语义理解能力。当多个文档都包含相同关键词时，可能出现误命中。

## 3. 测试问题与结果

| 问题 | 预期命中文档 | 实际命中文档 | 是否命中 | 备注 |
|---|---|---|---|---|
| E03 报警是什么意思？ | fault_codes.txt | maintenance_sop.txt | 否 | maintenance_sop.txt 中也出现了“E03 报警消失”，导致 TF-IDF 误判 |
| 更换温度传感器需要做哪些准备？ | maintenance_sop.txt | maintenance_sop.txt | 是 | 命中正确 |
| 每日点检需要检查哪些项目？ | inspection_checklist.txt | inspection_checklist.txt | 是 | 命中正确 |
| 维修设备前需要做哪些安全操作？ | safety_rules.txt | safety_rules.txt / maintenance_sop.txt | 部分命中 | Top1 正确，Top2 存在噪声 |

## 4. 问题分析

当前 baseline 已经跑通工业知识库检索流程，但检索准确性还不稳定。

例如“E03 报警是什么意思？”本应优先命中 fault_codes.txt，因为这是故障代码解释类问题。但 maintenance_sop.txt 中也包含“E03 报警消失”等关键词，因此 TF-IDF 将 SOP 文档排在前面。

这说明关键词检索容易受表面词重合影响，缺乏对“问题意图”和“文档类型”的判断能力。

## 5. 临时优化方案

在 TF-IDF baseline 基础上加入轻量 source boost：

1. 如果问题中出现 E01 / E02 / E03 / E04 等故障代码，优先提升 fault_codes.txt 的分数。
2. 如果问题中出现“更换、SOP、步骤、准备”等词，优先提升 maintenance_sop.txt 的分数。
3. 如果问题中出现“点检、巡检、检查项目”等词，优先提升 inspection_checklist.txt 的分数。
4. 如果问题中出现“安全、断电、防护、气源”等词，优先提升 safety_rules.txt 的分数。

## 6. Source Boost 优化后结果

在 TF-IDF baseline 基础上加入 source boost 后，重新测试 Top1 命中效果。

| 问题 | 预期命中文档 | 优化后 Top1 | 是否命中 |
|---|---|---|---|
| E03 报警是什么意思？ | fault_codes.txt | 未命中 | 命中 |
| 更换温度传感器需要做哪些准备？ | maintenance_sop.txt | 命中 | 命中 |
| 每日点检需要检查哪些项目？ | inspection_checklist.txt | 命中 | 命中 |
| 维修设备前需要做哪些安全操作？ | safety_rules.txt | 命中 | 命中 |

## 8. 阶段性结论

通过 source boost，系统可以根据问题意图对不同类型文档进行轻量优先级调整。该方法能改善故障代码、SOP、巡检、安全类问题的 Top1 命中效果。

但该方法仍然属于规则增强，泛化能力有限。后续仍需升级为 Embedding + 向量检索，并结合检索评估进一步提升准确性。
