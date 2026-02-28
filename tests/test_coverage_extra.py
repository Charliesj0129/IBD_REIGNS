import json
import tempfile

import pytest

from ibd_reigns.constants import FINAL_WEEK, STAT_HEALTH
from ibd_reigns.deck import CardDeck
from ibd_reigns.engine import (
    apply_choice,
    apply_ending,
    check_final_endoscopy,
    evaluate_checkup,
    handle_surgery_choice,
    is_fake_win,
    new_game_state,
    next_card,
    resolve_turn,
    start_turn,
)
from ibd_reigns.hints import consult
from ibd_reigns.models import Card, CardOption
from ibd_reigns.schema import SchemaError, load_cards
from ibd_reigns.ui import Renderer


def test_weighted_choice_zero_weights(rng):
    option = CardOption(label="l", effect={})
    cards = [Card(id="c1", text="t", left=option, right=option, weight=0), Card(id="c2", text="t", left=option, right=option, weight=0)]
    deck = CardDeck(cards)
    state = new_game_state()
    card = deck.draw(state, rng)
    assert card.id == "c1"


def test_apply_text_overrides_default():
    option = CardOption(label="l", effect={})
    card = Card(id="c", text="default", left=option, right=option)
    deck = CardDeck([card])
    state = new_game_state()
    drawn = deck.draw(state, lambda: 0.0)
    assert drawn.text == "default"


def test_required_and_forbidden_tags_filter(rng):
    option = CardOption(label="l", effect={})
    card = Card(id="c", text="t", left=option, right=option)
    card.conditions.required_tags = ["REQ"]
    card.conditions.forbidden_tags = ["NO"]
    deck = CardDeck([card])
    state = new_game_state()
    with pytest.raises(ValueError):
        deck.draw(state, rng)
    state.tags.add("REQ")
    state.tags.add("NO")
    with pytest.raises(ValueError):
        deck.draw(state, rng)


def test_consult_no_hint():
    option = CardOption(label="l", effect={})
    card = Card(id="c", text="t", left=option, right=option)
    sanity, hint = consult(card, 50)
    assert hint is None
    assert sanity == 50


def test_schema_non_list():
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump({"id": "x"}, handle)
    handle.close()
    with pytest.raises(SchemaError):
        load_cards(handle.name)


def test_start_turn_queues_checkup():
    state = new_game_state()
    state.week = 13
    start_turn(state)
    assert "checkup" in state.queued_card_ids


def test_next_card_uses_queue(deck, rng):
    state = new_game_state()
    state.queued_card_ids.append("daily_routine")
    card = next_card(state, deck, rng, pool=None)
    assert card.id == "daily_routine"


def test_next_card_post_surgery(deck, rng):
    state = new_game_state()
    state.tags.add("POST_SURGERY")
    card = next_card(state, deck, rng, pool="spring")
    assert card.pool == "post_surgery"


def test_resolve_turn_sets_game_over(deck, rng):
    state = new_game_state()
    state.stats[STAT_HEALTH] = -1
    card = deck.get_card("daily_routine")
    resolve_turn(state, deck, card, card.left, rng)
    assert state.game_over is True or "surgery" in state.queued_card_ids


def test_handle_surgery_choice():
    state = new_game_state()
    handle_surgery_choice(state, True)
    assert "POST_SURGERY" in state.tags
    state = new_game_state()
    handle_surgery_choice(state, False)
    assert state.game_over is True


def test_apply_ending(endings):
    state = new_game_state()
    apply_ending(state, endings, "deep_remission")
    assert state.allow_new_game_plus is True


def test_is_fake_win_false():
    state = new_game_state()
    state.week = FINAL_WEEK
    assert is_fake_win(state) is False


def test_check_final_endoscopy_no_history():
    state = new_game_state()
    state.stats[STAT_HEALTH] = 90
    assert check_final_endoscopy(state) == "deep_remission"


def test_evaluate_checkup_no_history():
    state = new_game_state()
    assert evaluate_checkup(state) == "stable"


def test_renderer_feedback_and_disclaimer():
    renderer = Renderer()
    renderer.feedback("msg", blocking=True)
    renderer.disclaimer("disc")
    assert renderer.calls[0].name == "feedback"
    assert renderer.calls[1].name == "disclaimer"
