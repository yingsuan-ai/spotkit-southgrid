#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlantAudit · 虚拟工厂用电体检（开源外壳 · 透明评分）
====================================================
输入负荷曲线 + 基础档案（变压器容量 / 行业 / 省份），
对「负荷率 / 需量压力 / 峰段占比 / 负荷波动」四个维度做
透明评分，生成一份自包含的 HTML「工厂用电健康度」报告。

⚠️ 边界说明：
1. 评分公式完全透明、可复现，用于建立直觉；它与算电宝™
   闭源内核（L2 约束优化、核销引擎、分润结算）无关，也不
   构成任何降本承诺。真实诊断请以算电宝专业版为准。
2. 本工具为开源免费体验的「镜像」，免费基础版用户可在
   https://yingsuan.top/power-advisor.html 上传自有数据、
   数据不出本机地获得更完整的体检与调峰指导。

用法：
  python plantaudit.py --demo
  python plantaudit.py --load load.csv --capacity 1000 --name "示例工厂" --province 云南
"""
import csv
import os
import sys
import math
import argparse
from datetime import datetime

DEFAULT_LOAD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data", "sample_load_yn.csv")

PEAK_HOURS = {9, 10, 11, 14, 15, 16, 17, 19, 20, 21}


def load_curve(path):
    arr = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            arr.append((int(r["hour"]), float(r["load_kw"])))
    arr.sort(key=lambda x: x[0])
    return [v for _, v in arr]


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def score(load, capacity):
    n = len(load)
    energy = sum(load)                 # kWh（1h 步长）
    peak = max(load)
    mean = energy / n
    var = sum((x - mean) ** 2 for x in load) / n
    std = math.sqrt(var)
    cv = std / mean if mean else 0.0

    load_factor = energy / (peak * n) if peak else 0.0
    demand_pressure = peak / capacity if capacity else 1.0
    peak_energy = sum(load[h] for h in PEAK_HOURS if h < n)
    peak_ratio = peak_energy / energy if energy else 0.0

    s_lf = clamp(load_factor / 0.70 * 100)
    s_dp = clamp(100 - max(0, (demand_pressure - 0.60)) / 0.40 * 100)
    s_pk = clamp(100 - peak_ratio * 100 * 1.15)
    s_var = clamp(100 - cv * 100)

    overall = 0.30 * s_lf + 0.25 * s_dp + 0.25 * s_pk + 0.20 * s_var

    dims = [
        ("负荷率", s_lf, f"{load_factor*100:.1f}%", "越高越省（目标≥60%）"),
        ("需量压力", s_dp, f"{demand_pressure*100:.0f}% 峰值/容量",
         "逼近容量上限有需量电费风险"),
        ("峰段占比", s_pk, f"{peak_ratio*100:.0f}%", "峰段用电越多越贵"),
        ("负荷波动", s_var, f"变异系数 {cv:.2f}", "波动越大偏差考核风险越高"),
    ]
    return {
        "load_factor": load_factor, "demand_pressure": demand_pressure,
        "peak_ratio": peak_ratio, "cv": cv,
        "scores": {"负荷率": s_lf, "需量压力": s_dp,
                   "峰段占比": s_pk, "负荷波动": s_var},
        "overall": overall, "dims": dims,
        "energy": energy, "peak": peak, "mean": mean,
    }


def suggestions(r):
    tips = []
    if r["scores"]["负荷率"] < 70:
        tips.append("负荷率偏低：可通过将部分可转移负荷（如储能充电、非连续生产）"
                    "从谷段前移至深夜，抬升平均负荷、摊薄需量。")
    if r["scores"]["需量压力"] < 70:
        tips.append("峰值逼近变压器容量：关注需量电费，考虑需量管理或容改需。")
    if r["scores"]["峰段占比"] < 70:
        tips.append("峰段用电占比偏高：存在峰→谷/平转移空间，可评估储能或生产排程优化。")
    if r["scores"]["负荷波动"] < 70:
        tips.append("日负荷波动大：申报偏差考核风险较高，建议加强负荷预测与曲线平滑。")
    if not tips:
        tips.append("四项指标良好，维持当前运行并持续监测即可。")
    return tips


def build_html(r, name, province, capacity, out_path):
    tips = suggestions(r)
    bars = "".join(
        f'<div class="row"><span class="lab">{d[0]}</span>'
        f'<div class="bar"><div class="fill" style="width:{d[1]:.0f}%"></div>'
        f'</div><span class="val">{d[1]:.0f}</span></div>'
        for d in r["dims"])
    tip_html = "".join(f"<li>{t}</li>" for t in tips)
    overall = r["overall"]
    grade = ("优秀" if overall >= 85 else "良好" if overall >= 70
             else "关注" if overall >= 55 else "预警")
    html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>工厂用电健康度 · {name}</title>
<style>
 body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
   max-width:760px;margin:24px auto;padding:0 16px;color:#1f2937;background:#f7f8fa}}
 .card{{background:#fff;border-radius:12px;padding:20px 24px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:16px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#6b7280;font-size:13px}}
 .score{{font-size:46px;font-weight:700;color:#0f766e}}
 .grade{{display:inline-block;padding:2px 10px;border-radius:999px;background:#0f766e;color:#fff;font-size:13px}}
 .row{{display:flex;align-items:center;margin:8px 0}}
 .lab{{width:72px;font-size:13px;color:#374151}}
 .bar{{flex:1;height:12px;background:#eef2f7;border-radius:6px;overflow:hidden;margin:0 10px}}
 .fill{{height:100%;background:linear-gradient(90deg,#14b8a6,#0ea5e9)}}
 .val{{width:34px;text-align:right;font-size:13px;color:#374151}}
 table{{width:100%;border-collapse:collapse;font-size:13px}}
 td,th{{padding:6px 8px;border-bottom:1px solid #eef2f7;text-align:left}}
 li{{margin:6px 0;line-height:1.5}}
 .foot{{font-size:12px;color:#9ca3af;line-height:1.6}}
 a{{color:#0ea5e9}}
</style></head><body>
<div class="card">
 <h1>工厂用电健康度体检</h1>
 <div class="sub">{name} · {province} · 变压器容量 {capacity} kVA · 生成于 {datetime.now():%Y-%m-%d}</div>
 <p><span class="score">{overall:.0f}</span> <span class="grade">{grade}</span></p>
 <div>{bars}</div>
</div>
<div class="card">
 <h3 style="margin-top:0">关键指标</h3>
 <table>
  <tr><th>日用电量</th><td>{r['energy']:.0f} kWh</td></tr>
  <tr><th>峰值负荷</th><td>{r['peak']:.0f} kW</td></tr>
  <tr><th>负荷率</th><td>{r['load_factor']*100:.1f}%</td></tr>
  <tr><th>峰段电量占比</th><td>{r['peak_ratio']*100:.0f}%</td></tr>
  <tr><th>负荷变异系数</th><td>{r['cv']:.2f}</td></tr>
 </table>
</div>
<div class="card">
 <h3 style="margin-top:0">优化建议（教学示意）</h3>
 <ul>{tip_html}</ul>
</div>
<div class="card foot">
 <p>⚠️ 本报告由 SpotKit-SouthGrid（开源外壳）生成，评分透明可复现，仅用于建立直觉，
 不构成任何降本承诺或结算依据，亦不含算电宝™闭源内核。</p>
 <p>想要对你<b>自己</b>的数据做完整体检与调峰指导？免费基础版数据不出本机：
 <a href="https://yingsuan.top/power-advisor.html?utm_source=github&utm_medium=repo&utm_campaign=spotkit_southgrid">yingsuan.top/power-advisor.html</a></p>
</div></body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description="虚拟工厂用电体检（开源外壳·透明评分）")
    ap.add_argument("--demo", action="store_true", help="使用自带样例")
    ap.add_argument("--load", default=DEFAULT_LOAD, help="负荷曲线 CSV")
    ap.add_argument("--capacity", type=float, default=1000, help="变压器容量 kVA")
    ap.add_argument("--name", default="示例工厂", help="工厂名称")
    ap.add_argument("--province", default="云南", help="省份")
    ap.add_argument("--out", default="plant_audit_report.html", help="输出 HTML")
    args = ap.parse_args()

    load_path = args.load if not args.demo else DEFAULT_LOAD
    if not os.path.exists(load_path):
        sys.exit(f"负荷文件不存在: {load_path}")
    load = load_curve(load_path)
    r = score(load, args.capacity)
    build_html(r, args.name, args.province, args.capacity, args.out)

    print("=" * 56)
    print("PlantAudit · 虚拟工厂用电体检（示意评分）")
    print("=" * 56)
    print(f"对象     : {args.name}（{args.province}）")
    print(f"综合健康度: {r['overall']:.0f} / 100")
    for d in r["dims"]:
        print(f"  {d[0]:<6} {d[1]:.0f}  （{d[2]} · {d[3]}）")
    print(f"\n报告已生成: {args.out}")


if __name__ == "__main__":
    main()
