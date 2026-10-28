# R1-B 冷启动复现输出（条件 B 结构化提问）——AI 输出逐字存档

- **运行日期**：2026-10-28；**运行者**：另一个新的隔离子代理（与 R1-A 运行者相互隔离）
- **输入**：与原始 B1 完全相同的包装语 + 条件 B 提示词 + 同一份按页论文全文
- **用量回执**：subagent_tokens 207,566；tool_uses 3；duration 552.7 s
- **独立性声明**：同 R1-A。以下为答复全文，逐字未改。

---

# 《Compilation Is Not Correctness: Scan-by-Scan Evaluation of LLM-Generated PLC Programs》结论提取

说明：页码均为 PDF 物理页码（与"论文全文-按页.md"一致）。公共背景：论文提出基准 CycleBench 与生成框架 CycleGen；评测器把 ST 经 Matiec 转 C、GCC 编译后，在对齐的输入、初值与逻辑时间下，逐扫描比较候选程序与隐藏参考程序的全部声明输出/inout（§3.2，第 5–6 页）。以下引文为英文原文。

## 一、主要结论清单

### 结论 1｜CycleBench 是首个对 LLM 生成的 ST 程序做"隐藏参考 + 逐扫描行为评测"的基准【论文声明】
- 原文出处：第 3 页，Contributions 第 1 条；规模见第 6 页 Table 2。
- 原文引文："To our knowledge, the first benchmark"（第 3 页）
- 成立条件：
  - 数据集/任务：301 个 ST 任务（287 功能块 + 14 程序）、684 个场景、共 61,424 次扫描（Table 2，第 6 页）；来源含 Broad/Curated GitHub、AutoPLC 库、Agents4PLC、Matiec/OpenPLC 示例共六条途径（第 4、6 页）；参考程序与评测场景对生成方法隐藏（第 4 页）。
  - 模型/实验规模：基准构建用 DeepSeek-V3.2、Grok-4.6 辅助起草需求，用 Grok-4.6、Qwen3-Coder-Next 生成场景输入（第 5 页）。
  - 关键设置：591 个候选参考 → 执行筛除 12 → 去重与人工选择排除 274 → 评审再排除 4，得 301 任务（第 5 页）；两位 PLC 工程师联合评审（第 5 页）；运行时为固定构建的 Matiec + GCC（第 5 页）；评测机器硬件：原文未说明。
  - 假设/范围：作者以"To our knowledge"自我限定（第 3 页）；代码与数据"计划同行评审后公开"（第 19 页），正文中未见已发布。

### 结论 2｜编译通过率显著高于执行通过率：池化差距 11.92 个百分点，且出现在每个模型—方法组合中【实验支持】
- 原文出处：第 12 页 §6.1 与 Table 5；摘要数字见第 1–2 页。
- 原文引文："compile but only 72.07% pass execution"（第 2 页）
- 成立条件：
  - 数据集/任务：CycleBench 全部 301 任务。
  - 模型/实验规模：8 个模型部署 × 4 种基线配置（Direct、Agents4PLC、LLM4PLC、AutoPLC）= 9,632 个基线结果；83.99% 可编译、72.07% 通过执行，差距 11.92pp（95% 任务簇 bootstrap CI [9.63, 14.43]，第 12 页）。
  - 关键设置：三个外部基线为公开材料"适配版"而非原生复现（Table 4，第 10 页）；16,384-token 输出上限；初始生成温度 0.7（第 10–11 页）；指标为编译率/执行通过率/差距，每条件每任务只取一个返回程序，失败留在分母（第 11 页）；差距含编译后全部失败阶段（Table 5 表注，第 12 页）；硬件：原文未说明。
  - 假设/范围："The gap appears in every model–method combination"（第 12 页），含编译率高于 99% 的组合；但差距量级随条件变化（见结论 3、Table 5 各组合 4.98–18.94pp）；编译率排名与执行率排名可反转：LLM4PLC 编译率最高（90.53%）而 Agents4PLC 执行率最高（76.33%）（第 12 页）。

### 结论 3｜参考程序越长，执行通过率越低、编译—执行差距越大【实验支持】
- 原文出处：第 7 页 §3.5 与 Table 3（按参考长度分组的池化率）。
- 原文引文："grows from 3.67 to 24.07 points"（第 7 页）
- 成立条件：
  - 数据集/任务：301 任务按参考 LOC 分四组（1–20/21–40/41–80/>80，每组 75/145/54/27 任务）。
  - 模型/实验规模：8 模型 Direct 结果的池化（每任务 8 个模型结果）。
  - 关键设置：执行通过率从最短组 87.17% 降至最长组 48.61%，差距从 3.67 增至 24.07pp；表注明"LOC groups describe reference size, not model-derived difficulty"（第 7 页）；中间各组不必单调下降；每个来源组的池化差距均为正，但 Matiec、OpenPLC 组仅 4、3 个任务（第 7 页）；硬件：原文未说明。
  - 假设/范围：结论限于"最短组 vs 最长组"的方向性对比（"All eight models perform worse in the longest group than in the shortest"，第 7 页）。

### 结论 4｜编译失败以语句/声明畸形为主：占 Direct 编译失败的 53.42%【实验支持】
- 原文出处：第 13–14 页 §6.2，Table 6(a)（n=146）。
- 原文引文："account for 53.42% of compiler failures"（第 14 页）
- 成立条件：
  - 数据集/任务：301 任务上 5 个模型（GPT-5.5、GPT-4o、Sonnet 4、Haiku 4.5、GLM-5.2）的 Direct 结果。
  - 模型/实验规模：1,505 个 Direct 结果中 9.70%（146 个）编译失败；诊断子集共 6,020 个基线结果（第 11、13 页）。
  - 关键设置：按"首个编译器诊断"归类，避免级联消息重复计数；分类的是症状而非根因（"reported symptoms, not definitive root causes"，第 13 页）；细项：畸形语句 41（28.08%）、畸形声明 37（25.34%）、类型不兼容 21（14.38%）等（Table 6(a)）；硬件：原文未说明。
  - 假设/范围：仅覆盖这 5 个模型的 Direct 失败；作者声明"这些症状本身不能确立行为正确性"（第 14 页）。

### 结论 5｜行为失败集中于输出更新、算术/边界与时序/调用次序三类，合计 65.6%；运行时检查能揭示编译反馈无法确立的状态与取值错误【实验支持】
- 原文出处：第 13–14 页 §6.2，Table 6(b)（n=157）及 RQ2 答案。
- 原文引文："account for 65.6% of behavioral failures"（第 14 页）
- 成立条件：
  - 数据集/任务：同结论 4 的 5 模型 Direct 结果。
  - 模型/实验规模：157 个 Direct 行为失败（69 个任务、156 个不同程序；154 个实现错误 + 3 个数值案例），占 1,505 结果的 10.43%（第 11、13 页）。
  - 关键设置：由一名评审用代码本为每个失败指定唯一主类别；独立标注一致性 33/40（82.5%），未加权 Cohen's κ = 0.78（95% CI [0.61, 0.91]）（第 14 页）；数值不一致单独归类（第 13 页）；时序/调用次序类含"在赋当前扫描输入之前调用有状态块"（第 14 页，例见图 5）；硬件：原文未说明。
  - 假设/范围：单一主标签方法有局限（7 处标注分歧中 6 处涉及"公共输出更新"这一宽泛类别，第 14 页）；一致性检验不等于根因唯一。

### 结论 6｜CycleGen 端到端将执行通过率从 74.63% 提升到 83.31%（+8.68pp），超过全部适配基线【实验支持】
- 原文出处：第 12 页 §6.1 与 Table 5；摘要与第 3 页。
- 原文引文："from Direct's 74.63% to 83.31%"（第 3 页）
- 成立条件：
  - 数据集/任务：301 任务，8 模型（2,408 个任务—模型对）。
  - 模型/实验规模：CycleGen 94.89% 编译 / 83.31% 执行；超 Direct 8.68pp（CI [7.23, 10.22]）、适配 Agents4PLC 6.98pp（CI [5.02, 9.01]）、LLM4PLC 8.89pp、AutoPLC 20.39pp；每模型超其最佳基线 1.66–12.29pp（第 12 页）。
  - 关键设置：k=5 个候选（种子 42–46），候选 1 与 Direct 共享；测试套件 ≤6 用例、每例 ≤10 扫描、共 ≤40 扫描（第 11 页）；预训练模型、无示例检索、无基准微调（第 10 页）；各方法预算不同，端到端对比含推理预算差异，统计推断只报告池化配对对比（第 12 页）；RQ3 用受控池分离组件效应；硬件：原文未说明。
  - 假设/范围：对比对象是"适配版"基线而非原生系统（第 10 页）；CycleGen 仍留 11.59pp 编译—执行差距（Table 5）。

### 结论 7｜仅靠"多候选 + 首个合格候选"就把执行通过率从 74.63% 提到 79.94%（+5.32pp）【实验支持】
- 原文出处：第 14 页 §6.3 与 Table 7（Multiple candidates 行）。
- 原文引文："a 5.32-point gain over Direct"（第 14 页）
- 成立条件：
  - 数据集/任务：301 任务 × 8 模型（2,408 任务—模型对）。
  - 模型/实验规模：同一批 5 个初始候选的受控池（Table 7）。
  - 关键设置：该对比只改采样预算、不改上下文或提示（"changes sampling budget, not context or prompt"，第 14 页）；平均 token 从 1,929 升至 9,740（Table 7）；选择器为"首个保接口且通过 ST→C 翻译的候选"；硬件：原文未说明。
  - 假设/范围：消融为探索性比较，固定候选池而非固定总推理资源（第 16 页）。

### 结论 8｜受控池上 Compile-Fix 贡献 +2.28pp、自测选择（Self-Test + Selection Gate）贡献 +1.62pp【实验支持】
- 原文出处：第 14–16 页 §6.3，Table 7 与 RQ3 答案。
- 原文引文："Compile-Fix adds 2.28 points"（第 16 页）
- 成立条件：
  - 数据集/任务：同结论 7 的受控池（相同 5 个初始候选、相同共享测试套件）。
  - 模型/实验规模：2,408 任务—模型对。
  - 关键设置：去 Compile-Fix 使执行率降 2.28pp（CI [1.45, 3.16]）、编译率 94.89%→92.23%，token 增量 2,183；自测选择救回 49、破坏 10，净 +1.62pp（CI [0.91, 2.37]；Holm 校正 p = 1.14×10^-5），token 11,922→18,197；未修复池上选择 +1.08pp（[0.50, 1.70]）（第 15 页）；Self-Test 与 Selection Gate 联合评估、"their individual effects are not separately identified"（第 14 页）；自测选择对比含构建验证与行为排序两部分（第 15 页）；硬件：原文未说明。
  - 假设/范围：这些是"conditional gains"（条件增益），仅在该控制方案下成立（第 16 页）。

### 结论 9｜候选数超过 5 后执行通过率不再提升，token 成本却上升（k=8 时 +38.8% 且少 4 个通过）【实验支持】
- 原文出处：第 15 页 §6.3 与 Fig. 4；结论重述见第 18 页 §8。
- 原文引文："without improving execution pass rate"（第 18 页）
- 成立条件：
  - 数据集/任务：301 任务 × 8 模型。
  - 模型/实验规模：冻结的生成序前缀 k = 1…8（Fig. 4）。
  - 关键设置：k=1（含 Compile-Fix）78.53% → k=5 83.31%；k=3→5 仅 +21 个通过（0.87pp）而 token +35.6%（13,419.9→18,197.2）；k=8 token 25,256.6（+38.8%）且少 4 个选中通过（0.17pp）（第 15 页）；k=5 时平均 7 次模型调用、18,197 token，Direct 为 1 次、1,929 token（第 15 页）；候选 6–8 用种子 47–49（第 11 页）；本地执行、美元成本与延迟不计入该度量（第 15 页）；硬件：原文未说明。
  - 假设/范围：作者明确限定——"this does not establish a generally optimal or equal-resource budget"（第 15 页）；Oracle@k（无接口约束的池上限）在 k=5→8 从 86.42% 升到 87.58%，但选中率不升（第 15–16 页）。

### 结论 10｜粗粒度观测会漏检行为失败：每 2/5/10 个扫描检查漏掉 7.01%/21.66%/29.94%，仅查末扫描漏掉 62.42%（98/157）【实验支持】
- 原文出处：第 16–17 页 §6.4；摘要（第 1 页）；场景端点保留。
- 原文引文："misses 21.66% of the 157 failures"（第 1 页）
- 成立条件：
  - 数据集/任务：157 个由逐扫描比较检出的 Direct 行为失败（同结论 4 的 5 个模型，1,505 个 Direct 结果）。
  - 模型/实验规模：固定程序与轨迹的事后重放分析；全部 157 条失败轨迹均经观测验证。
  - 关键设置：程序、输入、输出集合与"解码后类型—取值相等"判据全部固定，只改观测位置（第 16 页）；步长 2/5/10 分别漏 11/34/47 个；表观通过率从逐扫描的 79.53% 升到 80.27%/81.79%/82.66%；仅末扫描漏 98 个（62.42%；CI 50.00–74.14%），表观通过率 86.05%（第 16–17 页）；硬件：原文未说明。
  - 假设/范围："Higher apparent pass rates therefore reflect missed evidence rather than better code"（第 18 页）；该分析不改变程序与输入历史，输入覆盖是另一问题（第 18 页）。

### 结论 11｜漏检机制是瞬态输出不一致：144/157 的失败会在场景内重新一致，含全部 98 个末扫描漏检【实验支持】
- 原文出处：第 17 页 §6.4（机制分析）、Fig. 5（计时器例子）、Fig. 6(a)；摘要（第 1 页）。
- 原文引文："transient output discrepancies"（第 1 页）
- 成立条件：
  - 数据集/任务：同结论 10 的 157 个失败，关联 RQ2 的审计标签。
  - 模型/实验规模：按任务、模型、候选哈希连接失败与标签。
  - 关键设置：仅末扫描检查漏掉 31/43 输出更新、9/14 状态保持、8/13 边沿检测类失败（Fig. 6(a)）；115/157 失败的失配连续段不超过 5 个扫描（第 17 页）；跨场景复位不计为重新一致（第 17 页）；Fig. 5 的例子：候选在更新当前输入前调用 TOF 定时器，第 7 扫描出错、8–9 扫描又一致（第 17 页）；硬件：原文未说明。
  - 假设/范围："visible agreement does not establish internal-state equivalence"（第 17 页）。

### 结论 12｜漏检哪些失败取决于采样相位：每个固定相位都会漏检（每 5 扫描跨相位漏检率 12.10%–28.03%）【实验支持】
- 原文出处：第 17 页 §6.4 与 Fig. 6(b)；摘要（第 1 页）。
- 原文引文："Every fixed phase misses failures"（第 17 页）
- 成立条件：
  - 数据集/任务：同结论 10 的 157 个失败、固定轨迹。
  - 模型/实验规模：对步长 k∈{2,5,10} 均匀施加所有相位并保留场景端点。
  - 关键设置：相位 0 时漏 11/34/47 个；跨相位范围分别为 11–17、19–44、25–56 个；等权相位均值 14.0/31.0/44.9（第 17 页）；19/157=12.10%、44/157=28.03%（摘要，第 1 页）；端点保留会略微改变观测预算（第 17–18 页）；硬件：原文未说明。
  - 假设/范围："Full-trace dominance is structural; these results quantify its magnitude, mechanisms, and phase sensitivity on fixed traces."（第 18 页）。

### 结论 13｜（适用性声明）通过评测只表明在给定有限场景上与参考一致，不等于完全功能正确、可终止或物理安全【论文声明】
- 原文出处：第 6 页 §3.2"Isolation and validity"；第 18 页 Threats（Construct validity）。
- 原文引文："on the supplied finite scenarios"（第 6 页）
- 成立条件：
  - 数据集/任务：CycleBench 的 684 个有限场景；通过要求所有场景、全部扫描完全匹配（第 6 页）。
  - 模型/实验规模：适用于全部被评方法与模型。
  - 关键设置：精确相等判据可能把数值舍入差异记为失败（RQ2 单独标注，第 6、13 页）；逻辑时间按扫描调度推进，"physical timing guarantees require separate measurements"（第 6 页）；硬件（物理时序测量）：原文未说明。
  - 假设/范围：结论"subject to reference validity"（以参考有效为前提，第 6 页）；不覆盖未见输入、物理行为与终止性（第 18 页）。

### 结论 14｜（适用性声明）生成质量的提升不能替代基于执行的评测【论文声明】
- 原文出处：第 13 页 RQ1 答案；第 12 页末句；第 18 页 §8 末句。
- 原文引文："do not replace execution-based evaluation"（第 13 页）
- 成立条件：
  - 数据集/任务：CycleBench 301 任务。
  - 模型/实验规模：8 模型；数字支撑：CycleGen 执行率 83.31% 仍留 11.59pp 编译—执行差距（Table 5，第 12 页）。
  - 关键设置：同结论 2/6 的评测器与指标；硬件：原文未说明。
  - 假设/范围：作者据此主张逐扫描评测与行为反馈的必要性："These findings motivate scan-by-scan evaluation and behavioral feedback for generated PLC programs."（第 18 页）——这是作者的建议性主张。

### 结论 15｜剔除 Agents4PLC/AutoPLC 来源任务或超长场景任务后，编译—执行差距与 CycleGen 增益依然存在【实验支持】
- 原文出处：第 13 页 §6.1"Source and scenario-length sensitivity"。
- 原文引文："persist beyond these source groups"（第 13 页）
- 成立条件：
  - 数据集/任务：剔除 126 个 Agents4PLC/AutoPLC 来源任务后剩 175 任务：四基线差距 11.04pp、CycleGen 较 Direct +8.86pp；再剔除 6 个总扫描数 >1000 的任务：差距 11.33pp、增益 8.56pp（第 13 页）。
  - 模型/实验规模：同主实验（8 模型）。
  - 关键设置：同结论 2/6；硬件：原文未说明。
  - 假设/范围：仅排除这两类可疑来源/超长场景，不构成对其他分布的外推验证。

### 结论 16｜（适用性声明）模型生成的自测套件是易错信号：仅 54.35% 的有效套件全过参考绑定用例，突变检出率 73.33%【实验支持】
- 原文出处：第 16 页 §6.3"Self-test agreement and discrimination"（24 任务试点）；设计声明见第 8 页 §4.1。
- 原文引文："only 75/138 suites (54.35%)"（第 16 页）
- 成立条件：
  - 数据集/任务：24 个试点任务（按来源轮转与参考长度/静态特征分层选取，与候选成败无关）；192 个任务—模型套件槽。
  - 模型/实验规模：144 个套件通过有效性检查、46 个无效、2 个缺失；138 个可完整重复参考执行（第 16 页）。
  - 关键设置：原断言匹配 2,242/2,673 个绑定扫描（83.88%）；50 个单点突变、18 个任务、每任务至多 3 个；135 个稳定"套件—突变"对中 99 个拒识突变（73.33%；CI [51.04, 91.30]）；仅 43/192 原套件槽检出任一突变（第 16 页）；套件编制规则见第 11 页（≤6 用例等）；候选盲编写"controls information flow, not semantic independence"（第 8 页）；硬件：原文未说明。
  - 假设/范围：作者定位为"supporting process evidence rather than an additional module ablation"（第 16 页），并明言套件"does not turn model predictions into a correctness oracle"（第 8 页）。

### 结论 17｜（适用性声明）SemaPLC 重建结果仅是 GPT-4o 单模型过程证据，不构成八模型基线排名或完整复现【论文声明】
- 原文出处：第 13 页 §6.1"SemaPLC reconstruction and single-model scope"。
- 原文引文："single-model process evidence"（第 13 页）
- 成立条件：
  - 数据集/任务：301 任务；SemaPLC 发布的 agent 核心与原生验证器经接口适配器运行。
  - 模型/实验规模：仅 GPT-4o；κ=0/1/2 次失败驱动修复对应执行通过率 31.89%/45.85%/45.85%；κ=2 用 38.07M token，为该模型下 CycleGen 2.97M 的 12.82 倍（第 13 页）。
  - 关键设置：每任务预算上限 12 次调用、180,000 token、2 美元、1,200 秒（第 10 页）；原生交付接受 75 个目标、其中 6 个未过公共评测器；第二次修复 +6.80% token，救 3 个、害 3 个（第 13 页）；硬件：原文未说明。
  - 假设/范围：作者自述因预算与交付门差异，无法形成"directly comparable method condition"，故只作过程证据（第 13 页）。

### 结论 18｜（作者推测）泛化性与采样稳定性需要在独立任务与重复生成上进一步检验【作者推测】
- 原文出处：第 18 页 §7 Conclusion validity。
- 原文引文："needed to assess generalization"（第 18 页）
- 成立条件：
  - 数据集/任务：当前全部结果来自 CycleBench 这一个基准（"The CycleGen configuration was developed using this benchmark."，第 18 页）。
  - 模型/实验规模：8 部署 / 5 模型诊断子集；每条件每任务只评一个返回程序，五候选非独立工作流运行，"cannot estimate reliability@k or seed variance"（第 11 页）。
  - 关键设置：统计检验假设任务簇独立与符号可交换性，"related tasks may violate independence"；全部为"exploratory estimates on the evaluated task set"（第 11 页）；硬件：原文未说明。
  - 假设/范围：作者声明的待办：独立任务与重复生成；另提示基准衍生任务与 Qwen3-Coder-Next 的双重角色（场景编写方 + 被评模型）可能影响结果、训练暴露情况未知（第 18 页）。

## 二、依据不足（想下但原文找不到依据的说法）

1. "CycleGen 优于 Agents4PLC/LLM4PLC/AutoPLC/SemaPLC 这些已发表系统"。诱因：Table 5 中 CycleGen 超各基线 6.98–20.39pp。但原文明确说对比对象是公开材料适配版——"Results characterize these adaptations, not complete native reproductions."（第 10 页），SemaPLC 只是 GPT-4o 单模型重建（第 13 页）。对"原系统"的胜负判断无依据，故不列入结论。
2. "5 个候选是（等资源意义下的）最优生成预算"。诱因：Fig. 4 中 k=5 支配 k=6–8。但作者原话否认普遍性："this does not establish a generally optimal or equal-resource budget"（第 15 页），且只测到 k=8、成本只计 token（美元成本与延迟不计，第 15 页）。
3. "结论可迁移到其他 ST 方言、厂商工具链或物理 PLC 控制器"。原文反向声明："Fixed budgets, one runtime, and provider-specific reasoning limit transfer to other dialects and physical controllers"（第 18 页）；逻辑时间评测不保证物理时序（第 6 页）。无迁移证据。
4. "模型自测套件可作为正确性判据/验收门"。原文明确否定："it does not turn model predictions into a correctness oracle"（第 8 页）；试点显示仅 54.35% 套件全过参考、突变检出 73.33%（第 16 页）。
5. "评测不受训练数据污染影响"。原文只说"training exposure remains unknown"，且指出 Qwen3-Coder-Next 兼任场景编写方与被评模型可能影响结果（第 18 页）；任何"无污染"或"有污染"的断言都缺依据。

## 三、读者最容易过度泛化的两点

1. 把"编译—执行差距 11.92 个百分点"当成 LLM 生成 PLC 代码的普遍规律或固定量级。11.92pp 只是本基准 9,632 个基线结果的池化平均，量级高度依赖条件：按参考长度分组后"the compile–execution gap grows from 3.67 to 24.07 points"（第 7 页，Table 3）；Table 5 中各模型—方法组合的差距从 4.98 到 18.94pp 不等。作者也限定了外推边界："These analyses are exploratory estimates on the evaluated task set."（第 11 页）"Eight deployments cover 301 tasks... Source concentration and limited scenarios constrain diversity and coverage"（第 18 页）"Fixed budgets, one runtime, and provider-specific reasoning limit transfer to other dialects and physical controllers"（第 18 页）。基准内成立的是方向性结论（每个组合差距为正，第 12 页），量级不可外推。
2. 把"候选数超过 5 无收益"读成普遍最优预算结论（"5 个候选就够，多了纯属浪费"）。该结果只在冻结生成序前缀 k=1–8、以 token 为唯一成本、且配置在同一基准上调出的条件下观察到的：作者原话"Observed k = 5 dominates its k = 6–8 extensions; this does not establish a generally optimal or equal-resource budget."（第 15 页）；成本度量排除本地执行、美元与延迟（"local execution, dollar costs, and latency are outside this measure"，第 15 页）；且"The CycleGen configuration was developed using this benchmark."（第 18 页）。换模型、换任务分布或换等值预算口径，k=5 的优势未必保持。
