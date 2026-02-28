from ibd_reigns.hints import consult
from ibd_reigns.models import Card, CardOption


def test_consult_returns_hint():
    card = Card(id="c", text="t", left=CardOption(label="l", effect={}), right=CardOption(label="r", effect={}), consult_hint="hint")
    sanity, hint = consult(card, 50)
    assert hint == "hint"
    assert sanity < 50
