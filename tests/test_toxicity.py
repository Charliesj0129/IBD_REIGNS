from ibd_reigns.engine import apply_choice, new_game_state
from ibd_reigns.models import Card, CardOption


def test_toxicity_threshold_triggers_event(deck, rng):
    state = new_game_state()
    option = CardOption(label="Test", effect={}, toxic_delta=100)
    card = Card(id="tox", text="t", left=option, right=option)
    apply_choice(state, deck, card, option, rng)
    assert "megacolon" in state.queued_card_ids
