import json
import tempfile

import pytest

from ibd_reigns.schema import SchemaError, load_cards, load_endings


def _write_json(payload):
    handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
    json.dump(payload, handle)
    handle.close()
    return handle.name


def test_load_cards_valid():
    path = _write_json([
        {"id": "c1", "text": "t", "left": {"label": "l", "effect": {}}, "right": {"label": "r", "effect": {}}}
    ])
    cards = load_cards(path)
    assert cards[0].id == "c1"


def test_load_cards_missing_fields():
    path = _write_json([{"id": "c1", "left": {"label": "l", "effect": {}}, "right": {"label": "r", "effect": {}}}])
    with pytest.raises(SchemaError):
        load_cards(path)


def test_load_endings_valid():
    path = _write_json([
        {"id": "e1", "title": "t", "trigger": "x", "description": "d"}
    ])
    endings = load_endings(path)
    assert endings[0].id == "e1"


def test_load_endings_missing_fields():
    path = _write_json([{"id": "e1", "title": "t"}])
    with pytest.raises(SchemaError):
        load_endings(path)
