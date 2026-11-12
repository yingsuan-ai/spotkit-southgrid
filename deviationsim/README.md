# DeviationSim · 偏差考核模拟器（开源外壳）

给定「实际负荷曲线」与「申报曲线」，按透明的偏差考核思路做**可复现**的模拟测算，输出逐时偏差、越界时段与模拟考核费。

## 用法

```bash
# 演示：自带样例（峰段申报不足 18% 的典型错误）
python deviationsim.py --demo --out ./out

# 自定义：实际 vs 申报曲线
python deviationsim.py --load load.csv --declare declare.csv --out ./out

# 调整阈值与模拟单价（示意值）
python deviationsim.py --demo --tolerance 0.05 --penalty-price 0.40
```

输入 CSV 字段：`hour,load_kw`（实际）/ `hour,declare_kw`（申报）

## 输出

- `deviationsim_detail.csv` — 逐时 实际/申报/偏差率/越界电量/模拟费/标记

## ⚠️ 边界说明

本工具采用「±5% 免考核阈值 + 越界电量 × 模拟单价」的**示意规则**，仅用于建立直觉。真实南方区域市场的偏差考核口径（免考核比例、考核电价、结算公式、考核权重）以各省电力交易中心最新规则与合同为准，**本工具不构成任何合规或结算依据，模拟单价亦为示意值，不代表真实考核电价**。不含任何闭源内核。
