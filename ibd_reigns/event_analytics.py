"""細緻化玩家關卡決策分析 (Fine-grained Event Analytics)

針對「單一卡牌/事件」的深度決策統計。
追蹤玩家在特定嚴苛選項的 YES/NO 選擇比例，
分析不同選擇帶來的存活率差異，
並於後台呈現特定醫療情境的行為漏斗。
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple


# --- DP Primitive (reuse) ---

def _dp_count(true_count: int, epsilon: float = 0.5) -> int:
    """差分隱私計數。"""
    scale = 1.0 / epsilon
    u = random.random() - 0.5
    noise = -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))
    return max(0, round(true_count + noise))


def _dp_ratio(numerator: int, denominator: int, epsilon: float = 0.5) -> Optional[float]:
    """差分隱私比率，分母過小時回傳 None。"""
    if denominator < 3:
        return None
    dp_num = _dp_count(numerator, epsilon)
    dp_den = max(1, _dp_count(denominator, epsilon))
    return round(min(1.0, max(0.0, dp_num / dp_den)), 3)


# --- Per-Card Decision Statistics ---

def compute_card_decision_stats(
    events: List[Dict[str, Any]],
    apply_dp: bool = True,
    k_min: int = 5,
) -> List[Dict[str, Any]]:
    """計算每張卡牌的左/右選擇比例。

    回傳格式:
    [
        {
            "card_id": "...",
            "total_shown": int (DP),
            "total_chosen": int (DP),
            "left_count": int (DP),
            "right_count": int (DP),
            "left_ratio": float|None (DP),
            "right_ratio": float|None (DP),
        },
        ...
    ]
    """
    shown_counts: Counter = Counter()
    choice_counts: Dict[str, Counter] = defaultdict(Counter)

    for e in events:
        name = e.get("name")
        card_id = e.get("card_id")
        if not card_id:
            continue
        if name == "card_shown":
            shown_counts[card_id] += 1
        elif name == "option_chosen":
            side = e.get("option_side", "unknown")
            choice_counts[card_id][side] += 1

    results = []
    for card_id in sorted(shown_counts.keys()):
        total_shown = shown_counts[card_id]
        left_raw = choice_counts[card_id].get("left", 0)
        right_raw = choice_counts[card_id].get("right", 0)
        total_chosen = left_raw + right_raw

        # k-匿名：樣本太少的卡牌不顯示
        if total_shown < k_min:
            continue

        if apply_dp:
            dp_total_shown = _dp_count(total_shown)
            dp_total_chosen = _dp_count(total_chosen)
            dp_left = _dp_count(left_raw)
            dp_right = _dp_count(right_raw)
            left_ratio = _dp_ratio(left_raw, total_chosen)
            right_ratio = _dp_ratio(right_raw, total_chosen)
        else:
            dp_total_shown = total_shown
            dp_total_chosen = total_chosen
            dp_left = left_raw
            dp_right = right_raw
            left_ratio = round(left_raw / total_chosen, 3) if total_chosen > 0 else None
            right_ratio = round(right_raw / total_chosen, 3) if total_chosen > 0 else None

        results.append({
            "card_id": card_id,
            "total_shown": dp_total_shown,
            "total_chosen": dp_total_chosen,
            "left_count": dp_left,
            "right_count": dp_right,
            "left_ratio": left_ratio,
            "right_ratio": right_ratio,
        })

    # 依出現次數由高到低排序
    results.sort(key=lambda x: x["total_shown"], reverse=True)
    return results


# --- Survival Rate by Choice ---

def compute_survival_by_choice(
    events: List[Dict[str, Any]],
    target_card_ids: Optional[List[str]] = None,
    apply_dp: bool = True,
    k_min: int = 5,
) -> List[Dict[str, Any]]:
    """分析選擇特定卡牌左/右後的存活率差異。

    回傳:
    [
        {
            "card_id": str,
            "left_survivors": float|None (存活率, DP),
            "right_survivors": float|None,
            "left_avg_weeks": float|None (平均存活週數, DP),
            "right_avg_weeks": float|None,
            "delta_survival": float|None (存活率差值: left - right),
        },
        ...
    ]
    """
    # Step 1: Build per-session choice map: session -> {card_id -> side}
    session_choices: Dict[str, Dict[str, str]] = defaultdict(dict)
    session_outcomes: Dict[str, Dict[str, Any]] = {}

    for e in events:
        sid = e.get("session_id")
        if not sid:
            continue
        name = e.get("name")
        if name == "option_chosen":
            card_id = e.get("card_id")
            side = e.get("option_side")
            if card_id and side:
                session_choices[sid][card_id] = side
        elif name == "session_end":
            session_outcomes[sid] = {
                "ending_id": e.get("ending_id", "unknown"),
                "weeks_survived": e.get("weeks_survived", 0),
            }

    # Determine which cards to analyze
    if target_card_ids is None:
        all_cards: Counter = Counter()
        for choices in session_choices.values():
            for cid in choices:
                all_cards[cid] += 1
        # Only cards with sufficient appearances
        target_card_ids = [cid for cid, cnt in all_cards.items() if cnt >= k_min]

    results = []
    for card_id in sorted(target_card_ids):
        # Partition sessions by choice for this card
        left_sessions: List[Dict[str, Any]] = []
        right_sessions: List[Dict[str, Any]] = []

        for sid, choices in session_choices.items():
            if card_id not in choices:
                continue
            outcome = session_outcomes.get(sid)
            if outcome is None:
                continue
            side = choices[card_id]
            if side == "left":
                left_sessions.append(outcome)
            elif side == "right":
                right_sessions.append(outcome)

        if len(left_sessions) < k_min and len(right_sessions) < k_min:
            continue

        # 定義「存活」= 週數 >= 52 或結局非死亡類
        _BAD_ENDINGS = {"infection", "flare_storm", "perforation", "give_up",
                        "burnout", "financial_toxicity", "workaholic", "false_confidence"}

        def _survival_stats(sessions: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
            if len(sessions) < k_min:
                return None, None
            survived = sum(1 for s in sessions if s["ending_id"] not in _BAD_ENDINGS)
            total = len(sessions)
            avg_weeks = sum(s["weeks_survived"] for s in sessions) / total if total > 0 else 0
            if apply_dp:
                rate = _dp_ratio(survived, total)
                # DP noise on avg_weeks: Laplace with sensitivity 52/n
                scale = 52.0 / (total * 0.5) if total > 0 else 10
                u = random.random() - 0.5
                noise = -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))
                dp_avg = round(max(0, avg_weeks + noise), 1)
                return rate, dp_avg
            else:
                return round(survived / total, 3) if total > 0 else None, round(avg_weeks, 1)

        left_rate, left_avg = _survival_stats(left_sessions)
        right_rate, right_avg = _survival_stats(right_sessions)

        delta = None
        if left_rate is not None and right_rate is not None:
            delta = round(left_rate - right_rate, 3)

        results.append({
            "card_id": card_id,
            "left_survivors": left_rate,
            "right_survivors": right_rate,
            "left_avg_weeks": left_avg,
            "right_avg_weeks": right_avg,
            "delta_survival": delta,
        })

    return results


# --- Behavioral Funnel ---

def compute_behavioral_funnel(
    events: List[Dict[str, Any]],
    apply_dp: bool = True,
) -> List[Dict[str, Any]]:
    """建立行為漏斗分析。

    衡量從「開始遊戲」到「達到結局」的各階段留存：
    1. 開始遊戲 (session_start)
    2. 做出第一個決策 (first option_chosen)
    3. 存活超過 13 週 (season 1)
    4. 存活超過 26 週 (mid-game)
    5. 存活超過 39 週 (late-game)
    6. 完成遊戲：到達結局 (session_end)
    7. 好結局 (存活 >= 52 週)

    回傳:
    [
        {"stage": "開始遊戲", "count": int (DP), "percent": 100},
        {"stage": "首次決策", "count": int (DP), "percent": float},
        ...
    ]
    """
    session_data: Dict[str, Dict[str, Any]] = {}
    session_first_choice: Dict[str, bool] = {}
    session_max_week: Dict[str, int] = defaultdict(int)

    for e in events:
        sid = e.get("session_id")
        if not sid:
            continue
        name = e.get("name")
        if name == "session_start":
            session_data[sid] = {"started": True}
        elif name == "option_chosen":
            session_first_choice[sid] = True
            week = e.get("week", 0)
            if week > session_max_week[sid]:
                session_max_week[sid] = week
        elif name == "session_end":
            if sid in session_data:
                session_data[sid]["ended"] = True
                session_data[sid]["ending_id"] = e.get("ending_id", "unknown")
                session_data[sid]["weeks_survived"] = e.get("weeks_survived", 0)
                wk = e.get("weeks_survived", 0)
                if wk > session_max_week[sid]:
                    session_max_week[sid] = wk

    total_started = len(session_data)
    if total_started == 0:
        return []

    made_choice = sum(1 for sid in session_data if sid in session_first_choice)
    past_13 = sum(1 for sid in session_data if session_max_week.get(sid, 0) >= 13)
    past_26 = sum(1 for sid in session_data if session_max_week.get(sid, 0) >= 26)
    past_39 = sum(1 for sid in session_data if session_max_week.get(sid, 0) >= 39)
    completed = sum(1 for sid, d in session_data.items() if d.get("ended"))
    good_end = sum(
        1 for sid, d in session_data.items()
        if d.get("ended") and d.get("weeks_survived", 0) >= 52
    )

    raw = [
        ("開始遊戲", total_started),
        ("首次決策", made_choice),
        ("度過第一季 (W13)", past_13),
        ("半年存活 (W26)", past_26),
        ("後期挑戰 (W39)", past_39),
        ("完成遊戲", completed),
        ("好結局 (W52+)", good_end),
    ]

    funnel = []
    for stage, count in raw:
        dp_count_val = _dp_count(count) if apply_dp else count
        pct = round(count / total_started * 100, 1) if total_started > 0 else 0
        funnel.append({
            "stage": stage,
            "count": dp_count_val,
            "percent": pct,
        })

    return funnel


# --- Critical Card Decisions (嚴苛選項分析) ---

def find_critical_decision_cards(
    card_stats: List[Dict[str, Any]],
    threshold_ratio: float = 0.3,
) -> List[Dict[str, Any]]:
    """找出玩家在選擇上最極端的卡牌（左右比例差異最大的）。

    threshold_ratio: 只回傳左右比例差異超過此閾值的卡牌。
    """
    critical = []
    for stat in card_stats:
        lr = stat.get("left_ratio")
        rr = stat.get("right_ratio")
        if lr is None or rr is None:
            continue
        diff = abs(lr - rr)
        if diff >= threshold_ratio:
            dominant = "left" if lr > rr else "right"
            critical.append({
                **stat,
                "dominant_side": dominant,
                "ratio_diff": round(diff, 3),
            })

    critical.sort(key=lambda x: x["ratio_diff"], reverse=True)
    return critical
