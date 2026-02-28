"""Tests for Round 3 medical simulation mechanics:
- Malnutrition
- Medication adherence tracking
- Adherence flare risk
- Comorbidity cascade (EIM in deck)
- Enhanced checkup evaluation
- Autopsy report generation
"""
from ibd_reigns.constants import (
    ADHERENCE_POOR_THRESHOLD,
    EIM_TAGS,
    FLARE_TAG,
    MALNUTRITION_HEALTH_THRESHOLD,
    MALNUTRITION_MONEY_THRESHOLD,
    MALNUTRITION_TAG,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_MONEY,
    STAT_SANITY,
)
from ibd_reigns.engine import (
    _apply_malnutrition,
    _track_medication_adherence,
    _apply_adherence_flare_risk,
    build_autopsy_report,
    evaluate_checkup,
    new_game_state,
)
from ibd_reigns.models import Card, CardOption


def _make_card(card_id="test", theme="treatment"):
    return Card(
        id=card_id,
        text="test",
        left=CardOption(label="L", effect={STAT_IMMUNE: -5}),
        right=CardOption(label="R", effect={STAT_IMMUNE: 5}),
        theme=theme,
    )


# --- Malnutrition ---


def test_malnutrition_triggers_when_both_low():
    state = new_game_state()
    state.stats[STAT_HEALTH] = 20
    state.stats[STAT_MONEY] = 15
    _apply_malnutrition(state)
    assert MALNUTRITION_TAG in state.tags


def test_malnutrition_drains_health_and_immune():
    state = new_game_state()
    state.stats[STAT_HEALTH] = 20
    state.stats[STAT_MONEY] = 15
    state.stats[STAT_IMMUNE] = 50
    _apply_malnutrition(state)
    assert state.stats[STAT_HEALTH] < 20  # drained
    assert state.stats[STAT_IMMUNE] > 50  # penalty added (immune instability)


def test_malnutrition_clears_when_stats_recover():
    state = new_game_state()
    state.tags.add(MALNUTRITION_TAG)
    state.stats[STAT_HEALTH] = 60
    state.stats[STAT_MONEY] = 60
    _apply_malnutrition(state)
    assert MALNUTRITION_TAG not in state.tags


def test_malnutrition_no_trigger_if_only_health_low():
    state = new_game_state()
    state.stats[STAT_HEALTH] = 20
    state.stats[STAT_MONEY] = 50
    _apply_malnutrition(state)
    assert MALNUTRITION_TAG not in state.tags


# --- Medication Adherence ---


def test_adherence_tracks_treatment_cards():
    state = new_game_state()
    card = _make_card(theme="treatment")
    option = CardOption(label="Take meds", effect={STAT_IMMUNE: -5})
    _track_medication_adherence(state, card, option)
    assert state.medication_doses_offered == 1
    assert state.medication_doses_taken == 1


def test_adherence_skip_counts_offered_not_taken():
    state = new_game_state()
    card = _make_card(theme="treatment")
    option = CardOption(label="Skip meds", effect={STAT_IMMUNE: 5})
    _track_medication_adherence(state, card, option)
    assert state.medication_doses_offered == 1
    assert state.medication_doses_taken == 0


def test_adherence_ignores_non_treatment():
    state = new_game_state()
    card = _make_card(theme="social")
    option = CardOption(label="L", effect={STAT_IMMUNE: -5})
    _track_medication_adherence(state, card, option)
    assert state.medication_doses_offered == 0


# --- Adherence Flare Risk ---


def test_adherence_flare_risk_triggers_on_poor_adherence():
    state = new_game_state()
    state.medication_doses_offered = 10
    state.medication_doses_taken = 2  # 20% < 50%
    state.flare_cooldown = 0
    _apply_adherence_flare_risk(state, lambda: 0.1)  # below 0.3 threshold
    assert FLARE_TAG in state.tags
    assert "flare_episode" in state.queued_card_ids


def test_adherence_flare_risk_no_trigger_good_adherence():
    state = new_game_state()
    state.medication_doses_offered = 10
    state.medication_doses_taken = 8  # 80% > 50%
    _apply_adherence_flare_risk(state, lambda: 0.1)
    assert FLARE_TAG not in state.tags


def test_adherence_flare_risk_no_trigger_too_few_doses():
    state = new_game_state()
    state.medication_doses_offered = 2
    state.medication_doses_taken = 0
    _apply_adherence_flare_risk(state, lambda: 0.1)
    assert FLARE_TAG not in state.tags


def test_adherence_flare_risk_respects_cooldown():
    state = new_game_state()
    state.medication_doses_offered = 10
    state.medication_doses_taken = 2
    state.flare_cooldown = 3  # on cooldown
    _apply_adherence_flare_risk(state, lambda: 0.1)
    assert FLARE_TAG not in state.tags


# --- Enhanced Checkup ---


def test_checkup_returns_escalate_on_high_immune():
    state = new_game_state()
    state.immune_history = [70, 65, 75, 68, 72, 65, 70, 68, 72, 65, 70, 68, 72]
    assert evaluate_checkup(state) == "escalate"


def test_checkup_returns_concern_on_borderline():
    state = new_game_state()
    state.immune_history = [50, 48, 46, 45, 47, 50, 48, 46, 45, 47, 50, 48, 46]
    state.health_history = [35, 38, 32, 40, 37, 35, 38, 32, 40, 37, 35, 38, 32]
    assert evaluate_checkup(state) == "concern"


def test_checkup_returns_stable_on_good_values():
    state = new_game_state()
    state.immune_history = [40, 42, 38, 41, 39, 40, 42, 38, 41, 39, 40, 42, 38]
    state.health_history = [60, 65, 62, 58, 63, 60, 65, 62, 58, 63, 60, 65, 62]
    assert evaluate_checkup(state) == "stable"


def test_checkup_returns_stable_on_no_history():
    state = new_game_state()
    assert evaluate_checkup(state) == "stable"


# --- Autopsy Report ---


def test_autopsy_report_structure():
    state = new_game_state()
    state.death_reason = "sepsis"
    state.medication_doses_offered = 10
    state.medication_doses_taken = 8
    state.steroid_use_count = 4
    state.tags.add("JOINT_PAIN")
    report = build_autopsy_report(state)
    assert report["fatal_stat"] == "sepsis"
    assert report["adherence_pct"] == 80
    assert report["steroid_uses"] == 4
    assert "JOINT_PAIN" in report["active_eims"]
    assert "final_stats" in report


def test_autopsy_report_worst_cards():
    state = new_game_state()
    from ibd_reigns.models import TurnRecord
    state.death_reason = "sepsis"
    state.history = [
        TurnRecord(week=1, card_id="a", option="left", deltas={STAT_IMMUNE: -10}, education_id=None),
        TurnRecord(week=2, card_id="b", option="right", deltas={STAT_IMMUNE: 5}, education_id=None),
        TurnRecord(week=3, card_id="c", option="left", deltas={STAT_IMMUNE: -15}, education_id=None),
    ]
    report = build_autopsy_report(state)
    card_ids = [c["card_id"] for c in report["worst_cards"]]
    assert "a" in card_ids
    assert "c" in card_ids
    assert "b" not in card_ids


def test_autopsy_report_zero_adherence_when_no_doses():
    state = new_game_state()
    state.death_reason = "unknown"
    report = build_autopsy_report(state)
    assert report["adherence_pct"] == 0


# --- Comorbidity Cascade (Deck) ---


def test_comorbidity_cascade_boosts_complication_weight():
    """Verify EIM tags increase complication card draw probability."""
    from ibd_reigns.deck import CardDeck
    from ibd_reigns.constants import EIM_COMPLICATION_WEIGHT_BONUS
    from ibd_reigns.constants import EIM_COMPLICATION_WEIGHT_BONUS, EIM_TAGS
    cards = [
        Card(id="comp", text="t", left=CardOption(label="L"), right=CardOption(label="R"),
             theme="complication"),
        Card(id="soc", text="t", left=CardOption(label="L"), right=CardOption(label="R"),
             theme="social"),
    ]
    rules = {
        "tag_rules": [{
            "check_tags_any": list(EIM_TAGS),
            "base_mult": 1.0,
            "per_tag_bonus": EIM_COMPLICATION_WEIGHT_BONUS,
            "target_theme": "complication"
        }]
    }
    deck = CardDeck(cards=cards, rules=rules)

    # Without EIMs — draw with a fixed rng, note result
    state_no_eim = new_game_state()
    draws_no = {"comp": 0, "soc": 0}
    import random
    rng1 = random.Random(99)
    for _ in range(200):
        c = deck.draw(state_no_eim, rng1.random)
        draws_no[c.id] += 1

    # With 3 EIMs — same rng seed
    state_eim = new_game_state()
    state_eim.tags.add("JOINT_PAIN")
    state_eim.tags.add("SKIN_EIM")
    state_eim.tags.add("EYE_EIM")
    draws_eim = {"comp": 0, "soc": 0}
    rng2 = random.Random(99)
    for _ in range(200):
        c = deck.draw(state_eim, rng2.random)
        draws_eim[c.id] += 1

    # EIM should increase complication ratio
    ratio_no = draws_no["comp"] / max(1, draws_no["soc"])
    ratio_eim = draws_eim["comp"] / max(1, draws_eim["soc"])
    assert ratio_eim > ratio_no, f"EIM should boost comp ratio: {ratio_eim} vs {ratio_no}"
