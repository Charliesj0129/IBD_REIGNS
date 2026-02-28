"""Tests for the new medical simulation mechanics."""
from ibd_reigns.constants import (
    FLARE_COOLDOWN_TURNS,
    FLARE_HEALTH_DRAIN,
    FLARE_IMMUNE_THRESHOLD,
    FLARE_SANITY_DRAIN,
    FLARE_TAG,
    GUT_BRAIN_HEALTH_THRESHOLD,
    SEASON_CHANGE_WEEKS,
    SLEEP_DEPRIVED_IMMUNE_PENALTY,
    SLEEP_DEPRIVED_SANITY_DRAIN,
    SLEEP_DEPRIVED_TAG,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_MONEY,
    STAT_SANITY,
    STEROID_BONE_LOSS_THRESHOLD,
    STEROID_CUMULATIVE_THRESHOLD,
    STEROID_MOON_FACE_TAG,
)
from ibd_reigns.engine import (
    _apply_flare_cycle,
    _apply_gut_brain_axis,
    _apply_season_change_jitter,
    _apply_sleep_deprivation,
    _track_steroid_cumulative,
    new_game_state,
)
from ibd_reigns.models import CardOption


def _rng_always(val: float):
    def _rng():
        return val
    return _rng


def test_flare_cycle_triggers_on_high_immune():
    state = new_game_state()
    state.stats[STAT_IMMUNE] = FLARE_IMMUNE_THRESHOLD + 5
    state.flare_cooldown = 0
    _apply_flare_cycle(state, _rng_always(0.5))
    assert FLARE_TAG in state.tags
    assert state.flare_cooldown == FLARE_COOLDOWN_TURNS
    assert "flare_episode" in state.queued_card_ids


def test_flare_cycle_drains_stats():
    state = new_game_state()
    state.stats[STAT_IMMUNE] = FLARE_IMMUNE_THRESHOLD + 5
    state.tags.add(FLARE_TAG)
    state.flare_cooldown = 2  # already in cooldown
    initial_health = state.stats[STAT_HEALTH]
    initial_sanity = state.stats[STAT_SANITY]
    _apply_flare_cycle(state, _rng_always(0.5))
    assert state.stats[STAT_HEALTH] == initial_health - FLARE_HEALTH_DRAIN
    assert state.stats[STAT_SANITY] == initial_sanity - FLARE_SANITY_DRAIN


def test_flare_resolves_when_immune_drops():
    state = new_game_state()
    state.tags.add(FLARE_TAG)
    state.stats[STAT_IMMUNE] = FLARE_IMMUNE_THRESHOLD - 15  # Below threshold - 10
    _apply_flare_cycle(state, _rng_always(0.5))
    assert FLARE_TAG not in state.tags


def test_flare_does_not_trigger_during_cooldown():
    state = new_game_state()
    state.stats[STAT_IMMUNE] = FLARE_IMMUNE_THRESHOLD + 10
    state.flare_cooldown = 3
    _apply_flare_cycle(state, _rng_always(0.5))
    assert FLARE_TAG not in state.tags


def test_gut_brain_axis_amplifies_sanity_loss():
    state = new_game_state()
    state.stats[STAT_HEALTH] = GUT_BRAIN_HEALTH_THRESHOLD - 5
    initial_sanity = state.stats[STAT_SANITY]
    deltas = {STAT_SANITY: -10}
    _apply_gut_brain_axis(state, deltas)
    assert state.stats[STAT_SANITY] < initial_sanity


def test_gut_brain_axis_no_effect_when_healthy():
    state = new_game_state()
    state.stats[STAT_HEALTH] = 80  # Well above threshold
    initial_sanity = state.stats[STAT_SANITY]
    deltas = {STAT_SANITY: -10}
    _apply_gut_brain_axis(state, deltas)
    assert state.stats[STAT_SANITY] == initial_sanity


def test_gut_brain_axis_no_effect_on_positive_sanity():
    state = new_game_state()
    state.stats[STAT_HEALTH] = GUT_BRAIN_HEALTH_THRESHOLD - 5
    initial_sanity = state.stats[STAT_SANITY]
    deltas = {STAT_SANITY: 5}  # Positive delta
    _apply_gut_brain_axis(state, deltas)
    assert state.stats[STAT_SANITY] == initial_sanity


def test_steroid_cumulative_moon_face():
    state = new_game_state()
    option = CardOption(label="steroids", steroid_use=True)
    for _ in range(STEROID_CUMULATIVE_THRESHOLD):
        _track_steroid_cumulative(state, option)
    assert STEROID_MOON_FACE_TAG in state.tags


def test_steroid_cumulative_bone_loss():
    state = new_game_state()
    option = CardOption(label="steroids", steroid_use=True)
    initial_cap = state.max_caps[STAT_HEALTH]
    for _ in range(STEROID_BONE_LOSS_THRESHOLD):
        _track_steroid_cumulative(state, option)
    assert state.max_caps[STAT_HEALTH] < initial_cap


def test_steroid_no_effect_without_steroid_use():
    state = new_game_state()
    option = CardOption(label="other", steroid_use=False)
    _track_steroid_cumulative(state, option)
    assert state.steroid_use_count == 0
    assert STEROID_MOON_FACE_TAG not in state.tags


def test_sleep_deprivation_effects():
    state = new_game_state()
    state.tags.add(SLEEP_DEPRIVED_TAG)
    initial_immune = state.stats[STAT_IMMUNE]
    initial_sanity = state.stats[STAT_SANITY]
    _apply_sleep_deprivation(state)
    assert state.stats[STAT_IMMUNE] == initial_immune + SLEEP_DEPRIVED_IMMUNE_PENALTY
    assert state.stats[STAT_SANITY] == initial_sanity - SLEEP_DEPRIVED_SANITY_DRAIN


def test_sleep_deprivation_no_effect_when_rested():
    state = new_game_state()
    initial_immune = state.stats[STAT_IMMUNE]
    initial_sanity = state.stats[STAT_SANITY]
    _apply_sleep_deprivation(state)
    assert state.stats[STAT_IMMUNE] == initial_immune
    assert state.stats[STAT_SANITY] == initial_sanity


def test_season_change_jitter_at_transition():
    state = new_game_state()
    state.week = SEASON_CHANGE_WEEKS[0]
    initial_immune = state.stats[STAT_IMMUNE]
    _apply_season_change_jitter(state, _rng_always(0.0))
    # rng=0.0 -> jitter = int((0 - 0.5) * 2 * 5) = -5
    assert state.stats[STAT_IMMUNE] == initial_immune - 5


def test_season_change_jitter_no_effect_normal_week():
    state = new_game_state()
    state.week = 5  # Not a transition week
    initial_immune = state.stats[STAT_IMMUNE]
    _apply_season_change_jitter(state, _rng_always(0.5))
    assert state.stats[STAT_IMMUNE] == initial_immune


def test_dynamic_deck_weighting_high_immune():
    """Test that high immune boosts treatment/complication card weights."""
    from ibd_reigns.deck import CardDeck
    from ibd_reigns.models import Card, CardConditions

    cards = [
        Card(id="treat", text="t", left=CardOption(label="L"), right=CardOption(label="R"), theme="treatment"),
        Card(id="social", text="s", left=CardOption(label="L"), right=CardOption(label="R"), theme="social"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    state.stats[STAT_IMMUNE] = 80  # High immune

    # Draw many times to check distribution
    counts = {"treat": 0, "social": 0}
    for _ in range(200):
        card = deck.draw(state, _rng_always(0.3), pool=None)
        counts[card.id] += 1
    # Treatment should be drawn more often
    assert counts["treat"] > counts["social"]
