from ibd_reigns.constants import STAT_IMMUNE
from ibd_reigns.engine import apply_choice, new_game_state


def test_biologic_failure_after_threshold(deck):
    state = new_game_state()
    card = deck.get_card("biologic_start")
    state.biologic_uses["bio_a"] = 10
    # rng returns 0.0 to force failure
    def rng():
        return 0.0
    before = state.stats[STAT_IMMUNE]
    apply_choice(state, deck, card, card.left, rng)
    assert state.stats[STAT_IMMUNE] == before
