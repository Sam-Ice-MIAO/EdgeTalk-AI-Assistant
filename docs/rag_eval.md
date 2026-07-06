# RAG 检索评估记录

## 1. 目标

本阶段将 EdgeTalk 的 RAG 检索能力从 TF-IDF baseline 升级为 Embedding 语义检索，并对两种检索方式进行基础对比。

## 2. 测试问题

| 问题 | 预期命中文档 |
|---|---|
| E03 报警是什么意思？ | fault_codes.txt |
| 更换温度传感器前需要做哪些准备？ | maintenance_sop.txt |
| 每日点检需要检查哪些项目？ | inspection_checklist.txt |
| 维修设备前需要做哪些安全操作？ | safety_rules.txt |

## 3. 测试结果

| 检索方式 | Top1 命中结果 |
|---|---|
| TF-IDF + source_boost | 4/4 |
| Embedding 检索 | 4/4 |

## 4. 结论

在当前小规模工业知识库中，TF-IDF + source_boost 和 Embedding 检索都能完成基础问题的准确命中。

由于当前知识库规模较小、问题较直接，Embedding 的优势没有明显拉开。但从企业知识库扩展角度看，Embedding 更适合处理语义改写、多样化提问和更大规模文档检索，因此后续默认采用 Embedding 作为主检索方式，TF-IDF 保留为 baseline。

