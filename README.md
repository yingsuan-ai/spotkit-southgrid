# SpotKit-SouthGrid · 南网五省·用电侧决策开源工具箱

> 面向**南网五省区（滇黔桂粤琼）**用电侧的决策开源工具箱。开源**外壳四件套**做技术钩子，闭源**算法内核**（预测 / 约束优化 / 核销 / 分润）永不公开——目的是让你 clone 后能跑通、跑通后会惊艳、惊艳后想算**自己**的数据，自然转化到算电宝™。

[English abstract below](#english-abstract)

---

## 这是什么（Open-Core 边界）

| 层 | 内容 | 是否在本仓库 |
|----|------|--------------|
| **开源外壳** | SpotProbe 现货探针 · DeviationSim 偏差模拟 · BillParser 电费单解析 · PlantAudit 虚拟工厂体检 | ✅ 是（透明、可复现） |
| **闭源内核** | 现货/节点电价预测 · L2 约束优化调度 · 能耗台账与节省核销引擎(M&V) · 分润结算 | ❌ 否（属算电宝™，永不公开） |

本仓库的价值：**先把"用电侧决策"这件事讲清楚、跑起来、建立直觉**；真正的优化与核销，在算电宝™闭源内核里。

## 为什么开源（名 → 利 转化漏斗）

```
GitHub 技术控 clone / star
   ↓  跑通四件套 Demo，建立直觉（如 10.13 暴涨、峰段申报不足被罚）
   ↓  想用「自己」的负荷/账单/电价算一遍
   ↓  注册 算电宝™ 免费基础版（全年免费体检测算 · 数据不出本机）
   ↓  撞上免费版边界（前 3 项调峰指导 · 不导出完整报告）
   ↓  转化 标准版 ¥8,800/年（邀请码可减 800）或 售电双引擎
```

我们不靠"开源"变现，靠"开源把需求讲明白、把信任建立起来"。

## 快速开始

```bash
git clone https://github.com/yingsuan-ai/spotkit-southgrid.git
cd spotkit-southgrid

# 一键跑通四件套演示（仅标准库，无需安装任何依赖）
python run_demo.py

# 或单独运行
python spotprobe/spotprobe.py  --out ./out      # 现货探针
python deviationsim/deviationsim.py --demo --out ./out   # 偏差模拟
python billparser/billparser.py --out bill.json  # 电费单解析
python plantaudit/plantaudit.py --demo --out report.html # 工厂体检
```

产物写入 `./out` 或 `./demo_out`：`spotprobe_chart.svg`、`deviationsim_detail.csv`、`bill.json`、`plant_audit_report.html`。

## 四件套一览

| 工具 | 干什么 | 输入 | 输出 |
|------|--------|------|------|
| **SpotProbe** | 南网五省脱敏样本电价：加权均价 / 峰谷差 / 极端事件 | 电价 CSV | SVG 图 + 统计 CSV |
| **DeviationSim** | 偏差考核透明模拟（±5% 阈值 + 示意单价） | 实际/申报曲线 | 逐时明细 CSV |
| **BillParser** | 南网电费单 → 结构化 JSON | 账单文本 | JSON |
| **PlantAudit** | 虚拟工厂"用电健康度"四維体检 | 负荷曲线 + 档案 | 自包含 HTML 报告 |

## 年度观察（综合包一部分）

- 📄 [`annual_observation_2026/observation_2026.md`](annual_observation_2026/observation_2026.md) — 《2026 南网五省电力现货年度观察》
- 📊 [`annual_observation_2026/data/metrics_2026.csv`](annual_observation_2026/data/metrics_2026.csv) — 支撑指标数据集

> 数据截至 2026-11-12，由公开报道梳理，**请以官方发布为准**；本仓库自带样本为脱敏教学数据，不可用于结算。

## ⚠️ 红线与边界（务必阅读）

1. **南网五省区**：滇黔桂粤琼。云南是起点与验证场，不是终点。
2. **数据脱敏**：本仓库所有电价/负荷/账单样本均为**脱敏教学样本**，由公开区间合成，**不可用于真实结算**。
3. **不承诺降本**：开源工具只做展示/统计/教学，不构成任何保证、降本承诺或结算依据。
4. **内核不公开**：预测、约束优化、核销、分润等闭源内核**不在本仓库**，永不公开。
5. **免费全年无陷阱**：算电宝™免费基础版为**全年免费**体检测算、数据不出本机，不存在"21 天到期后收费"的设定。
6. **售电双引擎**：售电公司视角为「风险台（按年费）+ 白标席位（按户/年）」双引擎，与用电企业标准版是不同产品线。

## 转化入口

带着你自己的数据，进入算电宝™做完整诊断与优化（免费基础版·数据不出本机）：

👉 **https://yingsuan.top/power-advisor.html?utm_source=github&utm_medium=repo&utm_campaign=spotkit_southgrid**

## 目录结构

```
spotkit-southgrid/
├── README.md
├── LICENSE                      # MIT + 算法内核边界声明
├── requirements.txt             # 仅标准库；matplotlib 为可选
├── run_demo.py                  # 一键跑通四件套
├── spotprobe/                   # 现货探针
├── deviationsim/                # 偏差考核模拟
├── billparser/                  # 电费单解析
├── plantaudit/                  # 虚拟工厂体检
├── sample_data/                 # 脱敏样本（电价/负荷/申报/账单）
└── annual_observation_2026/     # 年度观察报告 + 数据集
```

## License

[MIT](LICENSE) · © 2026 云南盈菜通电子商务有限公司（盈算智服）

---

## English Abstract

**SpotKit-SouthGrid** is an open-source toolkit for the **Southern Grid five-provider region (Yunnan/Guizhou/Guangxi/Guangdong/Hainan)** electricity end-user decision-making. It ships four transparent, reproducible "open-shell" tools — SpotProbe (spot-price probe), DeviationSim (deviation penalty simulator), BillParser (bill parser), and PlantAudit (virtual-plant health audit) — bundled with a 2026 annual observation report & dataset. The proprietary kernels (price forecasting, constraint optimization, M&V settlement, revenue-share) live in the closed-source **算电宝™ (SuanDianBao)** product and are **never** included here. The repo works as a technical hook: clone → run demos → build intuition → bring your own data to the closed-source product. All bundled data is **synthetic/desensitized** and must not be used for real settlement.
