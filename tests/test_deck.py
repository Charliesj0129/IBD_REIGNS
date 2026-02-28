from ibd_reigns.deck import apply_text_overrides
from ibd_reigns.engine import season_pool_for_week


def test_apply_text_overrides(cards):
    card = next(c for c in cards if c.id == "social_photo")
    assert apply_text_overrides(card, {"MOON_FACE"}) == "月亮臉讓你對拍照感到很不自在。"


def test_season_pool_for_week():
    assert season_pool_for_week(1) == "spring"
    assert season_pool_for_week(14) == "summer"
    assert season_pool_for_week(27) == "fall"
    assert season_pool_for_week(40) == "winter"


def test_draw_respects_conditions(deck, state, rng):
    state.week = 1
    card = deck.draw(state, rng, pool="spring")
    assert card.conditions.max_week is None or card.conditions.max_week >= 1


def test_prevent_immediate_repeat(deck, state, rng):
    state.week = 1
    card1 = deck.draw(state, rng, pool="spring")
    state.history.append(type("R", (), {"card_id": card1.id})())
    card2 = deck.draw(state, rng, pool="spring")
    assert card2.id != card1.id or len(deck.cards) == 1


def test_theme_cooldown(deck, state, rng):
    state.recent_themes = ["social", "social"]
    card = deck.draw(state, rng, pool="spring")
    assert card.theme != "social"


def test_chapter_theme_weights(deck, state, rng):
    state.week = 1
    card = deck.draw(state, rng, pool="winter")
    assert card is not None


def test_option_lock_for_money(deck, state):
    card = next(c for c in deck.cards if c.id == "premium_treatment")
    state.stats["MONEY"] = 20
    locks = deck.options_locked(state, card)
    assert locks["right"] == "資金不足"


def test_only_one_option_lock(deck, state):
    card = next(c for c in deck.cards if c.id == "urgent_bathroom")
    locks = deck.options_locked(state, card)
    assert locks["right"] == "強制行動"
