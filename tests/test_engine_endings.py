from ibd_reigns.engine import (
    check_final_endoscopy,
    resolve_turn,
    run_end_of_year,
    new_game_state,
)
from ibd_reigns.constants import FINAL_WEEK, STAT_HEALTH


def test_immediate_death_sets_reason(deck, rng):
    state = new_game_state()
    state.stats[STAT_HEALTH] = 1
    card = deck.get_card("overconfidence")
    resolve_turn(state, deck, card, card.left, rng)
    assert state.game_over or "surgery" in state.queued_card_ids


def test_final_endoscopy_scoring(state):
    state.health_history = [90, 85, 88]
    assert check_final_endoscopy(state) == "deep_remission"
    state.health_history = [60, 55, 58]
    assert check_final_endoscopy(state) == "clinical_remission"
    state.health_history = [40, 45, 42]
    assert check_final_endoscopy(state) == "treatment_failure"


def test_run_end_of_year(endings, state):
    state.week = FINAL_WEEK + 1
    state.health_history = [90, 90, 90]
    ending = run_end_of_year(state, endings)
    assert ending.id == "deep_remission"
    assert state.allow_new_game_plus is True
