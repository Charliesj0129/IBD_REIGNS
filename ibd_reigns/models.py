from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .constants import STATS


@dataclass
class CardConditions:
    min_week: Optional[int] = None
    max_week: Optional[int] = None
    min_immune: Optional[int] = None
    max_immune: Optional[int] = None
    required_tags: List[str] = field(default_factory=list)
    forbidden_tags: List[str] = field(default_factory=list)


@dataclass
class Education:
    title: str
    content: str
    source: str
    image_url: Optional[str] = None


@dataclass
class CardOption:
    label: str
    effect: Dict[str, int] = field(default_factory=dict)
    add_tags: List[str] = field(default_factory=list)
    remove_tags: List[str] = field(default_factory=list)
    impact: Optional[List[str]] = None
    response_text: Optional[str] = None
    cost_money: Optional[int] = None
    consult_hint: Optional[str] = None
    consult_cost_sanity: Optional[int] = None
    toxic_delta: int = 0
    symptom_suppression: bool = False
    steroid_use: bool = False
    stop_steroid: bool = False
    biologic_id: Optional[str] = None
    induction_start: bool = False
    injection_required: bool = False
    missed_injection: bool = False
    mild_treatment: bool = False
    risk_tags: List[str] = field(default_factory=list)
    risk_event_id: Optional[str] = None
    # --- Round 4 Fields ---
    diet_delta: int = 0
    ostomy_skill_delta: int = 0


@dataclass
class Card:
    id: str
    text: str
    left: CardOption
    right: CardOption
    emoji: Optional[str] = None
    character_name: Optional[str] = None
    character_role: Optional[str] = None
    chain_next: List[str] = field(default_factory=list)
    theme: Optional[str] = None
    rarity: Optional[str] = None
    conditions: CardConditions = field(default_factory=CardConditions)
    weight: int = 1
    education: Optional[Education] = None
    hint_deceptive: bool = False
    educational: bool = False
    consult_hint: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    text_overrides: Dict[str, str] = field(default_factory=dict)
    forced: bool = False
    only_one_option: bool = False
    pool: Optional[str] = None


@dataclass
class Ending:
    id: str
    title: str
    trigger: str
    description: str
    tier: Optional[str] = None
    cta_type: Optional[str] = None


@dataclass
class TurnRecord:
    week: int
    card_id: str
    option: str
    deltas: Dict[str, int]
    education_id: Optional[str]


@dataclass
class GameState:
    week: int
    stats: Dict[str, int]
    max_caps: Dict[str, int]
    tags: Set[str] = field(default_factory=set)
    history: List[TurnRecord] = field(default_factory=list)
    active_card_id: Optional[str] = None
    last_card_id: Optional[str] = None
    game_over: bool = False
    death_reason: Optional[str] = None
    queued_card_ids: List[str] = field(default_factory=list)
    scheduled_card_ids: Dict[int, List[str]] = field(default_factory=dict)
    toxic: int = 0
    immune_ideal_streak: int = 0
    remission_buff_turns: int = 0
    biologic_uses: Dict[str, int] = field(default_factory=dict)
    resistance: int = 0
    used_steroid_last_turn: bool = False
    suppression_turns: int = 0
    health_history: List[int] = field(default_factory=list)
    immune_history: List[int] = field(default_factory=list)
    recent_themes: List[str] = field(default_factory=list)
    ending: Optional[Ending] = None
    allow_new_game_plus: bool = False
    available_perks: List[str] = field(default_factory=list)
    # --- New Medical Simulation Fields ---
    steroid_use_count: int = 0              # Cumulative steroid uses
    medication_doses_taken: int = 0         # Total prescribed doses taken
    medication_doses_offered: int = 0       # Total prescribed doses offered
    flare_cooldown: int = 0                 # Turns until next flare can trigger
    sleep_deprived_turns: int = 0           # Remaining sleep deprivation debuff turns
    # --- Round 4 Fields ---
    diet_score: int = 0                     # -10 to +10, tracks dietary habits
    ostomy_care_skill: int = 0              # 0 to 10, tracks proficiency with stoma appliance
    # --- Round 5 Fields ---
    social_isolation_counter: int = 0       # Tracks consecutive social rejections
    milestones: List[str] = field(default_factory=list) # Significant event log
    # --- Education Tracking ---
    learned_topics: Set[str] = field(default_factory=set)  # Education titles already shown
    bad_choice_streak: int = 0              # Consecutive risky/negative decisions

    def clamp_stats(self) -> None:
        for stat in STATS:
            cap = self.max_caps.get(stat, 100)
            val = self.stats.get(stat, 0)
            if val < 0:
                val = 0
            if val > cap:
                val = cap
            self.stats[stat] = val
