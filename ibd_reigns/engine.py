from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict, List, Optional, Tuple

from .constants import (
    ADHERENCE_POOR_FLARE_PROB,
    ADHERENCE_POOR_THRESHOLD,
    BASE_FATIGUE_DRAIN,
    BIOLOGIC_FAILURE_PROB,
    BIOLOGIC_RESISTANCE_THRESHOLD,
    CHECKUP_WEEKS,
    DEFAULT_STATS,
    DEATH_ENDINGS,
    DIET_HEALING_BONUS,
    DIET_HIGH_THRESHOLD,
    DIET_IMMUNE_PENALTY,
    DIET_LOW_THRESHOLD,
    FATIGUE_GROWTH_PER_WEEK,
    FINAL_WEEK,
    FLARE_COOLDOWN_TURNS,
    FLARE_HEALTH_DRAIN,
    FLARE_IMMUNE_THRESHOLD,
    FLARE_SANITY_DRAIN,
    FLARE_TAG,
    GUT_BRAIN_HEALTH_THRESHOLD,
    GUT_BRAIN_SANITY_MULT,
    HEALING_LAG_CAP,
    IMMUNE_DAMAGE_HEALTH_DELTA,
    IMMUNE_DAMAGE_THRESHOLD,
    IMMUNE_IDEAL_MAX,
    IMMUNE_IDEAL_MIN,
    INFECTION_PROB_DEFAULT,
    MALNUTRITION_HEALTH_DRAIN,
    MALNUTRITION_HEALTH_THRESHOLD,
    MALNUTRITION_IMMUNE_PENALTY,
    MALNUTRITION_MONEY_THRESHOLD,
    MALNUTRITION_TAG,
    OSTOMY_CARE_THRESHOLD,
    OSTOMY_LEAK_PROB_BASE,
    OSTOMY_LEAK_SANITY_DRAIN,
    OSTOMY_TAG,
    OVERCONFIDENCE_HEALTH_RESET,
    OVERCONFIDENCE_IMMUNE_SPIKE,
    REMISSION_BUFF_DURATION,
    REMISSION_BUFF_HEALTH_BONUS,
    REMISSION_BUFF_TAG,
    REMISSION_STREAK_TARGET,
    SCAR_CAP_REDUCTION,
    SCAR_THRESHOLD,
    SEASON_CHANGE_IMMUNE_JITTER,
    SEASON_CHANGE_WEEKS,
    SLEEP_DEPRIVED_IMMUNE_PENALTY,
    SLEEP_DEPRIVED_SANITY_DRAIN,
    SLEEP_DEPRIVED_TAG,
    STAT_HEALTH,
    STAT_IMMUNE,
    STAT_MONEY,
    STAT_SANITY,
    STEROID_BONE_LOSS_REDUCTION,
    STEROID_BONE_LOSS_THRESHOLD,
    STEROID_CUMULATIVE_THRESHOLD,
    STEROID_DEPENDENCE_IMMUNE_RISE,
    STEROID_MOON_FACE_TAG,
    STRESS_COUPLING_IMMUNE_DELTA,
    STRESS_COUPLING_THRESHOLD,
    TOXICITY_RESET,
    TOXICITY_THRESHOLD,
    WINTER_END,
    WINTER_IMMUNE_VOLATILITY_MULT,
    WINTER_START,
)
from .deck import CardDeck
from .models import Card, CardOption, Ending, GameState, TurnRecord


RngFunc = Callable[[], float]


def new_game_state() -> GameState:
    return GameState(
        week=1,
        stats=dict(DEFAULT_STATS),
        max_caps={STAT_HEALTH: 100, STAT_IMMUNE: 100, STAT_SANITY: 100, STAT_MONEY: 100},
    )


def is_immune_ideal(value: int) -> bool:
    return IMMUNE_IDEAL_MIN <= value <= IMMUNE_IDEAL_MAX


def season_pool_for_week(week: int) -> str:
    if week <= 13:
        return "spring"
    if week <= 26:
        return "summer"
    if week <= 39:
        return "fall"
    return "winter"


def _apply_winter_volatility(state: GameState, deltas: Dict[str, int]) -> Dict[str, int]:
    if WINTER_START <= state.week <= WINTER_END and STAT_IMMUNE in deltas:
        immune_delta = deltas[STAT_IMMUNE]
        if immune_delta:
            adjusted = int(round(immune_delta * WINTER_IMMUNE_VOLATILITY_MULT))
            deltas = dict(deltas)
            deltas[STAT_IMMUNE] = adjusted
    return deltas


def _apply_mild_treatment_inertia(state: GameState, option: CardOption, deltas: Dict[str, int]) -> Dict[str, int]:
    if state.stats.get(STAT_IMMUNE, 0) > 75 and option.mild_treatment:
        if STAT_IMMUNE in deltas:
            deltas = dict(deltas)
            deltas[STAT_IMMUNE] = int(deltas[STAT_IMMUNE] * 0.5)
    return deltas


def _apply_healing_lag(state: GameState, deltas: Dict[str, int]) -> Dict[str, int]:
    if STAT_HEALTH in deltas and deltas[STAT_HEALTH] > 0:
        if state.immune_ideal_streak >= 2:
            deltas = dict(deltas)
            deltas[STAT_HEALTH] = min(deltas[STAT_HEALTH], HEALING_LAG_CAP)
    return deltas


def _apply_tag_modifiers(state: GameState, deltas: Dict[str, int]) -> Dict[str, int]:
    if "ANEMIA" in state.tags and STAT_MONEY in deltas and deltas[STAT_MONEY] > 0:
        deltas = dict(deltas)
        deltas[STAT_MONEY] = int(deltas[STAT_MONEY] * 0.5)
    return deltas


def _apply_coupling(state: GameState, deltas: Dict[str, int]) -> Dict[str, int]:
    extra: Dict[str, int] = {}
    sanity_delta = deltas.get(STAT_SANITY, 0)
    if sanity_delta <= STRESS_COUPLING_THRESHOLD:
        extra[STAT_IMMUNE] = extra.get(STAT_IMMUNE, 0) + STRESS_COUPLING_IMMUNE_DELTA
    immune_delta = deltas.get(STAT_IMMUNE, 0)
    if immune_delta >= IMMUNE_DAMAGE_THRESHOLD:
        extra[STAT_HEALTH] = extra.get(STAT_HEALTH, 0) + IMMUNE_DAMAGE_HEALTH_DELTA
    if not extra:
        return deltas
    combined = dict(deltas)
    for key, value in extra.items():
        combined[key] = combined.get(key, 0) + value
    return combined


def _apply_fatigue(state: GameState) -> int:
    drain = BASE_FATIGUE_DRAIN + int((state.week - 1) * FATIGUE_GROWTH_PER_WEEK)
    return max(0, drain)


def _apply_remission_buff(state: GameState) -> None:
    if state.remission_buff_turns > 0:
        state.stats[STAT_HEALTH] += REMISSION_BUFF_HEALTH_BONUS
        state.remission_buff_turns -= 1


def _queue_scheduled_cards(state: GameState) -> None:
    scheduled = state.scheduled_card_ids.pop(state.week, [])
    state.queued_card_ids = scheduled + state.queued_card_ids





def _check_scar(state: GameState) -> None:
    if state.stats.get(STAT_HEALTH, 0) < SCAR_THRESHOLD:
        state.max_caps[STAT_HEALTH] = max(50, state.max_caps[STAT_HEALTH] - SCAR_CAP_REDUCTION)


def _update_immune_streak(state: GameState) -> None:
    if is_immune_ideal(state.stats.get(STAT_IMMUNE, 0)):
        state.immune_ideal_streak += 1
    else:
        state.immune_ideal_streak = 0

    if state.immune_ideal_streak >= REMISSION_STREAK_TARGET:
        state.tags.add(REMISSION_BUFF_TAG)
        state.remission_buff_turns = REMISSION_BUFF_DURATION


def _apply_steroid_dependence(state: GameState) -> None:
    if "STEROID_DEPENDENT" in state.tags and not state.used_steroid_last_turn:
        state.stats[STAT_IMMUNE] += STEROID_DEPENDENCE_IMMUNE_RISE


def _record_history(state: GameState, card: Card, option: str, deltas: Dict[str, int]) -> None:
    edu_id = card.education.title if card.education else None
    state.history.append(
        TurnRecord(
            week=state.week,
            card_id=card.id,
            option=option,
            deltas=dict(deltas),
            education_id=edu_id,
        )
    )


def _maybe_fail_biologic(state: GameState, option: CardOption, rng: RngFunc) -> bool:
    if not option.biologic_id:
        return False
    uses = state.biologic_uses.get(option.biologic_id, 0)
    if uses < BIOLOGIC_RESISTANCE_THRESHOLD:
        return False
    return rng() < BIOLOGIC_FAILURE_PROB


def _apply_biologic_use(state: GameState, option: CardOption) -> None:
    if option.biologic_id:
        state.biologic_uses[option.biologic_id] = state.biologic_uses.get(option.biologic_id, 0) + 1


# --- New Medical Simulation Helpers ---

def _apply_flare_cycle(state: GameState, rng: RngFunc) -> None:
    """Manage active flare state based on immune levels."""
    immune = state.stats.get(STAT_IMMUNE, 50)
    if immune >= FLARE_IMMUNE_THRESHOLD and state.flare_cooldown <= 0:
        if FLARE_TAG not in state.tags:
            state.tags.add(FLARE_TAG)
            state.flare_cooldown = FLARE_COOLDOWN_TURNS
            state.queued_card_ids.insert(0, "flare_episode")
    elif immune < FLARE_IMMUNE_THRESHOLD - 10 and FLARE_TAG in state.tags:
        state.tags.discard(FLARE_TAG)

    if FLARE_TAG in state.tags:
        state.stats[STAT_HEALTH] = state.stats.get(STAT_HEALTH, 0) - FLARE_HEALTH_DRAIN
        state.stats[STAT_SANITY] = state.stats.get(STAT_SANITY, 0) - FLARE_SANITY_DRAIN


def _apply_gut_brain_axis(state: GameState, deltas: Dict[str, int]) -> None:
    """When gut health is critically low, sanity losses are amplified."""
    health = state.stats.get(STAT_HEALTH, 50)
    if health < GUT_BRAIN_HEALTH_THRESHOLD:
        sanity_delta = deltas.get(STAT_SANITY, 0)
        if sanity_delta < 0:
            extra = int(abs(sanity_delta) * (GUT_BRAIN_SANITY_MULT - 1))
            state.stats[STAT_SANITY] = state.stats.get(STAT_SANITY, 0) - extra


def _track_steroid_cumulative(state: GameState, option: CardOption) -> None:
    """Track cumulative steroid use and apply side effects at thresholds."""
    if option.steroid_use:
        state.steroid_use_count += 1
        if state.steroid_use_count >= STEROID_CUMULATIVE_THRESHOLD:
            state.tags.add(STEROID_MOON_FACE_TAG)
        if state.steroid_use_count >= STEROID_BONE_LOSS_THRESHOLD:
            state.max_caps[STAT_HEALTH] = max(
                50, state.max_caps.get(STAT_HEALTH, 100) - STEROID_BONE_LOSS_REDUCTION
            )


def _apply_sleep_deprivation(state: GameState) -> None:
    """Apply ongoing sleep deprivation effects."""
    if SLEEP_DEPRIVED_TAG in state.tags:
        state.stats[STAT_IMMUNE] = state.stats.get(STAT_IMMUNE, 0) + SLEEP_DEPRIVED_IMMUNE_PENALTY
        state.stats[STAT_SANITY] = state.stats.get(STAT_SANITY, 0) - SLEEP_DEPRIVED_SANITY_DRAIN


def _apply_season_change_jitter(state: GameState, rng: RngFunc) -> None:
    """At season transitions, add random immune perturbation."""
    if state.week in SEASON_CHANGE_WEEKS:
        jitter = int((rng() - 0.5) * 2 * SEASON_CHANGE_IMMUNE_JITTER)
        state.stats[STAT_IMMUNE] = state.stats.get(STAT_IMMUNE, 0) + jitter


def _apply_malnutrition(state: GameState) -> None:
    """When both HEALTH and MONEY are critically low, apply malnutrition debuff."""
    health = state.stats.get(STAT_HEALTH, 50)
    money = state.stats.get(STAT_MONEY, 50)
    if health < MALNUTRITION_HEALTH_THRESHOLD and money < MALNUTRITION_MONEY_THRESHOLD:
        if MALNUTRITION_TAG not in state.tags:
            state.tags.add(MALNUTRITION_TAG)
        state.stats[STAT_IMMUNE] = state.stats.get(STAT_IMMUNE, 0) + MALNUTRITION_IMMUNE_PENALTY
        state.stats[STAT_HEALTH] = state.stats.get(STAT_HEALTH, 0) - MALNUTRITION_HEALTH_DRAIN
    elif MALNUTRITION_TAG in state.tags:
        state.tags.discard(MALNUTRITION_TAG)


def _track_medication_adherence(state: GameState, card: Card, option: CardOption) -> None:
    """Track medication adherence when treatment cards offer medication."""
    if card.theme == "treatment" and option.effect:
        immune_delta = option.effect.get(STAT_IMMUNE, 0)
        if immune_delta != 0:
            state.medication_doses_offered += 1
            if immune_delta < 0:
                state.medication_doses_taken += 1


def _update_round4_stats(state: GameState, option: CardOption) -> None:
    """Update diet and ostomy/surgery related stats."""
    if option.diet_delta:
        state.diet_score = max(-10, min(10, state.diet_score + option.diet_delta))
    if option.ostomy_skill_delta:
        state.ostomy_care_skill = max(0, min(10, state.ostomy_care_skill + option.ostomy_skill_delta))


def _apply_diet_mechanics(state: GameState) -> Dict[str, int]:
    """Apply ongoing diet effects on health/immune."""
    bonus = {}
    if state.diet_score >= DIET_HIGH_THRESHOLD:
        bonus[STAT_HEALTH] = DIET_HEALING_BONUS
    elif state.diet_score <= DIET_LOW_THRESHOLD:
        bonus[STAT_IMMUNE] = bonus.get(STAT_IMMUNE, 0) + DIET_IMMUNE_PENALTY
    return bonus


def _apply_ostomy_mechanics(state: GameState, rng: RngFunc) -> None:
    """Apply ostomy leak risk and skill checks."""
    if OSTOMY_TAG not in state.tags:
        return

    # Check for leaks
    risk = OSTOMY_LEAK_PROB_BASE - (state.ostomy_care_skill * 0.05)
    if rng() < max(0.1, risk):
        state.tags.add("OSTOMY_LEAK")
        state.stats[STAT_SANITY] = state.stats.get(STAT_SANITY, 0) - OSTOMY_LEAK_SANITY_DRAIN
        state.queued_card_ids.insert(0, "ostomy_leak_event")


def _apply_adherence_flare_risk(state: GameState, rng: RngFunc) -> None:
    """Poor medication adherence increases flare risk."""
    if state.medication_doses_offered < 3:
        return
    adherence = state.medication_doses_taken / state.medication_doses_offered
    if adherence < ADHERENCE_POOR_THRESHOLD:
        if state.flare_cooldown <= 0 and rng() < ADHERENCE_POOR_FLARE_PROB:
            state.tags.add(FLARE_TAG)
            state.flare_cooldown = FLARE_COOLDOWN_TURNS
            state.queued_card_ids.insert(0, "flare_episode")



def _apply_induction_schedule(state: GameState, option: CardOption) -> None:
    if option.induction_start:
        state.scheduled_card_ids.setdefault(state.week + 2, []).append("biologic_injection")
        state.scheduled_card_ids.setdefault(state.week + 6, []).append("biologic_injection")


def _track_social_isolation(state: GameState, card: Card, option: CardOption) -> None:
    """Track consecutive social avoidance and apply ISOLATED tag."""
    if (card.theme or "misc") == "social":
        label_lower = option.label.lower()
        is_avoidance = any(k in label_lower for k in ["home", "skip", "refuse", "cancel", "no", "avoid"])
        if is_avoidance:
            state.social_isolation_counter += 1
        else:
            state.social_isolation_counter = max(0, state.social_isolation_counter - 1)

    if state.social_isolation_counter >= 3:
        if "ISOLATED" not in state.tags:
            state.tags.add("ISOLATED")
            state.max_caps[STAT_SANITY] = max(50, state.max_caps.get(STAT_SANITY, 100) - 10)
            state.queued_card_ids.insert(0, "social_breakdown")
    elif "ISOLATED" in state.tags:
        state.tags.discard("ISOLATED")
        state.max_caps[STAT_SANITY] = min(100, state.max_caps.get(STAT_SANITY, 100) + 10)


def _record_milestone_log(state: GameState, card: Card, option: CardOption) -> None:
    """Log significant events for the medical profile."""
    is_significant = (
        (card.rarity in ("rare", "legendary") and card.theme != "education") or
        "surgery" in card.id or
        "biologic" in card.id or
        "diagnosis" in card.id or
        bool(option.add_tags)
    )
    if is_significant:
        entry = f"W{state.week}: {option.label} ({card.id})"
        state.milestones.insert(0, entry)


def apply_choice(
    state: GameState,
    deck: CardDeck,
    card: Card,
    option: CardOption,
    rng: RngFunc,
    infection_prob: float = INFECTION_PROB_DEFAULT,
) -> None:
    _update_round4_stats(state, option)
    deltas = dict(option.effect)

    # Apply diet mechanics (ongoing buff/debuff)
    diet_bonus = _apply_diet_mechanics(state)
    for k, v in diet_bonus.items():
        deltas[k] = deltas.get(k, 0) + v

    deltas = _apply_winter_volatility(state, deltas)
    deltas = _apply_mild_treatment_inertia(state, option, deltas)
    deltas = _apply_healing_lag(state, deltas)
    deltas = _apply_tag_modifiers(state, deltas)

    if option.stop_steroid and state.used_steroid_last_turn:
        if STAT_IMMUNE in deltas and deltas[STAT_IMMUNE] < 0:
            deltas[STAT_IMMUNE] = abs(deltas[STAT_IMMUNE]) + 20

    if _maybe_fail_biologic(state, option, rng):
        deltas = {key: 0 for key in deltas}

    for stat, delta in deltas.items():
        state.stats[stat] = state.stats.get(stat, 0) + delta

    state.toxic += option.toxic_delta
    if option.symptom_suppression:
        state.suppression_turns += 1

    _apply_biologic_use(state, option)
    _apply_induction_schedule(state, option)
    if option.injection_required and option.missed_injection:
        state.resistance += 50

    state.tags.update(option.add_tags)
    for tag in option.remove_tags:
        state.tags.discard(tag)

    if card.id == "checkup":
        if evaluate_checkup(state) == "escalate":
            state.tags.add("TREATMENT_ESCALATED")

    combined = _apply_coupling(state, deltas)
    extra = {}
    for stat, delta in combined.items():
        extra_delta = delta - deltas.get(stat, 0)
        if extra_delta:
            extra[stat] = extra_delta
    for stat, delta in extra.items():
        state.stats[stat] = state.stats.get(stat, 0) + delta

    if option.risk_tags and state.tags.intersection(option.risk_tags) and option.risk_event_id:
        state.queued_card_ids.insert(0, option.risk_event_id)

    if card.chain_next:
        state.queued_card_ids = list(card.chain_next) + state.queued_card_ids

    _record_history(state, card, "left" if option is card.left else "right", combined)
    if card.theme:
        state.recent_themes.append(card.theme)
        state.recent_themes = state.recent_themes[-5:]

    state.used_steroid_last_turn = option.steroid_use

    _apply_steroid_dependence(state)
    _track_steroid_cumulative(state, option)

    state.stats[STAT_SANITY] -= _apply_fatigue(state)

    _apply_gut_brain_axis(state, deltas)
    _apply_flare_cycle(state, rng)
    _apply_sleep_deprivation(state)
    _apply_malnutrition(state)
    _apply_season_change_jitter(state, rng)

    _track_medication_adherence(state, card, option)
    _apply_adherence_flare_risk(state, rng)
    _track_social_isolation(state, card, option)
    _record_milestone_log(state, card, option)
    _apply_ostomy_mechanics(state, rng)

    _apply_remission_buff(state)

    _update_immune_streak(state)

    _check_scar(state)

    state.clamp_stats()
    state.health_history.append(state.stats.get(STAT_HEALTH, 0))
    state.immune_history.append(state.stats.get(STAT_IMMUNE, 0))

    if state.toxic >= TOXICITY_THRESHOLD:
        state.toxic = TOXICITY_RESET
        state.queued_card_ids.insert(0, "megacolon")



    if state.stats.get(STAT_IMMUNE, 0) < 20 and rng() < infection_prob:
        state.queued_card_ids.insert(0, "infection")

    # Decrement cooldowns
    if state.flare_cooldown > 0:
        state.flare_cooldown -= 1
    if state.sleep_deprived_turns > 0:
        state.sleep_deprived_turns -= 1
        if state.sleep_deprived_turns <= 0:
            state.tags.discard(SLEEP_DEPRIVED_TAG)

    state.week += 1
    state.last_card_id = card.id


def check_death(state: GameState) -> Optional[str]:
    immune = state.stats.get(STAT_IMMUNE, 0)
    health = state.stats.get(STAT_HEALTH, 0)
    sanity = state.stats.get(STAT_SANITY, 0)
    money = state.stats.get(STAT_MONEY, 0)
    if immune <= 0:
        return DEATH_ENDINGS["immune_low"]
    if immune >= 100:
        return DEATH_ENDINGS["immune_high"]
    if health <= 0:
        return DEATH_ENDINGS["health_low"]
    if health >= 100:
        return DEATH_ENDINGS.get("health_high", "false_confidence")
    if sanity <= 0:
        return DEATH_ENDINGS["sanity_low"]
    if sanity >= 100:
        return DEATH_ENDINGS["sanity_high"]
    if money <= 0:
        return DEATH_ENDINGS["money_low"]
    if money >= 100:
        return DEATH_ENDINGS["money_high"]
    return None


def evaluate_checkup(state: GameState) -> str:
    """Evaluate checkup with tri-state output: good / concern / escalate."""
    recent_immune = state.immune_history[-13:]
    recent_health = state.health_history[-13:]
    if not recent_immune:
        return "stable"
    avg_immune = sum(recent_immune) / len(recent_immune)
    avg_health = sum(recent_health) / len(recent_health) if recent_health else 50
    if avg_immune > 60:
        return "escalate"
    if avg_health < 40 or avg_immune > 45:
        return "concern"
    return "stable"


def build_autopsy_report(state: GameState) -> Dict:
    """Build structured post-mortem analysis for game-over screens."""
    fatal_stat = state.death_reason or "unknown"

    # Find the 3 worst contributing cards
    worst_cards = []
    if state.history:
        stat_key = {
            "sepsis": STAT_IMMUNE, "perforation": STAT_HEALTH,
            "megacolon": STAT_HEALTH, "bad_dropout": STAT_SANITY,
            "bad_bankruptcy": STAT_MONEY, "financial_toxicity": STAT_MONEY,
        }.get(fatal_stat, STAT_HEALTH)
        negative = [r for r in state.history if r.deltas.get(stat_key, 0) < 0]
        worst_cards = [
            {"card_id": r.card_id, "week": r.week, "delta": r.deltas.get(stat_key, 0)}
            for r in negative[-3:]
        ]

    # Medication adherence score
    adherence_pct = 0
    if state.medication_doses_offered > 0:
        adherence_pct = int(100 * state.medication_doses_taken / state.medication_doses_offered)

    # Active comorbidities
    from .constants import EIM_TAGS
    active_eims = sorted(state.tags & EIM_TAGS)

    # Counterfactual: "what if you chose the other option?"
    counterfactuals = []
    for wc in worst_cards:
        rec = next((r for r in state.history if r.card_id == wc["card_id"] and r.week == wc["week"]), None)
        if rec:
            counterfactuals.append({
                "card_id": wc["card_id"],
                "week": wc["week"],
                "chose": rec.option,
                "actual_delta": wc["delta"],
            })

    # Education topics learned
    edu_learned = sorted(state.learned_topics)

    return {
        "fatal_stat": fatal_stat,
        "weeks_survived": state.week,
        "worst_cards": worst_cards,
        "counterfactuals": counterfactuals,
        "adherence_pct": adherence_pct,
        "steroid_uses": state.steroid_use_count,
        "active_eims": active_eims,
        "final_stats": dict(state.stats),
        "education_learned": edu_learned,
    }


def check_final_endoscopy(state: GameState) -> str:
    health_scores = state.health_history
    if not health_scores:
        avg_health = state.stats.get(STAT_HEALTH, 0)
    else:
        avg_health = sum(health_scores) / len(health_scores)
    if avg_health > 80:
        return "deep_remission"
    if avg_health >= 50:
        return "clinical_remission"
    return "treatment_failure"


def is_fake_win(state: GameState) -> bool:
    if state.week <= FINAL_WEEK:
        return False
    total_turns = max(1, len(state.history))
    return state.suppression_turns / total_turns >= 0.5


def build_autopsy(state: GameState, stat_key: str) -> List[TurnRecord]:
    negative = [record for record in state.history if record.deltas.get(stat_key, 0) < 0]
    return negative[-3:]


def start_turn(state: GameState) -> None:
    _queue_scheduled_cards(state)
    if state.week in CHECKUP_WEEKS:
        state.queued_card_ids.insert(0, "checkup")


def next_card(state: GameState, deck: CardDeck, rng: RngFunc, pool: Optional[str]) -> Card:
    if state.queued_card_ids:
        card_id = state.queued_card_ids.pop(0)
        return deck.get_card(card_id)
    if "POST_SURGERY" in state.tags:
        pool = "post_surgery"
    return deck.draw(state, rng, pool=pool)


def resolve_turn(
    state: GameState,
    deck: CardDeck,
    card: Card,
    option: CardOption,
    rng: RngFunc,
) -> None:
    apply_choice(state, deck, card, option, rng)
    death = check_death(state)
    if death == "perforation":
        state.queued_card_ids.insert(0, "surgery")
    elif death:
        state.game_over = True
        state.death_reason = death


def handle_surgery_choice(state: GameState, accept: bool) -> None:
    if accept:
        state.tags.add("POST_SURGERY")
    else:
        state.game_over = True
        state.death_reason = "perforation"


def apply_ending(state: GameState, endings: Dict[str, Ending], ending_id: str) -> None:
    state.ending = endings[ending_id]
    state.allow_new_game_plus = state.ending.tier == "top"
    if state.allow_new_game_plus:
        state.available_perks = ["RICH_START", "MED_STUDENT"]


def run_end_of_year(state: GameState, endings: Dict[str, Ending]) -> Ending:
    tier = check_final_endoscopy(state)
    ending_id = tier
    if is_fake_win(state):
        ending_id = "bad_end"
    ending = endings[ending_id]
    state.ending = ending
    state.allow_new_game_plus = ending.tier == "top"
    if state.allow_new_game_plus:
        state.available_perks = ["RICH_START", "MED_STUDENT"]
    return ending


# --- Contextual Education Engine ---

_CONTEXTUAL_EDUCATION = {
    "adherence_poor": {
        "title": "用藥順從性的重要性",
        "content": "研究顯示，IBD 患者的用藥順從性低於 80% 時，復發風險會增加 2-3 倍。即使症狀好轉，也應繼續按醫囑服藥。",
        "source": "European Crohn's and Colitis Organisation (ECCO) Guidelines 2023",
    },
    "flare_active": {
        "title": "急性發作的處理原則",
        "content": "發炎期間應避免刺激性食物、保持充足休息，並遵循醫師的治療計畫。自行停藥或使用偏方可能導致病情惡化。",
        "source": "台灣消化系醫學會 IBD 治療指引",
    },
    "steroid_overuse": {
        "title": "類固醇的雙面刃效應",
        "content": "短期使用類固醇可快速控制發炎，但長期使用會導致骨質疏鬆、月亮臉、感染風險增加等副作用。醫師通常會建議逐步轉換為免疫調節劑。",
        "source": "American Gastroenterological Association (AGA)",
    },
    "malnutrition": {
        "title": "IBD 與營養不良",
        "content": "IBD 患者因腸道吸收不良、食慾下降等原因，容易出現營養不良。建議攝取高蛋白質飲食，並諮詢營養師制定個人化飲食計畫。",
        "source": "ESPEN Guideline on Clinical Nutrition in IBD",
    },
    "social_isolation": {
        "title": "心理健康與社交的關聯",
        "content": "IBD 患者的焦慮和憂鬱盛行率約為健康人群的 2 倍。維持社交活動、加入病友團體、尋求心理諮商都是有效的應對策略。",
        "source": "Journal of Crohn's and Colitis, 2022",
    },
    "sleep_quality": {
        "title": "睡眠品質與腸道健康",
        "content": "睡眠不足會擾亂腸道微生物組態、增加發炎指標。建議維持規律作息、每晚 7-8 小時睡眠，並避免睡前進食。",
        "source": "Gastroenterology, 2021",
    },
    "diet_poor": {
        "title": "飲食與 IBD 管理",
        "content": "低殘渣飲食可在發炎期減少腸道負擔。緩解期可逐漸增加纖維攝取。記錄飲食日誌有助於識別個人的觸發食物。",
        "source": "Crohn's & Colitis Foundation Diet Guide",
    },
}


def generate_contextual_education(
    state: GameState,
    card: Card,
    option: CardOption,
) -> Optional[Dict[str, str]]:
    """Generate contextual education based on the player's state and choice.

    Returns a dict with title/content/source, or None if no education is warranted.
    Deduplicates against state.learned_topics.
    """
    candidates: List[str] = []

    # Bad medication adherence
    if state.medication_doses_offered >= 3:
        adherence = state.medication_doses_taken / state.medication_doses_offered
        if adherence < ADHERENCE_POOR_THRESHOLD:
            candidates.append("adherence_poor")

    # Active flare
    if FLARE_TAG in state.tags:
        candidates.append("flare_active")

    # Steroid overuse
    if state.steroid_use_count >= STEROID_CUMULATIVE_THRESHOLD:
        candidates.append("steroid_overuse")

    # Malnutrition
    if MALNUTRITION_TAG in state.tags:
        candidates.append("malnutrition")

    # Social isolation
    if "ISOLATED" in state.tags:
        candidates.append("social_isolation")

    # Sleep deprivation
    if SLEEP_DEPRIVED_TAG in state.tags:
        candidates.append("sleep_quality")

    # Poor diet
    if state.diet_score <= -3:
        candidates.append("diet_poor")

    # Filter out already-learned topics
    candidates = [c for c in candidates if c not in state.learned_topics]

    # Track bad choice streak
    net_health = option.effect.get(STAT_HEALTH, 0) + option.effect.get(STAT_IMMUNE, 0)
    if net_health < -10:
        state.bad_choice_streak += 1
    elif net_health > 0:
        state.bad_choice_streak = max(0, state.bad_choice_streak - 1)

    if not candidates:
        return None

    # Prioritize: pick the first relevant, or if bad_choice_streak >= 2, always show
    if state.bad_choice_streak < 2 and len(candidates) > 1:
        # Only show education every other card to avoid fatigue
        if state.week % 2 != 0:
            return None

    topic = candidates[0]
    state.learned_topics.add(topic)
    edu = dict(_CONTEXTUAL_EDUCATION[topic])
    # Assign severity tier based on topic
    _severity_map = {
        "adherence_poor": "warning",
        "flare_active": "critical",
        "steroid_overuse": "warning",
        "malnutrition": "warning",
        "social_isolation": "info",
        "sleep_quality": "info",
        "diet_poor": "info",
    }
    edu["severity"] = _severity_map.get(topic, "info")
    return edu


# --- Milestone Education (first-time events) ---

_MILESTONE_EDUCATION = {
    "first_flare": {
        "title": "🔥 初次疾病發作",
        "content": "IBD 的第一次急性發作往往是最令人恐慌的。研究顯示約 50% 的 IBD 患者在確診後一年內經歷首次嚴重發作。早期積極治療可顯著降低併發症風險。",
        "source": "Lancet Gastroenterology & Hepatology, 2023",
        "severity": "critical",
    },
    "first_steroid": {
        "title": "💊 首次使用類固醇",
        "content": "類固醇 (如 Prednisolone) 可在 3-7 天內快速控制發炎。但這不是長期解決方案——約 30% 的患者會產生類固醇依賴。務必與醫師討論後續的維持療法計畫。",
        "source": "AGA Clinical Practice Guidelines, 2022",
        "severity": "warning",
    },
    "first_biologic": {
        "title": "🧬 首次生物製劑治療",
        "content": "生物製劑 (如 Infliximab, Adalimumab) 是精準醫療的代表。它們靶向特定發炎路徑，可有效誘導並維持緩解。注射時間表的遵守對療效至關重要。",
        "source": "ECCO Topical Review on Biologics, 2023",
        "severity": "info",
    },
    "first_surgery": {
        "title": "🏥 手術決策",
        "content": "約 23-45% 的潰瘍性結腸炎和 70-80% 的克隆氏症患者在一生中需要至少一次手術。手術不代表失敗，而是治療策略的重要工具。術後護理和營養管理同樣關鍵。",
        "source": "British Society of Gastroenterology Guidelines",
        "severity": "critical",
    },
}


def check_milestone_education(
    state: GameState, card: Card, option: CardOption,
) -> Optional[Dict[str, str]]:
    """Check for first-time milestone events and return education if applicable."""
    milestone_key = None

    if FLARE_TAG in option.add_tags and "first_flare" not in state.learned_topics:
        milestone_key = "first_flare"
    elif option.steroid_use and "first_steroid" not in state.learned_topics:
        milestone_key = "first_steroid"
    elif option.biologic_id and "first_biologic" not in state.learned_topics:
        milestone_key = "first_biologic"
    elif "surgery" in card.id and "first_surgery" not in state.learned_topics:
        milestone_key = "first_surgery"

    if milestone_key:
        state.learned_topics.add(milestone_key)
        return dict(_MILESTONE_EDUCATION[milestone_key])
    return None


# --- Micro-Tip System ---

_MICRO_TIPS = {
    FLARE_TAG: "💡 發炎期間避免高纖維及乳製品",
    SLEEP_DEPRIVED_TAG: "💡 規律作息可降低 23% 復發風險",
    MALNUTRITION_TAG: "💡 考慮口服營養補充品 (ONS)",
    "ISOLATED": "💡 病友團體支持可改善 40% 心理健康",
    STEROID_MOON_FACE_TAG: "💡 類固醇副作用停藥後通常可逆",
    REMISSION_BUFF_TAG: "💡 緩解期是鞏固治療的最佳時機",
    "OSTOMY_BAG": "💡 造口護理技巧越熟練，漏液風險越低",
}


def generate_micro_tip(state: GameState) -> Optional[str]:
    """Return a brief contextual micro-tip based on current tags, or None."""
    for tag, tip in _MICRO_TIPS.items():
        if tag in state.tags:
            return tip
    # Stat-based tips
    if state.stats.get(STAT_MONEY, 50) < 25:
        return "💡 經濟困難可申請重大傷病卡減免"
    if state.stats.get(STAT_HEALTH, 50) > 80 and state.stats.get(STAT_IMMUNE, 50) < 30:
        return "💡 症狀好轉不等於腸道已痊癒—持續追蹤發炎指標"
    return None


# Education severity constants for UI rendering
EDUCATION_SEVERITY_COLORS = {
    "info": ("#64B5F6", "rgba(100,181,246,0.06)", "ℹ️"),
    "warning": ("#FFB74D", "rgba(255,183,77,0.06)", "⚠️"),
    "critical": ("#E57373", "rgba(229,115,115,0.06)", "🚨"),
}


