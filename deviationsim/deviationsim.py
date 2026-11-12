#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeviationSim · 偏差考核模拟器（开源外壳 · 透明规则）
=====================================================
给定「实际负荷曲线」与「申报曲线」，按公开的偏差考核
思路做**透明、可复现**的模拟测算，输出逐时偏差、越界
时段与模拟考核费。

⚠️ 重要边界说明（务必阅读）：
1. 本工具采用「±5% 免考核阈值 + 越界电量 × 模拟单价」的
   **示意规则**，仅用于教学与直觉建立。真实南方区域市场的
   偏差考核口径（免考核比例、考核电价、结算公式、考核权重）
   以各省电力交易中心最新规则与合同为准，本工具不构成任何
   合规或结算依据。
2. 模拟单价（--penalty-price，默认 0.40 元/kWh）为示意值，
   不代表任何真实考核电价。
3. 本仓库不含任何预测 / 优化 / 核销 / 分润等闭源内核
   （详见仓库 README 的 open-core 说明）。

用法：
  # 演示：用自带样例（实际负荷 vs 峰段申报不足）
  python deviationsim.py --demo

  # 自定义：提供实际与申报曲线 CSV
  python deviationsim.py --load load.csv --declare declare.csv
"""
import csv
import os
import sys
import argparse

DEFAULT_LOAD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data", "sample_load_yn.csv")
DEFAULT_DECLARE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data", "sample_declare_yn.csv")


def load_curve(path, col="load_kw"):
    arr = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            arr.append((int(r["hour"]), float(r[col])))
    arr.sort(key=lambda x: x[0])
    return [v for _, v in arr]


def simulate(actual, declared, tolerance=0.05, penalty_price=0.40):
    """逐时偏差模拟。返回明细列表与汇总。"""
    n = min(len(actual), len(declared))
    lines = []
    total_penalty = 0.0
    breached = 0
    for i in range(n):
        a = actual[i]
        d = declared[i]
        denom = d if d != 0 else 1.0
        dev_ratio = (a - d) / denom
        abs_r = abs(dev_ratio)
        if abs_r > tolerance:
            # 越界电量（kWh，以 1h 为步长） × 模拟单价
            excess = abs(a - d) * 1.0
            fee = excess * penalty_price
            total_penalty += fee
            breached += 1
            flag = "超发" if a > d else "欠发"
        else:
            excess = 0.0
            fee = 0.0
            flag = "免考核"
        lines.append({
            "hour": i, "actual": a, "declared": d,
            "dev_ratio": dev_ratio, "excess_kwh": excess,
            "fee": fee, "flag": flag,
        })
    summary = {
        "hours": n, "breached": breached,
        "total_penalty": total_penalty,
        "avg_dev_abs": sum(abs(l["dev_ratio"]) for l in lines) / n,
        "tolerance": tolerance, "penalty_price": penalty_price,
    }
    return lines, summary


def write_csv(lines, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["hour", "actual_kw", "declared_kw",
                    "dev_ratio", "excess_kwh", "fee_yuan", "flag"])
        for l in lines:
            w.writerow([l["hour"], round(l["actual"], 1), round(l["declared"], 1),
                        round(l["dev_ratio"], 4), round(l["excess_kwh"], 1),
                        round(l["fee"], 2), l["flag"]])


def main():
    ap = argparse.ArgumentParser(description="偏差考核模拟器（开源外壳·透明规则）")
    ap.add_argument("--demo", action="store_true", help="使用自带样例")
    ap.add_argument("--load", default=DEFAULT_LOAD, help="实际负荷 CSV")
    ap.add_argument("--declare", default=DEFAULT_DECLARE, help="申报曲线 CSV")
    ap.add_argument("--tolerance", type=float, default=0.05,
                    help="免考核阈值（默认 ±5%%）")
    ap.add_argument("--penalty-price", type=float, default=0.40,
                    help="模拟考核单价 元/kWh（示意值）")
    ap.add_argument("--out", default=".", help="输出目录")
    args = ap.parse_args()

    load_path = args.load if not args.demo else DEFAULT_LOAD
    decl_path = args.declare if not args.demo else DEFAULT_DECLARE
    if not os.path.exists(load_path) or not os.path.exists(decl_path):
        sys.exit("负荷或申报文件不存在，请用 --load/--declare 指定。")

    actual = load_curve(load_path, "load_kw")
    declared = load_curve(decl_path, "declare_kw")
    lines, s = simulate(actual, declared, args.tolerance, args.penalty_price)

    os.makedirs(args.out, exist_ok=True)
    write_csv(lines, os.path.join(args.out, "deviationsim_detail.csv"))

    print("=" * 56)
    print("DeviationSim · 偏差考核模拟器（示意规则）")
    print("=" * 56)
    print(f"免考核阈值      : ±{args.tolerance*100:.0f}%")
    print(f"模拟考核单价    : {args.penalty_price:.2f} 元/kWh（示意值）")
    print(f"测算时段        : {s['hours']} 小时")
    print(f"越界时段        : {s['breached']} 小时")
    print(f"平均绝对偏差率  : {s['avg_dev_abs']*100:.1f}%")
    print(f"模拟考核费合计  : {s['total_penalty']:.2f} 元")
    print("\n越界时段明细（前 12 条）：")
    shown = 0
    for l in lines:
        if l["flag"] != "免考核":
            print(f"  {l['hour']:02d}:00 实际 {l['actual']:.0f} / 申报 {l['declared']:.0f}  "
                  f"偏差 {l['dev_ratio']*100:+.1f}%  {l['flag']}  模拟费 {l['fee']:.2f}元")
            shown += 1
            if shown >= 12:
                break
    print(f"\n明细已写出: {os.path.join(args.out, 'deviationsim_detail.csv')}")
    print("\n⚠️ 以上为「±5% 阈值 + 示意单价」的透明模拟，非真实结算口径。")


if __name__ == "__main__":
    main()
