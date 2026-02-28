from ibd_reigns.constants import STAT_HEALTH
from ibd_reigns.engine import resolve_turn, new_game_state


def test_perforation_queues_surgery(deck, rng):
    state = new_game_state()
    state.stats[STAT_HEALTH] = 1
    card = deck.get_card("overconfidence")
    resolve_turn(state, deck, card, card.left, rng)
    assert "surgery" in state.queued_card_ids
    assert state.game_over is False
