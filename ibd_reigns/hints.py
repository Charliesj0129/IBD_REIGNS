from typing import List

from .models import Card, CardOption


def hint_stats(card: Card, option: CardOption) -> List[str]:
    if option.impact:
        return list(option.impact)
    if card.hint_deceptive and option.effect:
        return list(option.effect.keys())
    return list(option.effect.keys())


def consult(card: Card, sanity: int) -> tuple[int, str | None]:
    if not card.consult_hint:
        return sanity, None
    cost = 5
    return sanity - cost, card.consult_hint
