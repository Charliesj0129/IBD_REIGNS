from ibd_reigns.constants import STAT_IMMUNE
from ibd_reigns.engine import apply_choice, new_game_state


def test_steroid_rebound(deck, rng):
    state = new_game_state()
    start_card = deck.get_card("steroid_start")
    stop_card = deck.get_card("stop_steroid")
    apply_choice(state, deck, start_card, start_card.left, rng)
    immune_after_steroid = state.stats[STAT_IMMUNE]
    apply_choice(state, deck, stop_card, stop_card.left, rng)
    assert state.stats[STAT_IMMUNE] > immune_after_steroid


def test_induction_schedule(deck, rng):
    state = new_game_state()
    card = deck.get_card("biologic_start")
    apply_choice(state, deck, card, card.left, rng)
    assert state.scheduled_card_ids
    assert state.week + 1 in state.scheduled_card_ids or state.week + 5 in state.scheduled_card_ids


def test_missed_injection_increases_resistance(deck, rng):
    state = new_game_state()
    card = deck.get_card("biologic_injection")
    apply_choice(state, deck, card, card.right, rng)
    assert state.resistance >= 50


def test_opportunistic_infection_queue(deck, rng):
    state = new_game_state()
    state.stats[STAT_IMMUNE] = 10
    card = deck.get_card("daily_routine")
    apply_choice(state, deck, card, card.left, rng, infection_prob=1.0)
    assert "infection" in state.queued_card_ids


def test_drug_interaction_triggers_bleeding(deck, rng):
    state = new_game_state()
    state.tags.add("ANTICOAGULANT")
    card = deck.get_card("supplement_risk")
    apply_choice(state, deck, card, card.left, rng)
    assert "bleeding" in state.queued_card_ids
