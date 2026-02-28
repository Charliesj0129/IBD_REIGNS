from ibd_reigns.constants import (
    OVERCONFIDENCE_HEALTH_RESET,
    OVERCONFIDENCE_IMMUNE_SPIKE,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_MONEY,
    STAT_SANITY,
)
from ibd_reigns.engine import apply_choice, check_death, new_game_state
from ibd_reigns.models import Card, CardOption


def test_clamp_stats(deck, rng):
    state = new_game_state()
    state.stats[STAT_HEALTH] = -10
    state.clamp_stats()
    assert state.stats[STAT_HEALTH] == 0


def test_death_conditions():
    state = new_game_state()
    state.stats[STAT_IMMUNE] = 0
    assert check_death(state) == "infection"
    state.stats[STAT_IMMUNE] = 100
    assert check_death(state) == "flare_storm"
    state.stats[STAT_IMMUNE] = 50
    state.stats[STAT_HEALTH] = 0
    assert check_death(state) == "perforation"
    assert check_death(state) == "perforation"
    state.stats[STAT_HEALTH] = 100
    assert check_death(state) == "false_confidence"
    state.stats[STAT_HEALTH] = 50
    state.stats[STAT_SANITY] = 0
    assert check_death(state) == "give_up"
    state.stats[STAT_SANITY] = 100
    assert check_death(state) == "burnout"
    state.stats[STAT_SANITY] = 50
    state.stats[STAT_MONEY] = 0
    assert check_death(state) == "financial_toxicity"
    state.stats[STAT_MONEY] = 100
    assert check_death(state) == "workaholic"





def test_coupling_stress_to_immune(deck, rng):
    state = new_game_state()
    option = CardOption(label="stress", effect={STAT_SANITY: -20})
    card = Card(id="stress", text="t", left=option, right=option)
    apply_choice(state, deck, card, option, rng)
    assert state.stats[STAT_IMMUNE] > 50


def test_coupling_immune_to_health(deck, rng):
    state = new_game_state()
    card = deck.get_card("stop_steroid")
    option = card.right
    apply_choice(state, deck, card, option, rng)
    assert state.stats[STAT_HEALTH] <= 50
