我已完整读取论文解析文本（共 214 行，覆盖摘要、正文第 1–18 页与参考文献）。以下是按你要求的结构化结论提取。

---

# 论文结论提取

**论文**：*Compilation Is Not Correctness: Scan-by-Scan Evaluation of LLM-Generated PLC Programs*（Chen et al., 2610.28675v1）

## 一、主要结论清单

### 结论 1：编译通过 ≠ 行为正确（核心发现）
在 8 个模型 × 4 个基线方法的 9,632 个结果上，可编译率 83.99%、执行通过率 72.07%，相差 11.92 个百分点，且该差距出现在每一个模型—方法组合（含编译率超 99% 的组合）。差距随参考代码长度扩大（最短组 3.67 点 → 最长组 24.07 点，Table 3）。

- **出处**：摘要（第 1 页）；第 6.1 节 RQ1（第 12 页）；表 5；表 3（第 7 页）。
- **引文**："83.99% yield compilable programs and 72.07% pass the complete execution criterion, a difference of 11.92 percentage points"[^1]
- **成立条件**：
  - 数据集/任务：CycleBench，301 个 ST 任务（287 功能块 + 14 程序），684 场景、61,424 次扫描；公开规格 + 隐藏参考程序；参考源自 6 条渠道（Broad/Curated GitHub、AutoPLC 库、Agents4PLC、Matiec/OpenPLC 示例）。
  - 模型/规模：8 个模型部署（GPT-5.5、GPT-4o、Claude Sonnet 4、Claude Haiku 4.5、GLM-5.2、Qwen3-Coder-Next、MiniMax-M2.5、Qwen3.6-27B）；9,632 = 8 × 4 × 301。
  - 关键设置：硬件：原文未说明；运行时 Matiec iec2c + GCC，逻辑时间（非物理时间）；逐扫描"类型+数值"精确相等；初始生成 temperature 0.7、输出上限 16,384 token；基线 = Direct + 三个改编版（省略形式化验证）；指标 = 可编译率、执行通过率、二者之差（gap 含编译后所有失败阶段）。
  - 假设/适用范围：结果对模型等权平均；逐模型差异为描述性；作者声明"结果刻画的是改编版而非完整原生复现"。
- **标签**：【论文声明】【实验支持】

### 结论 2：抽样观察粒度会掩盖行为错误
对 5 个模型的 157 个 Direct 行为失败固定轨迹，每 2/5/10 次扫描检查分别漏检 11/34/47 个（7.01%/21.66%/29.94%）；仅看末次扫描漏检 98 个（62.42%），表观通过率升至 86.05%。

- **出处**：第 6.4 节 RQ4（第 16–17 页）；图 6；摘要/结论（第 18 页）。
- **引文**："Checking every second, fifth, or tenth scan misses 11, 34, or 47 of 157 behavioral failures (7.01%, 21.66%, and 29.94%)"
- **成立条件**：
  - 数据集/任务：同一 CycleBench；157 个 Direct 行为失败（来自 GPT-5.5、GPT-4o、Claude Sonnet 4、Claude Haiku 4.5、GLM-5.2 五模型）。
  - 规模：1,505 个 Direct 结果；只改观察位置，程序/输入/输出集/解码相等判定固定。
  - 关键设置：stride ∈ {2,5,10} 与"仅末次扫描"；每场景首末扫描始终保留；硬件：原文未说明。
  - 假设/适用范围：漏检 = 逐扫描可检出而粗粒度策略检不出的分歧；作者声明"比较用同一完整轨迹，仅观察位置改变"。
- **标签**：【论文声明】【实验支持】

### 结论 3：失败多为"瞬时分歧后被掩盖"
144/157 个失败在场景内出现输出重新一致（含全部 98 个末次扫描漏检）；其中 115/157 个失败的失配不超过连续 5 次扫描。

- **出处**：第 6.4 节（第 17 页）；图 1、图 5、图 6。
- **引文**："144/157 failures exhibit within-scenario output re-agreement ... including all 98 final-scan misses"
- **成立条件**：
  - 数据集/任务：同上 157 个失败，按任务/模型/候选哈希关联审核标签。
  - 关键设置：场景内"重新一致"定义明确；跨场景复位不计入重新一致；作者声明"可见一致不建立内部状态等价"；硬件：原文未说明。
- **标签**：【实验支持】

### 结论 4：失败类别分布
Direct 编译失败中 malformed 语句 + 声明合计 53.42%；行为失败中输出更新（27.4%）、算术/边界（22.3%）、时序/调用顺序（15.9%）合计 65.6%。

- **出处**：第 6.2 节 RQ2（第 13–14 页）；表 6。
- **引文**："Public-output updates (43, 27.4%), arithmetic or boundary logic (35, 22.3%), and timing or call order (25, 15.9%) together account for 65.6%"
- **成立条件**：
  - 数据集/任务：RQ2 诊断子集，5 模型，6,020 基线结果、1,505 Direct 结果；146 个编译失败（取首个诊断）、157 个行为失败（各一主类）。
  - 关键设置：人工标注（1 名评审主类 + 第 2 名盲审 40 例；一致率 82.5%、Cohen's κ=0.78）；作者声明这些是"症状而非确立的根因"；3 个数值案例与 154 个实现错误分开；硬件：原文未说明。
- **标签**：【实验支持】

### 结论 5：CycleGen 提升执行通过率
Direct 74.63% → CycleGen 83.31%（+8.68 点），并超过改编版 Agents4PLC（76.33%）、LLM4PLC（74.42%）、AutoPLC（62.92%）；对 Direct 的 95% 任务簇自举区间 [7.23, 10.22] 点。

- **出处**：第 6.1 节（第 12–13 页）；表 5；摘要/结论（第 18 页）。
- **引文**："CycleGen reaches 83.31%, exceeding Direct by 8.68 points, adapted Agents4PLC by 6.98 points"
- **成立条件**：
  - 数据集/任务：CycleBench 301 任务 × 8 模型；2,408 个 CycleGen 结果。
  - 方法设置：k=5 候选、编译修复（每候选 ≤1 次）、运行自测 + 选择门；测试在独立上下文先行生成并对代码生成隐藏；参考/场景隐藏；预算 = 1 次测试创作 + ≤1 次套件修订 + k 次生成 + ≤k 次修复。
  - 关键设置：硬件原文未说明；初始生成 temperature 0.7，测试/修复 0；自测套件 ≤6 用例、每例 ≤10 扫描、总 ≤40 扫描；最终逐扫描严格相等评测。
  - 假设/适用范围：端到端比较含推理预算差异（非等资源）；"逐模型差异为描述性"；CycleGen 以 Direct 返回程序作为第 1 个候选。
- **标签**：【论文声明】【实验支持】

### 结论 6：模块消融的各自贡献
多候选（5 个未修复首合格选择）达 79.94%（较 Direct +5.32 点）；在受控池上 Compile-Fix 贡献 +2.28 点、Self-Test + 选择门贡献 +1.62 点。

- **出处**：第 6.3 节 RQ3（第 14–15 页）；表 7。
- **引文**："Compile-Fix adds 2.28 points ... while Self-Test and Selection Gate add 1.62 points with repair fixed"
- **成立条件**：
  - 数据集/任务：CycleBench，2,408 任务—模型对；复用同一 5 个初始候选、同一自测套件。
  - 关键设置：配置 = Direct(k=1)/多候选(k=5)/Self-test only/Repair only/CycleGen；指标 = 可编译率、执行通过率、平均 token；硬件原文未说明。
  - 假设/适用范围：作者声明"这些探索性比较固定池与所述控制，而非总推理资源"；Self-Test 与选择门联合评估，二者个体效应未单独识别。
- **标签**：【实验支持】

### 结论 7：候选数收益递减
k=5 后执行通过率不再提升；k 扩到 8 token 增加 38.8%，却丢失 4 个通过（−0.17 点）。

- **出处**：第 6.3 节（第 15 页）；图 4；摘要/结论（第 18 页）。
- **引文**："Extending to k = 8 raises tokens to 25,256.6 (+38.8%) but loses four selected passes (0.17 points)"
- **成立条件**：
  - 数据集/任务：CycleBench 301 任务 × 8 模型；有序前缀 k=1..8。
  - 关键设置：k=5 平均 7 次调用、18,197 token；Direct 1 次调用、1,929 token；硬件原文未说明。
  - 假设/适用范围：作者明确"这不建立普遍最优或等资源预算"；k=1（修复）已含 Compile-Fix，与 Direct 不同。
- **标签**：【论文声明】【实验支持】

### 结论 8：CycleBench 为首个逐扫描行为基准（贡献声明）
据作者所知，这是首个对 LLM 生成 ST 做逐扫描行为评测、对照隐藏参考的基准。

- **出处**：贡献列表（第 3 页）；第 3 节（第 4–7 页）；表 1、表 2。
- **引文**："To our knowledge, the first benchmark for LLM-based Structured Text generation with comprehensive per-scan behavioral evaluation against hidden references"
- **成立条件**：
  - 任务规模：301 任务、684 场景、61,424 扫描；90 个来自 Agents4PLC。
  - 构建设置：6 条收集渠道；两名 PLC 工程师联合评审；参考执行生成期望输出。
  - 假设/适用范围："To our knowledge" 是作者声明而非独立验证；作者声明循环/定时器/边沿等语法特征"不建立语义覆盖"。
- **标签**：【论文声明】

### 结论 9：自测信号本身可错
试点中 138 个可重复套件仅 83.88% 断言匹配、54.35% 套件接受全部绑定用例；突变检测率 73.33%。

- **出处**：第 6.3 节（第 16 页）。
- **引文**："original assertions match 2,242/2,673 binding scans (83.88%) but accept all binding cases in only 75/138 suites (54.35%)"
- **成立条件**：
  - 数据集/任务：独立 24 任务试点，192 个任务—模型套件槽；144 个有效套件、138 个可重复参考执行。
  - 关键设置：50 处单点突变、18 任务；检测要求同一套件接受参考且拒绝突变体；作者声明这是"支持性过程证据而非额外模块消融"；硬件原文未说明。
- **标签**：【实验支持】

### 结论 10：基线保真限定（方法适用性声明）
三项基线（Agents4PLC、LLM4PLC、AutoPLC）的结果表征"改编版"而非完整原生系统；它们保留了编译反馈修复但省略了形式化验证环节。

- **出处**：第 5 节（第 10 页）；第 7 节 Threats（第 18 页）；表 4。
- **引文**："Results characterize these adaptations, not complete native reproductions"
- **成立条件**：Agents4PLC 用公开 TF-IDF 重建检索、不运行 PLCverif/nuXmv；LLM4PLC 不重建 SMV/plant-model 循环与 LoRA；AutoPLC 将 CODESYS 重定向到 Matiec、AutoLearn 禁用；SemaPLC 仅以 GPT-4o 单模型作过程证据。
- **标签**：【论文声明】

### 结论 11：执行通过 ≠ 完整正确/安全（评测口径限定）
通过只意味着在所给有限场景上与参考逐扫描一致，而非完整功能正确、终止性或物理安全；逻辑时间不等于物理时间。

- **出处**：第 3.2 节（第 6 页）；第 7 节 Construct validity（第 18 页）。
- **引文**："Passing establishes agreement on the supplied finite scenarios ... rather than complete functional correctness, termination, or physical safety"
- **成立条件**：前提是参考程序有效；不覆盖未运行的输入、物理行为与终止性；逻辑时间按调度推进，"物理时序保证需另行测量"。
- **标签**：【论文声明】

### 结论 12：对领域的展望/动机（作者推测）
这些发现促使采用逐扫描评测与行为反馈来评估与生成 PLC 程序。

- **出处**：第 8 节结论（第 18 页）。
- **引文**："These findings motivate scan-by-scan evaluation and behavioral feedback for generated PLC programs"
- **成立条件**：这是基于上述实验的展望性建议，非新增实验；原文未给出具体未来工作条款。
- **标签**：【作者推测】

---

## 二、依据不足（想写但不能写进结论清单）

1. **"CycleGen 的增益对保留形式化验证的完整原生基线同样成立"**——想这么说是因为读者自然会追问"它是否真的打败了原生 LLM4PLC/Agents4PLC"；但原文只测了省略形式化验证的改编版，SemaPLC 也仅单模型（GPT-4o）作"过程证据"，明确称"不能形成可直接比较的方法条件"，因此该说法原文无据。

2. **"执行通过率高就意味着程序安全、可上线运行"**——想这么说是因为"执行通过率"听起来像质量结论；但原文明确相反：通过只是有限场景上的一致，不等价于功能正确、终止或物理安全。

3. **"11.92 pp / 21.66% 可外推到其他 ST 方言、真实 PLC 硬件或一般代码生成"**——想这么说是因为这是全篇最醒目的数字；但原文外部效度部分明确限定"固定预算、单一运行时、供应商特定推理限制了向其他方言与物理控制器的迁移"。

4. **"CycleGen 的测试与代码在语义上独立，因此选择信号可靠"**——想这么说是因为它"测试先于代码、且对生成隐藏"；但原文声明候选盲只"控制信息流，而非语义独立"，共享模型与规格仍可产生共同误解。

5. **"CycleGen 是全局最优方法 / 等资源下最优"**——想这么说是因为它超过了所有基线；但原文声明 k 的收益"不建立普遍最优或等资源预算"，且"CycleGen 配置是在本基准上开发的"。

---

## 三、读者最容易过度泛化的两点

**第一点：把"编译≠正确"和 11.92 pp / 21.66% 的具体差距外推到真实 PLC 硬件、其他 ST 方言乃至一般 LLM 代码生成。**
这是全文标题级发现，极易被当作普适结论。但原文明确：该差距是在单一运行时（Matiec + GCC）、逻辑时间、逐扫描精确相等判定的特定基准与 8 个 2026 年 9 月模型部署上测得，且"通过"并不等于功能正确或物理安全。原文自述："Fixed budgets, one runtime, and provider-specific reasoning limit transfer to other dialects and physical controllers"；"Passing establishes agreement on the supplied finite scenarios ... rather than complete functional correctness, termination, or physical safety"。

**第二点：把 CycleGen 的 +8.68 点、"超过所有基线"读成"CycleGen 就是最优方法、可替代原生验证系统"。**
基线是省略了形式化验证的改编版，且 CycleGen 正是在本基准上开发调参、逐模型差异本身是描述性的，推理预算也未对齐。因此其优势不能外推为对原生系统或对真实部署的全面领先。原文自述："Results characterize these adaptations, not complete native reproductions"；"The CycleGen configuration was developed using this benchmark"；"Per-model differences are descriptive"。

（可补充的第三处易被误读——"执行通过率≈正确性/安全性"——已并入第一点的解释；原文在构建效度部分同样明确否定。）

---

[^1]: Compilation Is Not Correctness: Scan-by-Scan Evaluation of LLM-Generated PLC Programs