from ibd_reigns.analytics_summary import (
    load_events, summarize_all, summarize_session,
    dp_count, purge_old_events, k_anonymize, K_ANONYMITY_THRESHOLD,
    PrivacyBudgetTracker, summarize_trend, filter_by_consent
)


def test_summarize_session(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        """{"name":"session_start","session_id":"s1"}\n{"name":"card_shown","session_id":"s1","card_id":"a"}\n{"name":"option_chosen","session_id":"s1","card_id":"a"}\n{"name":"session_end","session_id":"s1","ending_id":"end","weeks_survived":10}\n""",
        encoding="utf-8",
    )
    events = load_events(str(path))
    summary = summarize_session(events, "s1")
    assert summary["ending_id"] == "end"
    assert summary["choices"] == 1


def test_summarize_all(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        """{"name":"session_end","session_id":"s1","ending_id":"end"}\n{"name":"card_shown","session_id":"s1","card_id":"a"}\n{"name":"card_shown","session_id":"s2","card_id":"a"}\n""",
        encoding="utf-8",
    )
    events = load_events(str(path))
    summary = summarize_all(events, apply_dp=False)
    assert summary["total_sessions"] == 2
    assert summary["privacy_applied"] is False
    assert "privacy_metadata" in summary
    assert summary["privacy_metadata"]["mechanism"] == "none"
    assert "education_engagement" in summary


def test_summarize_all_with_dp(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        """{"name":"session_end","session_id":"s1","ending_id":"end"}\n{"name":"card_shown","session_id":"s1","card_id":"a"}\n""",
        encoding="utf-8",
    )
    events = load_events(str(path))
    summary = summarize_all(events, apply_dp=True)
    assert summary["privacy_applied"] is True
    pm = summary["privacy_metadata"]
    assert pm["mechanism"] == "Laplace DP"
    assert pm["epsilon"] == 0.5
    assert pm["k_anonymity_threshold"] == K_ANONYMITY_THRESHOLD


def test_privacy_budget_tracker():
    tracker = PrivacyBudgetTracker(total_budget=1.0, per_query_epsilon=0.6)
    # First query ok (0 + 0.6 <= 1.0)
    assert tracker.record_query() is True
    assert tracker.spent == 0.6
    # Second query fails (0.6 + 0.6 > 1.0)
    assert tracker.record_query() is False
    assert tracker.spent == 0.6
    assert tracker.query_count == 1


def test_consent_filtering():
    summary = {"total_sessions": 10, "total_events": 100, "top_cards": ["a"], "privacy_applied": True, "privacy_metadata": {}}
    
    # Basic: only total_sessions and metadata
    basic = filter_by_consent(summary, "basic")
    assert "total_sessions" in basic
    assert "total_events" not in basic
    assert "top_cards" not in basic

    # Analytics: removes total_events (raw)
    analytics = filter_by_consent(summary, "analytics")
    assert "total_sessions" in analytics
    assert "top_cards" in analytics
    assert "total_events" not in analytics

    # Full: keeps everything
    full = filter_by_consent(summary, "full")
    assert full == summary


def test_summarize_trend(tmp_path):
    import time
    now = time.time()
    events = [
        {"name": "session_start", "timestamp": now},
        {"name": "session_start", "timestamp": now - 7*86400}, # 1 week ago
    ]
    trend = summarize_trend(events, weeks=2)
    assert len(trend) == 2
    # Check that we have sessions > 0 (dp_count might return 0 due to noise if count is low, but usually >0 for valid input)
    # Since dp_count adds noise, we just check structure here
    assert "week" in trend[0]
    assert "sessions" in trend[0]


def test_dp_count_nonnegative():
    """DP count should never go negative."""
    for _ in range(100):
        assert dp_count(0) >= 0
        assert dp_count(1) >= 0


def test_k_anonymize_suppresses_rare():
    items = [("common", 10), ("rare", 2), ("very_rare", 1)]
    result = k_anonymize(items, k=5)
    labels = [r[0] for r in result]
    assert "common" in labels
    assert "rare" not in labels
    assert "very_rare" not in labels
    assert "other (suppressed)" in labels
    assert sum(r[1] for r in result if r[0] == "other (suppressed)") == 3


def test_k_anonymize_keeps_all_above_threshold():
    items = [("a", 10), ("b", 7)]
    result = k_anonymize(items, k=5)
    assert len(result) == 2
    assert "other (suppressed)" not in [r[0] for r in result]


def test_k_anonymize_empty():
    assert k_anonymize([]) == []


def test_purge_old_events(tmp_path):
    import time
    path = tmp_path / "events.jsonl"
    old_ts = time.time() - 100 * 86400  # 100 days ago
    new_ts = time.time() - 10 * 86400   # 10 days ago
    path.write_text(
        f'{{"name":"old","timestamp":{old_ts}}}\n{{"name":"new","timestamp":{new_ts}}}\n',
        encoding="utf-8",
    )
    purged = purge_old_events(str(path), max_age_days=90)
    assert purged == 1
    remaining = load_events(str(path))
    assert len(remaining) == 1
    assert remaining[0]["name"] == "new"
