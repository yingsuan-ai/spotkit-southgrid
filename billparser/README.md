# BillParser · 南网电费单解析（开源外壳）

将南网电费单（纯文本 / OCR 文本）解析为结构化 JSON，便于二次分析与对账。

## 用法

```bash
# 用自带样例账单
python billparser.py --bill sample_bill_yn.txt

# 写出 JSON 文件
python billparser.py --bill sample_bill_yn.txt --out bill.json
```

## 解析字段

- 头部：户号 / 户名 / 供电单位 / 计费周期 / 变压器容量
- 分段：尖峰 / 峰段 / 平段 / 谷段 的电量与电费
- 基本电费（计费方式 + 金额）、功率因数与力率调整
- 应收电费合计

## ⚠️ 边界说明

本工具仅做「格式解析 → 结构化」，不计算、不评价、不承诺任何降费。真实电费以供电单位出具的正式账单为准。不同地市账单版式可能不同，可按需扩展 `billparser.py` 中的正则。
