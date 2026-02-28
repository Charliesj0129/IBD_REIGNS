"""Tests for fine-grained event analytics module."""

import pytest
from ibd_reigns.event_analytics import (
    compute_card_decision_stats,
    compute_behavioral_funnel,
    compute_survival_by_choice,
    find_critical_decision_cards,
    _dp_count,
    _dp_ratio,
)


# --- Helper to build mock events ---

def _make_events(n_sessions: int = 10) -> list:
    """Generate synthetic analytics events for testing."""
    import time
    events = []
    for i in range(n_sessions):
        sid = f"session_{i}"
        events.append({"name": "session_start", "session_id": sid, "timestamp": time.time()})

        # Each session plays some cards
        cards_to_show = ["med_choice", "diet_question", "social_event", "flare_alert", "bio_treatment"]
        for week, card_id in enumerate(cards_to_show, start=1):
            events.append({
                "name": "card_shown",
                "session_id": sid,
                "card_id": card_id,
                "week": week,
                "pool": "spring",
                "available_options": ["left", "right"],
            })
            # Alternate choices to create patterns
            side = "left" if (i + week) % 3 != 0 else "right"
            events.append({
                "name": "option_chosen",
                "session_id": sid,
                "card_id": card_id,
                "option_side": side,
                "week": week,
                "stat_direction": {"HEALTH": "up"},
                "tags_count": 0,
            })

        # Some sessions survive, some don't
        weeks_survived = 52 if i % 3 == 0 else 20 + i * 3
        ending_id = "survived" if weeks_survived >= 52 else "infection"
        events.append({
            "name": "session_end",
            "session_id": sid,
            "ending_id": ending_id,
            "weeks_survived": weeks_survived,
        })

    return events


# --- DP Primitives ---

class TestDpPrimitives:
    def test_dp_count_non_negative(self):
        """DP count should never return negative."""
        for _ in range(100):
            result = _dp_count(0, epsilon=0.5)
            assert result >= 0

    def test_dp_count_roughly_correct(self):
        """DP count should be roughly near the true value for large counts."""
        results = [_dp_count(100, epsilon=1.0) for _ in range(200)]
        avg = sum(results) / len(results)
        assert 80 < avg < 120  # within ~20% on average

    def test_dp_ratio_small_denominator_returns_none(self):
        """Ratio with denominator < 3 should return None."""
        result = _dp_ratio(1, 2)
        assert result is None

    def test_dp_ratio_valid(self):
        """Ratio with large denominator should return a float in [0, 1]."""
        result = _dp_ratio(50, 100, epsilon=1.0)
        assert result is not None
        assert 0.0 <= result <= 1.0


# --- Card Decision Stats ---

class TestCardDecisionStats:
    def test_basic_stats(self):
        events = _make_events(10)
        stats = compute_card_decision_stats(events, apply_dp=False, k_min=5)
        assert len(stats) > 0
        for s in stats:
            assert "card_id" in s
            assert "total_shown" in s
            assert "left_count" in s
            assert "right_count" in s
            assert "left_ratio" in s
            assert "right_ratio" in s

    def test_ratios_sum_to_one(self):
        events = _make_events(10)
        stats = compute_card_decision_stats(events, apply_dp=False, k_min=5)
        for s in stats:
            if s["left_ratio"] is not None and s["right_ratio"] is not None:
                total = s["left_ratio"] + s["right_ratio"]
                assert abs(total - 1.0) < 0.01

    def test_dp_applied(self):
        events = _make_events(20)
        stats_raw = compute_card_decision_stats(events, apply_dp=False, k_min=5)
        stats_dp = compute_card_decision_stats(events, apply_dp=True, k_min=5)
        # Both should have results, but exact counts may differ
        assert len(stats_raw) > 0
        assert len(stats_dp) > 0

    def test_k_min_filter(self):
        events = _make_events(3)  # 只有 3 session
        stats = compute_card_decision_stats(events, apply_dp=False, k_min=10)
        # Not enough data, should be filtered out
        assert len(stats) == 0

    def test_empty_events(self):
        stats = compute_card_decision_stats([], apply_dp=False)
        assert stats == []


# --- Behavioral Funnel ---

class TestBehavioralFunnel:
    def test_funnel_stages(self):
        events = _make_events(10)
        funnel = compute_behavioral_funnel(events, apply_dp=False)
        assert len(funnel) == 7
        stage_names = [f["stage"] for f in funnel]
        assert "開始遊戲" in stage_names
        assert "首次決策" in stage_names
        assert "完成遊戲" in stage_names
        assert "好結局 (W52+)" in stage_names

    def test_funnel_decreasing_counts(self):
        events = _make_events(10)
        funnel = compute_behavioral_funnel(events, apply_dp=False)
        # Funnel should generally decrease (or stay same)
        for i in range(1, len(funnel)):
            assert funnel[i]["count"] <= funnel[0]["count"]

    def test_funnel_first_stage_100_percent(self):
        events = _make_events(10)
        funnel = compute_behavioral_funnel(events, apply_dp=False)
        assert funnel[0]["percent"] == 100.0

    def test_funnel_empty_events(self):
        funnel = compute_behavioral_funnel([], apply_dp=False)
        assert funnel == []

    def test_funnel_with_dp(self):
        events = _make_events(10)
        funnel = compute_behavioral_funnel(events, apply_dp=True)
        assert len(funnel) == 7
        for stage in funnel:
            assert stage["count"] >= 0


# --- Survival by Choice ---

class TestSurvivalByChoice:
    def test_basic_survival_stats(self):
        events = _make_events(20)
        survival = compute_survival_by_choice(events, apply_dp=False, k_min=3)
        # Should produce some results
        assert isinstance(survival, list)

    def test_survival_rates_in_range(self):
        events = _make_events(20)
        survival = compute_survival_by_choice(events, apply_dp=False, k_min=3)
        for s in survival:
            if s["left_survivors"] is not None:
                assert 0.0 <= s["left_survivors"] <= 1.0
            if s["right_survivors"] is not None:
                assert 0.0 <= s["right_survivors"] <= 1.0

    def test_target_card_filter(self):
        events = _make_events(20)
        survival = compute_survival_by_choice(
            events, target_card_ids=["med_choice"], apply_dp=False, k_min=3
        )
        for s in survival:
            assert s["card_id"] == "med_choice"

    def test_survival_empty_events(self):
        survival = compute_survival_by_choice([], apply_dp=False)
        assert survival == []


# --- Critical Decision Cards ---

class TestCriticalDecisionCards:
    def test_find_critical_cards(self):
        # Create heavily skewed stats
        stats = [
            {"card_id": "a", "left_ratio": 0.9, "right_ratio": 0.1, "total_chosen": 100},
            {"card_id": "b", "left_ratio": 0.5, "right_ratio": 0.5, "total_chosen": 50},
            {"card_id": "c", "left_ratio": 0.2, "right_ratio": 0.8, "total_chosen": 80},
        ]
        critical = find_critical_decision_cards(stats, threshold_ratio=0.3)
        assert len(critical) == 2  # a and c
        assert critical[0]["card_id"] == "a"
        assert critical[0]["dominant_side"] == "left"
        assert critical[1]["card_id"] == "c"
        assert critical[1]["dominant_side"] == "right"

    def test_no_critical_cards(self):
        stats = [
            {"card_id": "a", "left_ratio": 0.5, "right_ratio": 0.5},
            {"card_id": "b", "left_ratio": 0.55, "right_ratio": 0.45},
        ]
        critical = find_critical_decision_cards(stats, threshold_ratio=0.3)
        assert len(critical) == 0

    def test_none_ratios_skipped(self):
        stats = [
            {"card_id": "a", "left_ratio": None, "right_ratio": None},
        ]
        critical = find_critical_decision_cards(stats, threshold_ratio=0.3)
        assert len(critical) == 0

    def test_empty_stats(self):
        critical = find_critical_decision_cards([], threshold_ratio=0.3)
        assert len(critical) == 0
