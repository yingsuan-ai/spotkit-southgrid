#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BillParser · 南网电费单解析（开源外壳 · 结构化）
================================================
将南网电费单（纯文本 / OCR 文本）解析为结构化 JSON，
便于二次分析与对账。规则基于样例账单字段，可按需扩展
正则以适配不同地市的账单版式。

⚠️ 本工具仅做「格式解析 → 结构化」，不计算、不评价、
不承诺任何降费。真实电费以供电单位出具的正式账单为准。

用法：
  python billparser.py --bill sample_bill_yn.txt
  python billparser.py --bill sample_bill_yn.txt --out bill.json
"""
import re
import os
import sys
import json
import argparse

DEFAULT_BILL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data", "sample_bill_yn.txt")


def _num(s):
    return float(s.replace(",", "")) if s else None


def parse(text):
    out = {}
    # 头部字段
    m = re.search(r"用电户号[：:]\s*(\S+)", text)
    if m: out["account_no"] = m.group(1)
    m = re.search(r"用电户名[：:]\s*(\S+)", text)
    if m: out["account_name"] = m.group(1)
    m = re.search(r"供电单位[：:]\s*(\S+)", text)
    if m: out["utility"] = m.group(1)
    m = re.search(r"计费周期[：:]\s*(\S+?)\s*至\s*(\S+)", text)
    if m: out["billing_period"] = {"from": m.group(1), "to": m.group(2)}
    m = re.search(r"变压器容量[：:]\s*(\d+)", text)
    if m: out["transformer_capacity_kva"] = int(m.group(1))

    # 分段电量 / 电费
    segs = {}
    for label in ["尖峰", "峰段", "平段", "谷段"]:
        q = re.search(label + r"电量[：:]\s*([\d,]+)\s*kWh", text)
        c = re.search(label + r"电费[：:]\s*([\d,.]+)\s*元", text)
        if q or c:
            segs[label] = {
                "energy_kwh": _num(q.group(1)) if q else None,
                "charge_yuan": _num(c.group(1)) if c else None,
            }
    if segs: out["segment_energy"] = segs

    # 基本电费
    m = re.search(r"计费方式[：:]\s*(\S+)", text)
    bm = re.search(r"基本电费[：:]\s*([\d,.]+)\s*元", text)
    if m or bm:
        out["basic_charge"] = {
            "method": m.group(1) if m else None,
            "amount_yuan": _num(bm.group(1)) if bm else None,
        }

    # 功率因数 / 力率调整
    m = re.search(r"功率因数[：:]\s*([\d.]+)", text)
    fm = re.search(r"力率调整电费[：:]\s*([\-\d,.]+)\s*元", text)
    if m or fm:
        out["power_factor"] = {
            "value": float(m.group(1)) if m else None,
            "adjustment_yuan": _num(fm.group(1)) if fm else None,
        }

    # 合计
    m = re.search(r"应收电费合计[：:]\s*([\d,.]+)\s*元", text)
    if m: out["total_payable_yuan"] = _num(m.group(1))
    return out


def main():
    ap = argparse.ArgumentParser(description="南网电费单解析（开源外壳·结构化）")
    ap.add_argument("--bill", default=DEFAULT_BILL, help="电费单文本路径")
    ap.add_argument("--out", default=None, help="输出 JSON 路径（缺省打印到控制台）")
    args = ap.parse_args()
    if not os.path.exists(args.bill):
        sys.exit(f"账单文件不存在: {args.bill}")

    with open(args.bill, encoding="utf-8") as f:
        text = f.read()
    result = parse(text)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"已写出: {args.out}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
