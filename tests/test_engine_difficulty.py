from ibd_reigns.constants import (
    HEALING_LAG_CAP,
    REMISSION_BUFF_TAG,
    REMISSION_BUFF_HEALTH_BONUS,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_SANITY,
    WINTER_START,
    WINTER_IMMUNE_VOLATILITY_MULT,
)
from ibd_reigns.engine import apply_choice, new_game_state
from ibd_reigns.models import Card, CardOption


def test_healing_lag_caps_recovery(deck, rng):
    state = new_game_state()
    state.immune_ideal_streak = 2
    card = deck.get_card("premium_treatment")
    option = card.right
    apply_choice(state, deck, card, option, rng)
    assert state.stats[STAT_HEALTH] <= 50 + HEALING_LAG_CAP


def test_remission_streak_grants_buff(deck, rng):
    state = new_game_state()
    card = deck.get_card("daily_routine")
    option = card.left
    for _ in range(4):
        state.stats[STAT_IMMUNE] = 50
        apply_choice(state, deck, card, option, rng)
    assert REMISSION_BUFF_TAG in state.tags
    assert state.remission_buff_turns > 0


def test_fatigue_stacks(deck, rng):
    state = new_game_state()
    option = CardOption(label="neutral", effect={})
    card = Card(id="neutral", text="t", left=option, right=option)
    state.stats[STAT_SANITY] = 50
    state.week = 10
    apply_choice(state, deck, card, option, rng)
    assert state.stats[STAT_SANITY] < 50


def test_winter_volatility(deck, rng):
    state = new_game_state()
    state.week = WINTER_START
    card = deck.get_card("stop_steroid")
    option = card.left
    base = option.effect[STAT_IMMUNE]
    apply_choice(state, deck, card, option, rng)
    assert state.stats[STAT_IMMUNE] == 50 + int(round(base * WINTER_IMMUNE_VOLATILITY_MULT))


def test_immune_inertia_halves_mild_treatment(deck, rng):
    state = new_game_state()
    state.stats[STAT_IMMUNE] = 80
    card = deck.get_card("mild_treatment")
    apply_choice(state, deck, card, card.left, rng)
    assert state.stats[STAT_IMMUNE] == 80 - 5
