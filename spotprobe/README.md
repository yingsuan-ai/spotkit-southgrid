# SpotProbe · 南网五省现货电价探针（开源外壳）

读取南网五省区（滇黔桂粤琼）脱敏样本现货电价，计算每日加权均价、峰谷价差、极端价格事件，输出 SVG 走势图 + 统计 CSV + 控制台摘要。

## 用法

```bash
# 用自带样例（含 2026-10-13 区域暴涨典型事件）
python spotprobe.py --out ./out

# 自带样例 + 额外导出 PNG（需 matplotlib）
python spotprobe.py --out ./out --png

# 指定自定义电价 CSV
python spotprobe.py --data your_prices.csv --out ./out
```

输入 CSV 字段：`date,province,province_code,hour,price_yuan_kwh`

## 输出

- `spotprobe_stats.csv` — 逐日逐省 均价/峰/谷/峰谷差
- `spotprobe_chart.svg` — 每日加权均价多省折线图
- 控制台 — 极端价格事件（加权均价日环比 ≥ 15%）

## ⚠️ 数据边界

自带 `southgrid_sample_prices.csv` 为**脱敏教学样本**，由公开报道区间合成（含 10-13 区域日前加权均价单日涨约 20% 的典型事件），**不可用于真实结算**。真实电价以各省电力交易中心官方发布为准。本工具不含任何预测 / 优化 / 核销 / 分润闭源内核。
