# workbuddy.md — WorkBuddy 开发对话记录

本项目自始至终在 **腾讯 WorkBuddy** 中开发完成。本文件为开发对话的忠实节录，
用于「麦当劳程序员创意开发大赛 · WorkBuddy 专项奖励」核验。

- 开发产品：腾讯 WorkBuddy（PC 客户端 / 对话式 Agent）
- 开发时间：2026 年 10 月 15 日 — 10 月 16 日
- 开发方式：自然语言驱动，WorkBuddy 自主完成联网调研、方案设计、
  代码编写、本地测试与开源发布

---

## 阶段一 · 赛事调研（WorkBuddy 联网检索）

向 WorkBuddy 提问：参加麦当劳程序员创意开发大赛需要什么。

WorkBuddy 自主抓取并解析了：

- 腾讯云开发者社区大赛公告（article 2758235），提取活动时间、报名方式、
  奖项设置与仓库必备文件清单；
- 麦当劳官方活动仓库 `M-China/mcd-developer-innovation-challenge` 的
  README 与 `activityGuidelines.md`，确认报名 Issue 格式与 Star 排名规则；
- `M-China/mcd-mcp-server` 仓库，整理出 MCP Server 接入方式
  （`https://mcp.mcd.cn`、Streamable HTTP、Bearer Token）与 30+ 工具清单
  （点餐、优惠券、营养、商城、抽奖等场景）。

## 阶段二 · 选题决策（人机对话）

开发者背景：中学排课程序作者，日常接触晚自习值班表。

WorkBuddy 给出 4 个候选方向（值班餐管家 / 省钱助手 / 营养搭配 / 团餐助手）
并分析各自传播性；开发者选定 **「麦麦值班餐管家」**——把排课值班表与
麦当劳点餐连接，解决轮班制团队「今晚谁值班、谁来管饭」的真实痛点。

## 阶段三 · Skill 设计与代码实现（WorkBuddy 编写）

WorkBuddy 生成了项目全部代码与文档，并按大赛要求落地 5 个必备文件：

- `skill/SKILL.md`：五步工作流（值班表解析 → MCP 查菜单/自动领券 →
  预算搭配 → 用户确认 → 下单/取消），并写入「未确认不下单」硬约束；
- `src/duty_parser.py`：值班表解析器，兼容 datetime 单元格、
  `2026/10/16`、`10月16日`、星期制等多种写法，表头自动识别；
- `src/meal_planner.py`：预算搭配算法，回溯搜索保证不超预算；
- `MCP_INTEGRATION.md`：说明实际使用的 MCP Tool（now-time-info、
  query-nearby-stores、query-meals、auto-bind-coupons、query-store-coupons、
  calculate-price、create-order、cancel-order、query-order、
  list-nutrition-foods）、调用链与业务价值；
- `mcp-config.example.json`：脱敏配置，Token 使用环境变量占位。

## 阶段四 · 本地测试与算法修复（WorkBuddy 自测自修）

WorkBuddy 构造测试数据（值班表 xlsx + 菜单 JSON）并实际运行：

| 测试场景 | 结果 |
| --- | --- |
| 解析 2026-10-16 值班表（datetime 日期） | ✅ 3 人名单正确，附加列保留 |
| 解析字符串日期 `2026/10/18` | ✅ 正确命中 1 人 |
| 3 人 / 人均 30 元 | ✅ 合计 ¥83.5 / 预算 ¥90 |
| 4 人 / 人均 40 元 | ✅ 合计 ¥158.5 / 预算 ¥160，全员主餐+饮料 |
| 2 人 / 人均 10 元 | ✅ 正确报「预算不足」并给出最便宜组合提示 |

测试中发现并修复了两个算法问题：

1. 回溯搜索早退导致搭配方案单一 → 移除早退、恢复多样性搜索；
2. 不同花费档位直接比较评分导致饮料配不齐 → 重构为两阶段策略
   （先判断「主餐+饮料」能否全员配齐并预留预算，再在剩余预算内
   最大化主餐价格利用率与多样性）。

## 阶段五 · 开源发布与报名（WorkBuddy 代理执行）

在 WorkBuddy 对话内完成（开发者仅提供一次性 GitHub Token 授权）：

1. 创建公开仓库 `yigedagouge/mcd-duty-dinner-manager`；
2. 推送全部代码（含完整提交记录）；
3. 通过 GitHub API 逐项核验必备文件与 Public 状态；
4. 按官方模板向活动仓库提交报名 Issue（#790）；
5. 监测机器人校验回复。

---

## 完整对话上下文

以上为节录。完整对话可应主办方要求，由开发者从 WorkBuddy 客户端
（任务对话 → 导出 Markdown）提供，涉及本地路径与账号信息的部分已脱敏。
