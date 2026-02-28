import json
import tempfile

import pytest

from ibd_reigns.constants import STAT_HEALTH, STAT_IMMUNE
from ibd_reigns.deck import CardDeck, apply_text_overrides, _weighted_choice
from ibd_reigns.engine import apply_choice, apply_ending, new_game_state, run_end_of_year
from ibd_reigns.hints import hint_stats
from ibd_reigns.models import Card, CardConditions, CardOption
from ibd_reigns.schema import load_cards, load_endings
from ibd_reigns.ui import Renderer


def test_weighted_choice_fallback():
    option = CardOption(label="l", effect={})
    cards = [Card(id="c1", text="t", left=option, right=option, weight=1), Card(id="c2", text="t", left=option, right=option, weight=1)]
    def rng():
        return 2.0
    chosen = _weighted_choice(cards, rng, weights=[1, 1])
    assert chosen.id == "c2"


def test_apply_text_overrides_no_match():
    option = CardOption(label="l", effect={})
    card = Card(id="c", text="default", left=option, right=option)
    assert apply_text_overrides(card, {"OTHER"}) == "default"


def test_conditions_min_max_filter():
    option = CardOption(label="l", effect={})
    card = Card(id="c", text="t", left=option, right=option)
    card.conditions = CardConditions(min_week=5, max_week=6, min_immune=40, max_immune=60)
    deck = CardDeck([card])
    state = new_game_state()
    state.week = 4
    with pytest.raises(ValueError):
        deck.draw(state, lambda: 0.0)
    state.week = 5
    state.stats[STAT_IMMUNE] = 30
    with pytest.raises(ValueError):
        deck.draw(state, lambda: 0.0)
    state.stats[STAT_IMMUNE] = 70
    with pytest.raises(ValueError):
        deck.draw(state, lambda: 0.0)


def test_get_card_keyerror(deck):
    with pytest.raises(KeyError):
        deck.get_card("missing")


def test_filter_by_tag(deck):
    tagged = deck.filter_by_tag("winter")
    assert isinstance(tagged, list)


def test_option_lock_sufficient_money(deck):
    state = new_game_state()
    card = deck.get_card("premium_treatment")
    state.stats["MONEY"] = 100
    locks = deck.options_locked(state, card)
    assert locks["right"] is None


def test_remission_buff_applies(deck):
    state = new_game_state()
    state.remission_buff_turns = 1
    option = CardOption(label="x", effect={})
    card = Card(id="buff", text="t", left=option, right=option)
    apply_choice(state, deck, card, option, lambda: 0.0)
    assert state.stats[STAT_HEALTH] > 50


def test_stop_steroid_no_negative_delta(deck):
    state = new_game_state()
    state.used_steroid_last_turn = True
    option = CardOption(label="x", effect={STAT_IMMUNE: 5}, stop_steroid=True)
    card = Card(id="stop", text="t", left=option, right=option)
    apply_choice(state, deck, card, option, lambda: 0.0)
    assert state.stats[STAT_IMMUNE] == 55


def test_symptom_suppression_branch(deck):
    state = new_game_state()
    option = CardOption(label="x", effect={}, symptom_suppression=True)
    card = Card(id="supp", text="t", left=option, right=option)
    apply_choice(state, deck, card, option, lambda: 0.0)
    assert state.suppression_turns == 1


def test_remove_tags_branch(deck):
    state = new_game_state()
    state.tags.add("TEMP")
    option = CardOption(label="x", effect={}, remove_tags=["TEMP"])
    card = Card(id="remove", text="t", left=option, right=option)
    apply_choice(state, deck, card, option, lambda: 0.0)
    assert "TEMP" not in state.tags


def test_apply_ending_non_top(endings):
    state = new_game_state()
    apply_ending(state, endings, "clinical_remission")
    assert state.allow_new_game_plus is False


def test_run_end_of_year_fake_win(endings):
    state = new_game_state()
    state.week = 60
    state.suppression_turns = 10
    state.history = []
    ending = run_end_of_year(state, endings)
    assert ending.id == "bad_end"


def test_hint_deceptive_branch():
    option = CardOption(label="x", effect={"HEALTH": 0})
    card = Card(id="h", text="t", left=option, right=option, hint_deceptive=True)
    stats = hint_stats(card, option)
    assert "HEALTH" in stats


def test_schema_with_education_and_endings():
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump([
        {
            "id": "c1",
            "text": "t",
            "left": {"label": "l", "effect": {}},
            "right": {"label": "r", "effect": {}},
            "education": {"title": "ed", "content": "c", "source": "s"}
        }
    ], handle)
    handle.close()
    cards = load_cards(handle.name)
    assert cards[0].education is not None

    handle2 = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump([{"id": "e", "title": "t", "trigger": "x", "description": "d", "tier": "top"}], handle2)
    handle2.close()
    endings = load_endings(handle2.name)
    assert endings[0].tier == "top"


def test_schema_endings_non_list():
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump({"id": "e"}, handle)
    handle.close()
    with pytest.raises(Exception):
        load_endings(handle.name)


def test_schema_card_item_not_dict():
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump(["bad"], handle)
    handle.close()
    with pytest.raises(Exception):
        load_cards(handle.name)


def test_schema_ending_item_not_dict():
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump(["bad"], handle)
    handle.close()
    with pytest.raises(Exception):
        load_endings(handle.name)


def test_renderer_card_text():
    renderer = Renderer()
    renderer.card_text("text")
    assert renderer.calls[0].name == "card_text"


def test_clamp_above_cap():
    state = new_game_state()
    state.stats[STAT_HEALTH] = 150
    state.clamp_stats()
    assert state.stats[STAT_HEALTH] == 100
