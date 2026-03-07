from ibd_reigns.cta import build_cta
from ibd_reigns.engine import build_autopsy, is_fake_win, new_game_state
from ibd_reigns.models import TurnRecord


def test_autopsy_selects_negative_records():
    state = new_game_state()
    state.history = [
        TurnRecord(week=1, card_id="a", option="left", deltas={"HEALTH": -5}, education_id="e1"),
        TurnRecord(week=2, card_id="b", option="left", deltas={"HEALTH": -3}, education_id="e2"),
        TurnRecord(week=3, card_id="c", option="left", deltas={"HEALTH": -1}, education_id="e3"),
    ]
    top = build_autopsy(state, "HEALTH")
    assert len(top) == 3
    assert top[0].card_id == "a"


def test_fake_win_detection():
    state = new_game_state()
    state.week = 53
    state.suppression_turns = 6
    state.history = [TurnRecord(week=i, card_id=str(i), option="left", deltas={}, education_id=None) for i in range(10)]
    assert is_fake_win(state) is True


def test_cta_variants():
    bad = build_cta("bad_sepsis")
    assert "衛教手冊" in bad.actions[0].label
    support = build_cta("bad_dropout")
    assert "IBD" in support.actions[0].label
    good = build_cta("good")
    assert any(action.action_type == "link" for action in good.actions)
