---
name: mcd-duty-dinner-manager
title: 麦麦值班餐管家
description: 导入排课/值班表，自动为值班教师按预算搭配麦当劳晚餐并下单（基于麦当劳 MCP）
version: 1.0.0
---

# 麦麦值班餐管家（Skill 使用说明）

本 Skill 把「今晚谁值班」和「谁来管饭」两件事连起来：解析值班表 → 按预算
搭配麦当劳餐品 → 展示方案 → 用户确认后经麦当劳 MCP 下单。

## 前置条件

1. WorkBuddy 已配置 `mcd-mcp` 自定义连接器（见 `mcp-config.example.json`）；
2. 有一份值班/排课 Excel（长表格式：日期、姓名，以及班级/科目/时段等任选列）。

## 工作流程（严格按顺序执行）

### 第 1 步 · 确认今晚值班人员

运行 `src/duty_parser.py`：

```bash
python src/duty_parser.py --file <值班表.xlsx>          # 默认今天
python src/duty_parser.py --file <值班表.xlsx> --date 2026-10-16
```

把返回的 `people` 名单**展示给用户核对**。人数为 0 时提示检查表格后停止。

### 第 2 步 · 询问预算

向用户询问人均预算（缺省建议 30 元）与就餐方式（外送 / 到店取餐）。

### 第 3 步 · 获取菜单与优惠（麦当劳 MCP）

按顺序调用 MCP 工具，把结果落成本地 JSON 供搭配器使用：

| 顺序 | 工具 | 用途 |
| --- | --- | --- |
| 1 | `now-time-info` | 校准当前时间（决定能否点早餐/夜宵档） |
| 2 | `query-nearby-stores` 或 `delivery-query-stores` | 根据学校/家庭地址选门店 |
| 3 | `query-meals` | 拉取当前门店可售菜单 |
| 4 | `query-meal-detail` | 需要时查看套餐组成 |
| 5 | `auto-bind-coupons` → `query-store-coupons` | 先自动领券，再查可用券 |

把 `query-meals` 结果保存为 `menu.json`（字段：name / price / category）。

### 第 4 步 · 生成搭配方案

```bash
python src/meal_planner.py --menu menu.json --people <人数> --budget <人均预算>
```

把返回的 `plan`（每人主餐+饮料）与 `share_snacks`（公共小食）整理成表格
**展示给用户**，同时给出 `estimated_total` 与总预算对比。

### 第 5 步 · 用户确认后下单（必须有确认步骤！）

1. 如有可用券，询问是否使用；
2. 调用 `calculate-price` 计算含优惠实付价，与预估核对；
3. **必须复述完整订单（门店、就餐方式、商品明细、实付金额）并得到用户
   明确同意后**，才能调用 `create-order`；
4. 下单成功后展示 `query-order` 的订单状态与支付链接；
5. 用户反悔时用 `cancel-order` 取消。

## 安全与边界

- MCP Token 只从连接器配置读取，**永远不要**在对话中输出 Token 明文；
- 每分钟 MCP 限流 600 次，批量查询间无需刻意等待，但不要循环重试 429；
- 下单、支付属于不可逆操作，**未确认不下单**是硬约束；
- 本 Skill 不处理退款，只支持取消未支付订单。
