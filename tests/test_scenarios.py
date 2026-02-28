from ibd_reigns.schema import load_cards
import os

def test_load_scenarios():
    path = "assets/scenarios_expansion.json"
    assert os.path.exists(path)
    cards = load_cards(path)
    assert len(cards) > 0
    
    # Check specific cards
    card_ids = {c.id for c in cards}
    assert "work_overtime_flare" in card_ids
    assert "family_plan" in card_ids
    
    # Check education content 
    travel_edu = next((c for c in cards if c.id == "travel_meds_timezone"), None)
    assert travel_edu is not None
    assert travel_edu.education is not None
    assert "時區" in travel_edu.education.title

def test_load_all_cards():
    cards = load_cards(["assets/events.json", "assets/scenarios_expansion.json"])
    assert len(cards) > 0
    # Ensure no duplicate IDs across files (though schema doesn't strictly forbid it, it's bad practice)
    ids = [c.id for c in cards]
    assert len(ids) == len(set(ids))
