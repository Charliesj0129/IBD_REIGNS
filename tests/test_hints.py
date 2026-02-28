from ibd_reigns.hints import hint_stats


def test_hint_shows_impacted_stats(cards):
    card = next(c for c in cards if c.id == "steroid_start")
    stats = hint_stats(card, card.left)
    assert "IMMUNE" in stats


def test_deceptive_hint(cards):
    card = next(c for c in cards if c.id == "placebo")
    stats = hint_stats(card, card.left)
    assert "HEALTH" in stats
