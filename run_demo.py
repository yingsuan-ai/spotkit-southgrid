#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_demo.py · 一键跑通四件套（开源外壳）
========================================
在仓库根目录执行：  python run_demo.py
将依次运行 SpotProbe / DeviationSim / BillParser / PlantAudit 的演示，
产物写入 ./demo_out/。全部使用标准库，无需第三方依赖。
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "demo_out")
os.makedirs(OUT, exist_ok=True)


def run(script, *args):
    cmd = [sys.executable, os.path.join(ROOT, script), *args]
    print("\n" + "#" * 60)
    print("# 运行:", script, *args)
    print("#" * 60)
    subprocess.run(cmd, cwd=ROOT)


def main():
    run("spotprobe/spotprobe.py", "--out", OUT)
    run("deviationsim/deviationsim.py", "--demo", "--out", OUT)
    run("billparser/billparser.py", "--out", os.path.join(OUT, "bill.json"))
    run("plantaudit/plantaudit.py", "--demo",
        "--out", os.path.join(OUT, "plant_audit_report.html"))
    print("\n✅ 演示完成，产物在:", OUT)


if __name__ == "__main__":
    main()
