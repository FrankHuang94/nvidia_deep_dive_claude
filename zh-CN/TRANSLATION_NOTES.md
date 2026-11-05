# 译者说明（Translation notes）

本目录 `zh-CN/` 是英文资料库的**简体中文参考译文**，仅供参考；如与英文原文有任何出入，以英文原文为准。
This folder is a simplified-Chinese reference translation of the English repository. The English original prevails.

## 1. 翻译原则

- **忠实、专业、通顺**：采用半导体与投行研究报告的书面语体，意译为主，避免逐词直译；保留原文的结论、口径与语气（包括看空观点与不确定性）。
- **不改动事实**：所有数字、单位、日期、型号、引用编号原样保留（例如 `$96.2B`、`288 GB`、`19.2 TB/s`、`FY2026`、`[[S2031]](…)`），不做币种或单位换算。
- **专有名词**：产品名、代码、文件路径、URL、Mermaid 语法关键字保持英文；公司名首次出现用“中文（英文）”，之后用中文（见第 3 节）。
- **术语首次出现**：给出“中文（英文）”，例如“高带宽内存（HBM）”，此后可只用缩写。
- **链接**：保持 Markdown 链接目标与英文原文完全一致（构建脚本会自动改写路径）；只翻译链接文字。
- **图表**：SVG 图表本身保留英文；翻译 Markdown 中的替代文字（alt text），打印版会把它显示为中文图注。
- **Mermaid 图**：翻译可见标签与标题，保持语法正确；含中文或标点的节点标签放在 `["…"]` 引号中。
- **固定版式标题**（必须统一）：

| 英文 | 中文 |
|---|---|
| ⚡ The Executive Take | ⚡ 要点速览 |
| 🔧 Under the hood: … | 🔧 技术细节：… |
| Worked example — … | 算例 —— … |
| 🎯 Corp Dev Lens | 🎯 企业发展视角 |
| 📚 Sources | 📚 来源（Sources） |
| Myth vs. reality | 误区与事实 |
| 🐂 Bull view / 🐻 Bear view | 🐂 看多观点 / 🐻 看空观点 |
| 🟢 Confirmed / 🟡 Reported / 🔴 Speculative | 🟢 已确认 / 🟡 有报道 / 🔴 推测 |
| Est. | 估计 |
| 🟩 Leads / 🟨 Parity / 🟥 Behind / 🟦 Different approach | 🟩 领先 / 🟨 持平 / 🟥 落后 / 🟦 路线不同 |
| **[Q1 · Job & failure mode]** 等八个标准问题 | **[Q1 · 职能与失效后果]**、**[Q2 · 关键指标]**、**[Q3 · 代际进步]**、**[Q4 · 优势来源]**、**[Q5 · 最强挑战者]**、**[Q6 · 复制成本]**、**[Q7 · 路线图与变数]**、**[Q8 · 价值池与并购机会]** |

## 2. 术语表（统一译法）

| English | 中文 |
|---|---|
| scale-up / scale-out / scale-across | 纵向扩展 / 横向扩展 / 跨数据中心扩展（首次附英文） |
| die / package | 裸片（die）/ 封装 |
| reticle limit | 光罩尺寸极限 |
| tensor core / streaming multiprocessor (SM) | 张量核心 / 流式多处理器（SM） |
| HBM / LPDDR / GDDR | 高带宽内存（HBM）/ LPDDR / GDDR |
| advanced packaging / interposer / substrate | 先进封装 / 中介层 / 基板 |
| training / inference / prefill / decode | 训练 / 推理 / 预填充（prefill）/ 解码（decode） |
| token | token（词元）（首次），之后用 token |
| KV cache | KV 缓存 |
| throughput / latency / tail latency | 吞吐量 / 延迟 / 尾延迟 |
| interactivity (tokens/s per user) | 交互速度（每用户 tokens/s） |
| mixture of experts (MoE) | 混合专家模型（MoE） |
| all-reduce / all-gather / reduce-scatter / all-to-all | 全规约（all-reduce）/ 全收集（all-gather）/ 规约散射（reduce-scatter）/ 全交换（all-to-all） |
| switch / NIC / SuperNIC / DPU | 交换机 / 网卡（NIC）/ SuperNIC / 数据处理器（DPU） |
| co-packaged optics (CPO) / pluggable transceiver | 共封装光学（CPO）/ 可插拔光模块 |
| rack / compute tray / switch tray | 机架 / 计算托盘 / 交换托盘 |
| liquid cooling / power shelf / busbar | 液冷 / 电源架 / 母排 |
| AI factory | AI 工厂 |
| hyperscaler / neocloud / sovereign AI | 超大规模云厂商 / 新兴云服务商（neocloud）/ 主权 AI |
| custom ASIC / merchant silicon | 定制 ASIC / 商用芯片 |
| moat / flywheel / value pool | 护城河 / 飞轮 / 价值池 |
| gross margin / operating leverage | 毛利率 / 经营杠杆 |
| TCO | 总拥有成本（TCO） |
| capex / opex | 资本开支 / 运营开支 |
| purchase obligations / supply commitments | 采购义务 / 供应承诺 |
| acquihire / licensing deal / warrant | 收购式招聘（acquihire）/ 授权交易 / 认股权证 |
| circular financing | 循环融资 |
| bull case / bear case | 看多情景 / 看空情景 |
| export controls | 出口管制 |
| corp dev | 企业发展（corp dev） |
| build / buy / partner | 自建 / 收购 / 合作 |
| roadmap / gantt chart | 路线图 / 甘特图 |
| benchmark | 基准测试 |
| this repo / repo estimate | 本资料库 / 本资料库估计 |
| layer | 层（如“第 02 层”） |
| fiscal year (FY2026), Q2 FY2027 | 2026 财年（FY2026），之后可直接写 FY2026；Q2 FY2027 |

## 3. 公司与产品名

英伟达（NVIDIA）· AMD · 谷歌（Google）· 亚马逊 / AWS · 微软（Microsoft）· Meta · 博通（Broadcom）·
美满电子（Marvell）· 英特尔（Intel）· 高通（Qualcomm）· 华为 · 台积电（TSMC）· 三星 · SK 海力士 ·
美光（Micron）· 富士康 · 广达 · 纬创 · 甲骨文（Oracle）· OpenAI · Anthropic · xAI · CoreWeave · Arm ·
Mellanox · Cerebras · Groq · Hugging Face。产品名（Blackwell、Rubin、Vera、Grace、NVLink、Spectrum-X、
BlueField、ConnectX、CUDA、TPU、Trainium、Maia、MTIA、Ascend/昇腾、Instinct、Helios 等）保持英文（昇腾可写“昇腾（Ascend）”）。

## 4. 章节名称

| 编号 | 中文标题 |
|---|---|
| 00 | 执行摘要 |
| 01 | 英伟达的飞轮 |
| P1–P5 | AI 训练原理 · AI 推理原理 · 四大瓶颈 · 并行方式详解 · 芯片经济学入门 |
| 02 | GPU 芯片 |
| 03 | 内存、封装与供应链 |
| 04 | CPU（Grace、Vera） |
| 05 | 纵向扩展（NVLink、NVSwitch） |
| 06 | 横向扩展与跨数据中心网络 |
| 07 | DPU、SuperNIC、存储与安全 |
| 08 | 系统、机架与 AI 工厂 |
| 09 | CUDA 与系统软件 |
| 10 | 软件库（CUDA-X） |
| 11 | 推理与 AI 软件 |
| 12 | 编排与云服务 |
| 13 | 生态、市场进入与资本 |
| 14 | 训练与推理经济学 |
| 15 | 竞争格局 |
| 16 | 英伟达如何建成今日格局（时间线） |
| 17 | 路线图 2025–2028 |
| 18 | 弱点与看空情景 |
| 19 | 对高通的启示 |
| CS1–CS7 | Mellanox：最佳交易 · CUDA：十五年的赌注 · 谷歌 TPU：可信的替代方案 · AMD、OpenAI 与第二供应商 · DeepSeek 时刻与效率冲击 · 中国出口管制：H20 及之后 · 吉瓦级 AI 工厂：xAI、Stargate 等 |
| — | 速查表（Cheat sheet）· 术语表（Glossary） |

## 5. 补充译名（翻译过程中统一采用）

| English | 中文 |
|---|---|
| capacity backstop | 算力兜底承诺 |
| licence plus acquihire | 授权加收购式招聘 |
| capital-for-capacity | 以资本换产能 |
| non-marketable equity | 非流通股权 |
| Alchip / GUC / MediaTek | 世芯电子（Alchip）/ 创意电子（GUC）/ 联发科（MediaTek） |
| Cambricon / Hygon / Moore Threads / MetaX / Biren / T-Head / Kunlunxin | 寒武纪 / 海光 / 摩尔线程 / 沐曦 / 壁仞 / 平头哥 / 昆仑芯 |
| SMIC / CXMT / SoftBank | 中芯国际（SMIC）/ 长鑫存储（CXMT）/ 软银 |
| SuperPoD / SuperNode / UnifiedBus | 超节点 / 超节点 / 灵衢（UnifiedBus） |
| Cross-cutting chapter | 跨层专题（统一用语，不用“跨领域”或“横向专题”） |
| design win / tape-out / chiplet / known-good die | 设计导入 / 流片 / 芯粒 / 已知合格裸片（KGD） |
| dense / sparse | 稠密 / 稀疏 |
| earn-out | 或有对价（earn-out） |
| host CPU / superchip / cache coherence / attach | 主机 CPU / 超级芯片 / 缓存一致性 / 挂接 |
| royalty / architecture licence | 特许权使用费 / 架构授权 |
| agentic AI / reasoning model | 智能体 AI / 推理型模型（区别于 inference“推理”） |
| radix / rail-optimized / packet spraying / attach rate | 端口数 / 轨道优化 / 包喷洒 / 搭售率 |
| serving engine / disaggregated serving / goodput | 推理服务引擎 / 分离式服务 / 有效产出（goodput） |
| captive silicon / captive ASIC | 自用芯片 / 自用 ASIC |
| pull-through | 带动硬件销售（pull-through） |
| gang scheduling / GPU partitioning / take-or-pay / backlog | 成组调度 / GPU 切分 / 照付不议 / 收入积压 |
| equity-for-capacity / behind-the-meter / day-0 support | 以股权换产能 / 表后（behind-the-meter）/ 首日支持（day-0） |
| switching cost / compliant SKU | 转换成本 / 合规型号 |
| copper spine / NVLink spine | 铜缆背板 / NVLink 线缆背板 |
| optical circuit switch | 光路交换机 |
| steelman / verdict / signpost | 最强论证（steelman）/ 研判 / 路标 |
| roofline / ridge point / die harvesting | roofline / 脊点（ridge point）/ 裸片降级利用 |
| Innolight / Eoptolink / SPIL / Synopsys | 中际旭创 / 新易盛 / 矽品 / 新思科技 |

## 6. 标点约定

- 标题中的破折号统一用中文破折号“——”（如“第 02 层 —— GPU 芯片”“18 —— 弱点与看空情景”）；数字区间沿用英文短横“–”（如 2025–2028）。

## 7. 已知局限

- **桑基图（sankey）保留英文**：Mermaid 的 sankey 解析器只接受 ASCII 字符，因此执行摘要（00）、第 02 层、第 12 层与 CS7 中的四幅桑基图标签保留英文，图下中文说明给出对应译名。
- **数字写法**：多数译者保留原文的 `k` / `M` / `B` 记数（如 `100k GPU`、`$96.2B`）；少数页面在正文中改用“万 / 亿”。两种写法数值相同，以英文原文为准。
- **页内锚点**：中文标题的锚点与英文不同；指向其他页面某一小节的链接会退化为指向该页面开头。
- **图表**：SVG 图表为英文原图，打印版以中文图注（替代文字）说明。
