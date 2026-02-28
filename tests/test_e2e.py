from ibd_reigns.constants import FINAL_WEEK
from ibd_reigns.deck import CardDeck
from ibd_reigns.engine import new_game_state, next_card, resolve_turn, run_end_of_year, season_pool_for_week, start_turn
from ibd_reigns.schema import load_cards, load_endings


def test_full_year_simulation(rng):
    cards = load_cards("assets/events.json")
    deck = CardDeck(cards)
    endings = {ending.id: ending for ending in load_endings("assets/endings.json")}
    state = new_game_state()

    while state.week <= FINAL_WEEK and not state.game_over:
        start_turn(state)
        pool = season_pool_for_week(state.week)
        card = next_card(state, deck, rng, pool)
        option = card.left
        resolve_turn(state, deck, card, option, rng)

    if not state.game_over and state.week > FINAL_WEEK:
        ending = run_end_of_year(state, endings)
        assert ending.id in endings
    else:
        assert state.death_reason is not None
