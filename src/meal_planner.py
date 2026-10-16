#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""值班餐预算搭配器：按人均预算从菜单里搭配出 N 份晚餐方案。

输入（JSON，来自麦当劳 MCP 的 query-meals / query-meal-detail 导出）:
    [{"name": "巨无霸套餐", "price": 45.5, "category": "主食"}, ...]

category 取值（缺省自动推断）: 主食 / 小食 / 饮料
规则: 每人 1 份主食 + 1 份饮料（预算允许时）+ 剩余预算分配小食。
算法: 主食组合用有界回溯（人数少，组合空间小），保证总价 <= 总预算。
"""
import argparse
import json
import sys
from itertools import product

DRINK_HINTS = ("可乐", "咖啡", "汁", "奶茶", "汽水", "饮用水", "矿泉水", "奶", "茶")
MAIN_CATS = ("主食", "套餐", "汉堡", "饭", "面")


def _guess_category(item):
    if item.get("category"):
        return item["category"]
    name = item.get("name", "")
    if any(h in name for h in DRINK_HINTS):
        return "饮料"
    return "主食" if any(c in name for c in MAIN_CATS) else "小食"


def plan(meals, people, budget_per_person, prefer_cheap_when_tight=True):
    meals = [dict(m, category=_guess_category(m)) for m in meals]
    mains = sorted([m for m in meals if m["category"] == "主食"], key=lambda x: x["price"])
    drinks = sorted([m for m in meals if m["category"] == "饮料"], key=lambda x: x["price"])
    snacks = sorted([m for m in meals if m["category"] == "小食"], key=lambda x: x["price"])

    total_budget = round(budget_per_person * people, 2)
    if not mains:
        return {"ok": False, "error": "菜单中没有主食类餐品"}

    # 阶段一：先判断「每人主餐+饮料」是否配得起，配得起就预留饮料预算
    drink = None
    if drinks and total_budget >= people * (mains[0]["price"] + drinks[0]["price"]):
        drink = drinks[0]
        total_budget = round(total_budget - people * drink["price"], 2)

    # 阶段二：在剩余预算内搜索主餐组合（价格利用率 + 多样性）
    mains_pool = mains if prefer_cheap_when_tight else list(reversed(mains))
    best, best_score = None, -1.0

    def score(combo):
        prices = sum(m["price"] for m in combo)
        diversity = len({m["name"] for m in combo})
        return prices + 0.8 * diversity

    def backtrack(i, chosen, spent):
        nonlocal best, best_score
        if i == people:
            s = score(chosen)
            if s > best_score:
                best_score, best = s, list(chosen)
            return
        for m in mains_pool:
            p = m["price"]
            if spent + p > total_budget + 1e-9:
                continue
            chosen.append(m)
            backtrack(i + 1, chosen, spent + p)
            chosen.pop()

    backtrack(0, [], 0.0)
    if best is None:
        return {"ok": False,
                "error": f"预算不足：最便宜主食 {mains[0]['name']} ¥{mains[0]['price']} × {people} 人 "
                         f"已超过总预算 ¥{round(budget_per_person * people, 2)}"}

    plan_lines, total = [], 0.0
    for i, m in enumerate(best, 1):
        line = {"person": f"值班人员{i}", "main": m["name"], "price": m["price"]}
        if drink:
            line["drink"] = drink["name"]
            line["price"] = round(m["price"] + drink["price"], 2)
        total += line["price"]
        plan_lines.append(line)

    # 剩余预算分配小食（大家一起吃）
    remain = round(budget_per_person * people - total, 2)
    extras = []
    for s in reversed(snacks):
        while s["price"] <= remain and remain > 0:
            extras.append(s["name"])
            remain = round(remain - s["price"], 2)
            if len(extras) >= people:  # 小食最多按人数分配，避免堆砌
                break
        if len(extras) >= people:
            break

    return {
        "ok": True,
        "people": people,
        "budget_per_person": budget_per_person,
        "total_budget": round(budget_per_person * people, 2),
        "estimated_total": round(total, 2),
        "plan": plan_lines,
        "share_snacks": extras,
        "note": "价格为菜单参考价，实际以 calculate-price（含优惠券）结果为准",
    }


def main():
    ap = argparse.ArgumentParser(description="值班餐预算搭配器")
    ap.add_argument("--menu", required=True, help="菜单 JSON 文件（MCP 导出）")
    ap.add_argument("--people", type=int, required=True)
    ap.add_argument("--budget", type=float, required=True, help="人均预算（元）")
    args = ap.parse_args()

    with open(args.menu, encoding="utf-8") as f:
        meals = json.load(f)
    result = plan(meals, args.people, args.budget)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
