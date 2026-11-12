#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpotProbe · 南网五省现货电价探针（开源外壳 · 脱敏样本）
===================================================
读取南网五省区（滇黔桂粤琼）脱敏样本现货电价 CSV，
计算每日加权均价、峰谷价差、极端价格事件，并输出
SVG 走势图 + 统计 CSV + 控制台摘要。

⚠️ 数据说明：本工具自带 sample_data/southgrid_sample_prices.csv 为
「脱敏教学样本」，由公开报道的区间范围合成（含 2026-10-13 区域
日前加权均价单日涨约 20% 的典型事件），**不可用于真实结算**。
真实电价请以各省电力交易中心官方发布为准。

算法内核边界：本仓库只做「展示 / 统计 / 教学」，不含任何
预测、优化、核销、分润等闭源内核（详见仓库 README 的 open-core 说明）。
"""
import csv
import os
import sys
import argparse
from collections import defaultdict

DEFAULT_DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data", "southgrid_sample_prices.csv")

HOURS = list(range(24))


def load_prices(path):
    """返回 {date: {province: [24个float]}} 与省份顺序。"""
    table = defaultdict(lambda: defaultdict(list))
    provinces = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = r["date"]
            p = r["province"]
            h = int(r["hour"])
            v = float(r["price_yuan_kwh"])
            if p not in provinces:
                provinces.append(p)
            table[d][p].append((h, v))
    for d in table:
        for p in table[d]:
            table[d][p].sort(key=lambda x: x[0])
            table[d][p] = [v for _, v in table[d][p]]
    return table, provinces


def daily_stats(table):
    """逐日逐省：加权均价 / 峰价 / 谷价 / 峰谷价差。"""
    stats = defaultdict(dict)
    for d, pmap in table.items():
        for p, arr in pmap.items():
            avg = sum(arr) / len(arr)
            peak = max(arr)
            valley = min(arr)
            stats[d][p] = {
                "avg": avg, "peak": peak, "valley": valley,
                "spread": peak - valley,
            }
    return stats


def detect_extremes(stats):
    """跨日环比：某省某日加权均价较前一日变动 > 阈值 即记为极端事件。"""
    dates = sorted(stats.keys())
    events = []
    prev = {}
    for d in dates:
        for p, s in stats[d].items():
            if p in prev:
                base = prev[p]["avg"]
                chg = (s["avg"] - base) / base if base else 0.0
                if abs(chg) >= 0.15:
                    events.append({
                        "date": d, "province": p,
                        "prev_avg": base, "avg": s["avg"],
                        "change_pct": chg * 100.0,
                    })
        prev = stats[d]
    return events


def write_stats_csv(stats, provinces, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "province", "avg_yuan_kwh",
                    "peak_yuan_kwh", "valley_yuan_kwh", "spread_yuan_kwh"])
        for d in sorted(stats.keys()):
            for p in provinces:
                if p in stats[d]:
                    s = stats[d][p]
                    w.writerow([d, p, round(s["avg"], 4),
                                round(s["peak"], 4), round(s["valley"], 4),
                                round(s["spread"], 4)])


def build_svg(table, provinces, out_path):
    """生成每日加权均价多省折线 SVG（纯手写，无第三方依赖）。"""
    dates = sorted(table.keys())
    W, H = 900, 420
    pad_l, pad_r, pad_t, pad_b = 60, 20, 30, 40
    plot_w = W - pad_l - pad_r
    plot_h = H - pad_t - pad_b
    allvals = [v for d in dates for p in provinces
               for v in table[d].get(p, [0])]
    ymax = max(allvals) * 1.1 or 1.0
    ymin = 0.0
    xstep = plot_w / max(1, len(dates) - 1)
    y = lambda v: pad_t + plot_h * (1 - (v - ymin) / (ymax - ymin))
    x = lambda i: pad_l + xstep * i
    colors = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'font-family="sans-serif" font-size="12">']
    parts.append(f'<rect width="{W}" height="{H}" fill="#fff"/>')
    # y 轴网格
    for g in range(0, 6):
        gv = ymin + (ymax - ymin) * g / 5
        gy = y(gv)
        parts.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{W-pad_r}" y2="{gy:.1f}" '
                     f'stroke="#eee"/><text x="{pad_l-6}" y="{gy+4:.1f}" '
                     f'text-anchor="end" fill="#888">{gv:.2f}</text>')
    # 折线
    for i, p in enumerate(provinces):
        pts = []
        for j, d in enumerate(dates):
            arr = table[d].get(p)
            if not arr:
                continue
            avg = sum(arr) / len(arr)
            pts.append(f"{x(j):.1f},{y(avg):.1f}")
        col = colors[i % len(colors)]
        parts.append(f'<polyline fill="none" stroke="{col}" stroke-width="2" '
                     f'points="{" ".join(pts)}"/>')
        # 图例
        lx = pad_l + 10 + (i % 3) * 220
        ly = H - 14 - (i // 3) * 16
        parts.append(f'<rect x="{lx}" y="{ly-9}" width="10" height="10" fill="{col}"/>'
                     f'<text x="{lx+14}" y="{ly}" fill="#333">{p}</text>')
    # x 轴标签
    for j, d in enumerate(dates):
        parts.append(f'<text x="{x(j):.1f}" y="{H-pad_b+18}" text-anchor="middle" '
                     f'fill="#666">{d[5:]}</text>')
    parts.append(f'<text x="{pad_l}" y="16" fill="#333">每日加权均价（元/kWh，脱敏样本）</text>')
    parts.append('</svg>')
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def try_png(table, provinces, out_path):
    """可选：若环境装有 matplotlib 则额外导出 PNG。失败不影响主流程。"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    dates = sorted(table.keys())
    plt.figure(figsize=(9, 4.2))
    for p in provinces:
        avgs = []
        for d in dates:
            arr = table[d].get(p)
            avgs.append(sum(arr) / len(arr) if arr else 0)
        plt.plot(dates, avgs, marker="o", label=p)
    plt.title("南网五省区每日加权均价（脱敏样本）")
    plt.ylabel("元/kWh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    return True


def main():
    ap = argparse.ArgumentParser(description="南网五省现货电价探针（开源外壳·脱敏样本）")
    ap.add_argument("--data", default=DEFAULT_DATA, help="电价 CSV 路径")
    ap.add_argument("--out", default=".", help="输出目录")
    ap.add_argument("--png", action="store_true", help="尝试额外导出 PNG（需 matplotlib）")
    args = ap.parse_args()

    if not os.path.exists(args.data):
        sys.exit(f"数据文件不存在: {args.data}")
    os.makedirs(args.out, exist_ok=True)

    table, provinces = load_prices(args.data)
    stats = daily_stats(table)
    events = detect_extremes(stats)

    write_stats_csv(stats, provinces, os.path.join(args.out, "spotprobe_stats.csv"))
    build_svg(table, provinces, os.path.join(args.out, "spotprobe_chart.svg"))
    if args.png:
        try_png(table, provinces, os.path.join(args.out, "spotprobe_chart.png"))

    print("=" * 56)
    print("SpotProbe · 南网五省现货电价探针（脱敏样本）")
    print("=" * 56)
    for d in sorted(stats.keys()):
        print(f"\n📅 {d}")
        for p in provinces:
            if p in stats[d]:
                s = stats[d][p]
                print(f"  {p:<4} 均价 {s['avg']:.3f}  峰 {s['peak']:.3f}  "
                      f"谷 {s['valley']:.3f}  峰谷差 {s['spread']:.3f} 元/kWh")
    if events:
        print("\n⚠️  极端价格事件（加权均价日环比 ≥ 15%）：")
        for e in events:
            print(f"  {e['date']} {e['province']:<4}  "
                  f"{e['prev_avg']:.3f} → {e['avg']:.3f}  "
                  f"({'+' if e['change_pct']>=0 else ''}{e['change_pct']:.1f}%)")
    else:
        print("\n（样本窗口内未触发极端事件阈值）")
    print("\n输出：")
    print(f"  - {os.path.join(args.out, 'spotprobe_stats.csv')}")
    print(f"  - {os.path.join(args.out, 'spotprobe_chart.svg')}")
    print("\n⚠️ 本结果为脱敏教学样本，不可用于真实结算。")


if __name__ == "__main__":
    main()
