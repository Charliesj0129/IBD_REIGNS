from ibd_reigns.constants import STAT_IMMUNE, STAT_MONEY
from ibd_reigns.engine import apply_choice, new_game_state


def test_anemia_reduces_money_gain(deck, rng):
    state = new_game_state()
    state.tags.add("ANEMIA")
    card = deck.get_card("daily_routine")
    option = card.right
    apply_choice(state, deck, card, option, rng)
    assert state.stats[STAT_MONEY] < 60


def test_steroid_dependence_raises_immune(deck, rng):
    state = new_game_state()
    state.tags.add("STEROID_DEPENDENT")
    card = deck.get_card("daily_routine")
    apply_choice(state, deck, card, card.left, rng)
    assert state.stats[STAT_IMMUNE] > 50
