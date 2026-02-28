import itertools
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ibd_reigns.deck import CardDeck
from ibd_reigns.engine import new_game_state
from ibd_reigns.schema import load_cards, load_endings


class SeqRng:
    def __init__(self, values):
        self._values = itertools.cycle(values)

    def __call__(self):
        return next(self._values)


@pytest.fixture()
def rng():
    return SeqRng([0.1, 0.9, 0.2, 0.8])


@pytest.fixture()
def cards():
    return load_cards("assets/events.json")


@pytest.fixture()
def endings():
    return {ending.id: ending for ending in load_endings("assets/endings.json")}


@pytest.fixture()
def deck(cards):
    return CardDeck(cards)


@pytest.fixture()
def state():
    return new_game_state()
