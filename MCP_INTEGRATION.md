# MCP_INTEGRATION.md — 麦当劳 MCP 集成说明

## 接入方式

| 项 | 值 |
| --- | --- |
| MCP Server | 麦当劳中国官方远程托管服务 |
| Endpoint | `https://mcp.mcd.cn` |
| 协议 | Streamable HTTP |
| 认证 | `Authorization: Bearer <MCP_TOKEN>`（Token 申请：https://open.mcd.cn/mcp） |
| 限流 | 600 次/分钟/Token，超限返回 429 |

本项目通过 WorkBuddy「自定义连接器」接入（配置模板见
[`mcp-config.example.json`](mcp-config.example.json)，Token 以环境变量占位，
仓库中不含任何真实凭据）。

## 实际使用的 Tool 与调用流程

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ 值班表 Excel │ --> │ duty_parser.py   --> │ 今晚值班名单（JSON） │
└─────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                        │ 人数
                  ┌─────────────────────────────────────┘
                  v
  1. now-time-info          —— 校准日期时间（区分正餐/早餐/夜宵档）
  2. query-nearby-stores    —— 按学校地址查附近门店（外送场景用
                               delivery-query-stores / delivery-query-addresses）
  3. query-meals            —— 拉取门店可售菜单 -> menu.json
  4. query-meal-detail      —— 查看套餐组成/可替换项（按需）
  5. auto-bind-coupons      —— 一键领取麦麦省全部可用优惠券
  6. query-store-coupons    —— 查询当前门店可用券
  7. duty_parser.py 输出人数 + 用户预算
       -> meal_planner.py   —— 本地按预算生成「每人主餐+饮料+公共小食」方案
  8. calculate-price        —— 用（可含券）商品列表算实付价，与预估核对
  9. create-order           —— 用户确认后创建订单，返回支付链接
 10. query-order / order-list —— 查订单状态与历史
 11. cancel-order           —— 取消未支付订单
```

## 各工具的业务价值

| Tool | 在本项目中的价值 |
| --- | --- |
| `query-meals` + `query-meal-detail` | 菜单数据源，是预算搭配算法的输入 |
| `auto-bind-coupons` / `query-store-coupons` | 自动领券保证「同一预算吃到更多」，这是管家价值的核心 |
| `calculate-price` | 把搭配方案变成可支付的精确金额，避免预算失控 |
| `create-order` / `cancel-order` / `query-order` | 闭环：从方案到真正吃上饭 |
| `now-time-info` | 值班餐发生在晚间/深夜，需要时间档位判断 |
| `list-nutrition-foods` | 扩展功能：为值夜班的老师提供热量参考（熬夜友好搭配） |

## 未使用但说明原因

- `mall-*` / `query-my-account`（积分商城）：与「当餐解决值班餐」主场景无关，
  作为路线图功能（用积分兑换员工下午茶）保留；
- `party-*`（主题活动预约）：场景不符。

## 限流与容错

- 所有 MCP 调用按「一次对话一轮必要查询」组织，不做轮询；
- 收到 429 时提示用户稍后重试，脚本不自动重试；
- 收到 401 时提示 Token 失效，引导到 open.mcd.cn/mcp 重新激活。
