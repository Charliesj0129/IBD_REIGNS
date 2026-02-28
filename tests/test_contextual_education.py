"""Tests for the contextual education engine."""
from ibd_reigns.engine import (
    generate_contextual_education, new_game_state,
    check_milestone_education, generate_micro_tip
)
from ibd_reigns.models import Card, CardOption, Education, CardConditions
from ibd_reigns.constants import (
    FLARE_TAG, STEROID_CUMULATIVE_THRESHOLD, ADHERENCE_POOR_THRESHOLD,
    MALNUTRITION_TAG, SLEEP_DEPRIVED_TAG,
)


def _make_card(card_id="test", theme=None, education=None):
    return Card(
        id=card_id,
        text="test text",
        left=CardOption(label="left"),
        right=CardOption(label="right", effect={"HEALTH": -15, "IMMUNE": 5}),
        theme=theme,
        education=education,
    )


def test_milestone_education_first_flare():
    state = new_game_state()
    card = _make_card()
    option = CardOption(label="x", add_tags=[FLARE_TAG])
    
    edu = check_milestone_education(state, card, option)
    assert edu is not None
    assert edu["severity"] == "critical"
    assert "first_flare" in state.learned_topics
    
    # Second flare should not trigger milestone
    edu2 = check_milestone_education(state, card, option)
    assert edu2 is None


def test_milestone_education_first_steroid():
    state = new_game_state()
    card = _make_card()
    option = CardOption(label="x", steroid_use=True)
    
    edu = check_milestone_education(state, card, option)
    assert edu is not None
    assert "類固醇" in edu["title"]
    assert "first_steroid" in state.learned_topics


def test_milestone_education_surgery():
    state = new_game_state()
    card = _make_card(card_id="surgery_event")
    option = CardOption(label="x")
    
    edu = check_milestone_education(state, card, option)
    assert edu is not None
    assert "手術" in edu["title"]
    assert "first_surgery" in state.learned_topics


def test_micro_tip_generation():
    state = new_game_state()
    state.tags.add(SLEEP_DEPRIVED_TAG)
    
    tip = generate_micro_tip(state)
    assert tip is not None
    assert "睡眠" in tip or "作息" in tip


def test_micro_tip_financial():
    state = new_game_state()
    state.stats["MONEY"] = 10
    
    tip = generate_micro_tip(state)
    assert tip is not None
    assert "重大傷病" in tip


def test_no_education_when_healthy():
    """Healthy state should not trigger contextual education."""
    state = new_game_state()
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is None


def test_flare_triggers_education():
    """Active flare should trigger flare education."""
    state = new_game_state()
    state.tags.add(FLARE_TAG)
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "發作" in result["title"] or "flare" in result["title"].lower()


def test_steroid_overuse_triggers_education():
    """High steroid count triggers steroid education."""
    state = new_game_state()
    state.steroid_use_count = STEROID_CUMULATIVE_THRESHOLD
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "類固醇" in result["title"]


def test_poor_adherence_triggers_education():
    """Poor medication adherence triggers education."""
    state = new_game_state()
    state.medication_doses_offered = 10
    state.medication_doses_taken = 3  # 30% < ADHERENCE_POOR_THRESHOLD
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "順從" in result["title"] or "用藥" in result["title"]


def test_deduplication():
    """Same topic should not be shown twice."""
    state = new_game_state()
    state.tags.add(FLARE_TAG)
    card = _make_card()

    result1 = generate_contextual_education(state, card, card.right)
    assert result1 is not None

    result2 = generate_contextual_education(state, card, card.right)
    assert result2 is None  # Already learned


def test_bad_choice_streak_tracking():
    """Bad choices should increment the streak counter."""
    state = new_game_state()
    card = _make_card()
    # right option has HEALTH: -15, IMMUNE: 5, net = -10, exactly -10 not < -10
    # Make a worse option
    bad_option = CardOption(label="bad", effect={"HEALTH": -20, "IMMUNE": -5})
    card_with_bad = Card(
        id="bad_card", text="bad", left=card.left, right=bad_option,
    )
    generate_contextual_education(state, card_with_bad, bad_option)
    assert state.bad_choice_streak == 1


def test_malnutrition_triggers_education():
    """Malnutrition tag should trigger nutrition education."""
    state = new_game_state()
    state.tags.add(MALNUTRITION_TAG)
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "營養" in result["title"]


def test_sleep_deprivation_triggers_education():
    """Sleep deprivation tag should trigger sleep education."""
    state = new_game_state()
    state.tags.add(SLEEP_DEPRIVED_TAG)
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "睡眠" in result["title"]


def test_poor_diet_triggers_education():
    """Low diet score should trigger diet education."""
    state = new_game_state()
    state.diet_score = -5
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "飲食" in result["title"]


def test_social_isolation_triggers_education():
    """Social isolation tag should trigger social education."""
    state = new_game_state()
    state.tags.add("ISOLATED")
    card = _make_card()
    result = generate_contextual_education(state, card, card.right)
    assert result is not None
    assert "心理" in result["title"] or "社交" in result["title"]
