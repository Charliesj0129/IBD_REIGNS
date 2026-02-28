from ibd_reigns.constants import SCAR_CAP_REDUCTION, STAT_HEALTH
from ibd_reigns.engine import apply_choice, new_game_state


def test_scar_accumulation_reduces_cap(deck, rng):
    state = new_game_state()
    card = deck.get_card("overconfidence")
    option = card.left
    state.stats[STAT_HEALTH] = 15
    previous_cap = state.max_caps[STAT_HEALTH]
    apply_choice(state, deck, card, option, rng)
    assert state.max_caps[STAT_HEALTH] == previous_cap - SCAR_CAP_REDUCTION
