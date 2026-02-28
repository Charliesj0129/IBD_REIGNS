"""Tests for dynamic deck weighting and all stat-based branches."""
from ibd_reigns.constants import STAT_HEALTH, STAT_IMMUNE, STAT_MONEY, STAT_SANITY
from ibd_reigns.deck import CardDeck, _weighted_choice
from ibd_reigns.engine import new_game_state
from ibd_reigns.models import Card, CardOption


def _rng(val: float):
    def _f():
        return val
    return _f


def _make_card(card_id, theme="misc", rarity="common", pool=None, tags=None):
    return Card(
        id=card_id,
        text="test",
        left=CardOption(label="L"),
        right=CardOption(label="R"),
        theme=theme,
        rarity=rarity,
        pool=pool,
        tags=tags or [],
    )


def test_weighted_choice_picks_last_on_boundary():
    cards = [_make_card("a"), _make_card("b")]
    result = _weighted_choice(cards, _rng(1.0))
    assert result.id == "b"


def test_dynamic_weight_low_immune_boosts_complication():
    cards = [
        _make_card("comp", theme="complication"),
        _make_card("rec", theme="recovery"),
        _make_card("soc", theme="social"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    state.stats[STAT_IMMUNE] = 20  # Low

    counts = {"comp": 0, "rec": 0, "soc": 0}
    for _ in range(300):
        card = deck.draw(state, _rng(0.3))
        counts[card.id] += 1
    assert counts["comp"] > counts["soc"]


def test_dynamic_weight_low_health_boosts_recovery():
    cards = [
        _make_card("rec", theme="recovery"),
        _make_card("wrk", theme="work"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    state.stats[STAT_HEALTH] = 20  # Critical

    counts = {"rec": 0, "wrk": 0}
    for _ in range(300):
        card = deck.draw(state, _rng(0.3))
        counts[card.id] += 1
    assert counts["rec"] > counts["wrk"]


def test_dynamic_weight_low_sanity_boosts_support():
    cards = [
        _make_card("sup", theme="support"),
        _make_card("fam", theme="family"),
        _make_card("wrk", theme="work"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    state.stats[STAT_SANITY] = 20  # Low

    counts = {"sup": 0, "fam": 0, "wrk": 0}
    for _ in range(300):
        card = deck.draw(state, _rng(0.3))
        counts[card.id] += 1
    assert counts["sup"] + counts["fam"] > counts["wrk"]


def test_dynamic_weight_high_immune_boosts_treatment():
    cards = [
        _make_card("trt", theme="treatment"),
        _make_card("soc", theme="social"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    state.stats[STAT_IMMUNE] = 80  # High

    counts = {"trt": 0, "soc": 0}
    for _ in range(300):
        card = deck.draw(state, _rng(0.3))
        counts[card.id] += 1
    assert counts["trt"] > counts["soc"]


def test_dynamic_weight_normal_stats_balanced():
    import random
    cards = [
        _make_card("trt", theme="treatment"),
        _make_card("soc", theme="social"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    # All stats at 50 (normal)

    rng = random.Random(42)
    counts = {"trt": 0, "soc": 0}
    for _ in range(300):
        card = deck.draw(state, rng.random)
        counts[card.id] += 1
    # Both should be drawn (no extreme bias)
    assert counts["trt"] > 30
    assert counts["soc"] > 30


def test_draw_falls_back_when_theme_cooldown_filters_everything():
    cards = [
        _make_card("a", theme="social"),
        _make_card("b", theme="social"),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()
    state.recent_themes = ["social", "social"]

    card = deck.draw(state, _rng(0.1))
    assert card.id in {"a", "b"}


def test_draw_falls_back_from_empty_pool_to_global_pool():
    cards = [
        _make_card("spring_only", theme="social", pool="spring"),
        _make_card("global", theme="work", pool=None),
    ]
    deck = CardDeck(cards=cards)
    state = new_game_state()

    # No winter cards exist, so draw() should relax the pool constraint.
    card = deck.draw(state, _rng(0.1), pool="winter")
    assert card.id in {"spring_only", "global"}
