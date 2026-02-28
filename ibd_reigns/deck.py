from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from .constants import (
    RARITY_WEIGHTS,
    RECENT_CARD_EXCLUDE,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_MONEY,
    STAT_SANITY,
    THEME_COOLDOWN,
    WINTER_END,
    WINTER_START,
)
from .models import Card, GameState


RngFunc = Callable[[], float]


def _weighted_choice(cards: Sequence[Card], rng: RngFunc, weights: Optional[Sequence[int]] = None) -> Card:
    if weights is None:
        weights = [card.weight for card in cards]
    total = sum(max(weight, 0) for weight in weights)
    if total <= 0:
        return cards[0]
    pick = rng() * total
    upto = 0
    for card, weight in zip(cards, weights):
        upto += max(weight, 0)
        if pick <= upto:
            return card
    return cards[-1]


def apply_text_overrides(card: Card, tags: Iterable[str], base_text: Optional[str] = None) -> str:
    text = base_text or card.text
    for tag in tags:
        if tag in card.text_overrides:
            text = card.text_overrides[tag]
            break
    return text


@dataclass
class CardDeck:
    cards: List[Card]
    post_surgery_pool: Optional[str] = None
    rules: Dict[str, Any] = field(default_factory=dict)

    def _eligible(self, state: GameState, pool: Optional[str], *, ignore_theme_cooldown: bool = False) -> List[Card]:
        eligible: List[Card] = []
        for card in self.cards:
            if pool == "post_surgery":
                if card.pool != "post_surgery":
                    continue
            elif pool and card.pool not in (pool, None):
                continue
            if card.conditions.min_week is not None and state.week < card.conditions.min_week:
                continue
            if card.conditions.max_week is not None and state.week > card.conditions.max_week:
                continue
            immune = state.stats.get(STAT_IMMUNE, 0)
            if card.conditions.min_immune is not None and immune < card.conditions.min_immune:
                continue
            if card.conditions.max_immune is not None and immune > card.conditions.max_immune:
                continue
            if card.conditions.required_tags and not set(card.conditions.required_tags).issubset(state.tags):
                continue
            if card.conditions.forbidden_tags and set(card.conditions.forbidden_tags) & state.tags:
                continue
            if (not ignore_theme_cooldown) and card.theme and card.theme in state.recent_themes[-THEME_COOLDOWN:]:
                continue
            eligible.append(card)
        return eligible

    def draw(self, state: GameState, rng: RngFunc, pool: Optional[str] = None) -> Card:
        eligible = self._eligible(state, pool)
        if not eligible:
            eligible = self._eligible(state, pool, ignore_theme_cooldown=True)
        if not eligible and pool is not None:
            eligible = self._eligible(state, None)
        if not eligible and pool is not None:
            eligible = self._eligible(state, None, ignore_theme_cooldown=True)
        if not eligible:
            raise ValueError("No eligible cards")
        if state.history:
            recent_ids = [record.card_id for record in state.history[-RECENT_CARD_EXCLUDE:]]
            eligible = [card for card in eligible if card.id not in recent_ids] or eligible
        weights = None
        if WINTER_START <= state.week <= WINTER_END:
            weights = [card.weight + 1 if "joint_pain" in card.tags else card.weight for card in eligible]
        if weights is None:
            weights = [card.weight for card in eligible]
        
        # 1. Base weights adjusted by Rarity
        weights = [
            weight * RARITY_WEIGHTS.get(card.rarity or "common", 1.0) for card, weight in zip(eligible, weights)
        ]

        # 2. Chapter/Season Theme Weights (Data-Driven)
        chapter_weights_config = self.rules.get("chapter_theme_weights", {})
        chapter_weights = chapter_weights_config.get(pool or "spring", {})
        weights = [
            weight * chapter_weights.get(card.theme or "misc", 1.0) for card, weight in zip(eligible, weights)
        ]

        # 3. Dynamic Stat Rules (Data-Driven)
        # Apply multipliers based on stat conditions
        for rule in self.rules.get("stat_rules", []):
            conditions_met = True
            for cond in rule.get("conditions", []):
                stat_val = state.stats.get(cond["stat"], 50)  # default to 50 if missing
                op = cond["op"]
                target = cond["value"]
                
                if op == "gt" and not (stat_val > target):
                    conditions_met = False
                    break
                elif op == "lt" and not (stat_val < target):
                    conditions_met = False
                    break
                # add eq/gte/lte if needed, currently only gt/lt used
            
            if conditions_met:
                for mod in rule.get("modifiers", []):
                    multiplier = mod["mult"]
                    target_themes = set(mod["themes"])
                    for i, card in enumerate(eligible):
                        if (card.theme or "misc") in target_themes:
                            weights[i] *= multiplier

        # 4. Tag Rules (Data-Driven, e.g. Comorbidity)
        for rule in self.rules.get("tag_rules", []):
            check_tags = set(rule.get("check_tags_any", []))
            active_count = len(check_tags & state.tags)
            
            if active_count > 0:
                base_mult = rule.get("base_mult", 1.0)
                bonus = rule.get("per_tag_bonus", 0.0)
                final_mult = base_mult + (active_count * bonus)
                target_theme = rule.get("target_theme")
                
                for i, card in enumerate(eligible):
                    if (card.theme or "misc") == target_theme:
                        weights[i] *= final_mult

        return _weighted_choice(eligible, rng, weights=weights)

    def get_card(self, card_id: str) -> Card:
        for card in self.cards:
            if card.id == card_id:
                return card
        raise KeyError(card_id)

    def filter_by_tag(self, tag: str) -> List[Card]:
        return [card for card in self.cards if tag in card.tags]

    def options_locked(self, state: GameState, card: Card) -> Dict[str, Optional[str]]:
        locks: Dict[str, Optional[str]] = {"left": None, "right": None}
        if card.only_one_option:
            locks["right"] = "強制行動"
        for side, option in ("left", card.left), ("right", card.right):
            if option.cost_money is not None:
                if state.stats.get("MONEY", 0) < option.cost_money:
                    locks[side] = "資金不足"
        return locks
