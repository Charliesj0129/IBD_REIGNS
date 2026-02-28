"""Tests for Round 4 and 5 mechanics:
- Diet Score & Effects
- Ostomy Mechanics
- Social Isolation
- Milestone Logging
"""
from ibd_reigns.constants import (
    DIET_HIGH_THRESHOLD,
    DIET_LOW_THRESHOLD,
    OSTOMY_TAG,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_SANITY,
)
from ibd_reigns.engine import (
    _apply_diet_mechanics,
    _apply_ostomy_mechanics,
    _record_milestone_log,
    _track_social_isolation,
    _update_round4_stats,
    apply_choice,
    new_game_state,
)
from ibd_reigns.models import Card, CardOption


def _make_card(card_id="test", theme="treatment", rarity="common"):
    return Card(
        id=card_id,
        text="test",
        left=CardOption(label="L"),
        right=CardOption(label="R"),
        theme=theme,
        rarity=rarity,
    )


# --- Diet Mechanics ---


def test_diet_score_update():
    state = new_game_state()
    option = CardOption(label="Eat well", diet_delta=2)
    _update_round4_stats(state, option)
    assert state.diet_score == 2

    option_bad = CardOption(label="Eat junk", diet_delta=-5)
    _update_round4_stats(state, option_bad)
    assert state.diet_score == -3


def test_diet_score_clamping():
    state = new_game_state()
    state.diet_score = 8
    option = CardOption(label="Super food", diet_delta=5)
    _update_round4_stats(state, option)
    assert state.diet_score == 10  # Max 10


def test_apply_diet_mechanics_bonus():
    state = new_game_state()
    state.diet_score = DIET_HIGH_THRESHOLD + 1
    bonus = _apply_diet_mechanics(state)
    assert STAT_HEALTH in bonus
    assert bonus[STAT_HEALTH] > 0


def test_apply_diet_mechanics_penalty():
    state = new_game_state()
    state.diet_score = DIET_LOW_THRESHOLD - 1
    bonus = _apply_diet_mechanics(state)
    assert STAT_IMMUNE in bonus  # Instability penalty


# --- Ostomy Mechanics ---


def test_ostomy_leak_risk_logic():
    state = new_game_state()
    state.tags.add(OSTOMY_TAG)
    state.ostomy_care_skill = 0  # Low skill -> High risk
    
    # Mock rng to force leak (high probability check)
    # The function uses rng() < risk. risk ~ 0.4.
    # If rng returns 0.0, leak happens.
    _apply_ostomy_mechanics(state, lambda: 0.0)
    
    assert "OSTOMY_LEAK" in state.tags
    assert "ostomy_leak_event" in state.queued_card_ids
    assert state.stats[STAT_SANITY] < 50


def test_ostomy_mechanics_ignored_without_tag():
    state = new_game_state()
    # No OSTOMY_TAG
    _apply_ostomy_mechanics(state, lambda: 0.0)
    assert "OSTOMY_LEAK" not in state.tags


# --- Social Isolation ---


def test_social_isolation_increase_on_avoidance():
    state = new_game_state()
    card = _make_card(theme="social")
    option = CardOption(label="Stay home alone")  # Keywords: home
    _track_social_isolation(state, card, option)
    assert state.social_isolation_counter == 1


def test_social_isolation_decrease_on_participation():
    state = new_game_state()
    state.social_isolation_counter = 2
    card = _make_card(theme="social")
    option = CardOption(label="Go to party")  # No avoidance keywords
    _track_social_isolation(state, card, option)
    assert state.social_isolation_counter == 1


def test_social_isolation_triggers_isolated_tag():
    state = new_game_state()
    state.social_isolation_counter = 2
    card = _make_card(theme="social")
    option = CardOption(label="Refuse invitation")
    _track_social_isolation(state, card, option)
    
    assert state.social_isolation_counter == 3
    assert "ISOLATED" in state.tags
    assert state.max_caps[STAT_SANITY] < 100
    assert "social_breakdown" in state.queued_card_ids


def test_social_isolation_recovery():
    state = new_game_state()
    state.tags.add("ISOLATED")
    state.max_caps[STAT_SANITY] = 90
    state.social_isolation_counter = 2  # Already dropped below 3 somehow (simulate mechanic)
    
    # Trigger check with non-avoidance
    card = _make_card(theme="social")
    option = CardOption(label="Go out")
    _track_social_isolation(state, card, option)
    
    assert "ISOLATED" not in state.tags
    assert state.max_caps[STAT_SANITY] == 100


# --- Milestone Logging ---


def test_milestone_logging_rare_card():
    state = new_game_state()
    card = _make_card(rarity="rare")
    option = CardOption(label="Do something")
    _record_milestone_log(state, card, option)
    assert len(state.milestones) == 1
    assert "rare" in state.milestones[0] or "Do something" in state.milestones[0]


def test_milestone_logging_surgery():
    state = new_game_state()
    card = _make_card(card_id="surgery_event", rarity="common")
    option = CardOption(label="Operate")
    _record_milestone_log(state, card, option)
    assert len(state.milestones) == 1
