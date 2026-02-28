from ibd_reigns.engine import apply_choice, new_game_state


def test_checkup_escalates(deck, rng):
    state = new_game_state()
    state.immune_history = [70] * 13
    card = deck.get_card("checkup")
    apply_choice(state, deck, card, card.left, rng)
    assert "TREATMENT_ESCALATED" in state.tags
