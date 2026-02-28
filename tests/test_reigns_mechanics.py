from unittest.mock import MagicMock
from ibd_reigns.engine import check_death, OVERCONFIDENCE_HEALTH_RESET
from ibd_reigns.models import GameState, Card
from ibd_reigns.deck import apply_text_overrides
from ibd_reigns.constants import STAT_HEALTH, STAT_IMMUNE, STAT_SANITY, STAT_MONEY

def test_health_100_death():
    state = GameState(week=1, stats={STAT_HEALTH: 100, STAT_IMMUNE: 50, STAT_SANITY: 50, STAT_MONEY: 50}, max_caps={STAT_HEALTH: 100})
    death = check_death(state)
    assert death == "false_confidence"

def test_health_99_alive():
    state = GameState(week=1, stats={STAT_HEALTH: 99, STAT_IMMUNE: 50, STAT_SANITY: 50, STAT_MONEY: 50}, max_caps={STAT_HEALTH: 100})
    death = check_death(state)
    assert death is None

