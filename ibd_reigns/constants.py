STAT_HEALTH = "HEALTH"
STAT_IMMUNE = "IMMUNE"
STAT_SANITY = "SANITY"
STAT_MONEY = "MONEY"

STATS = (STAT_HEALTH, STAT_IMMUNE, STAT_SANITY, STAT_MONEY)

IMMUNE_IDEAL_MIN = 40
IMMUNE_IDEAL_MAX = 60

WINTER_START = 40
WINTER_END = 52

CHECKUP_WEEKS = (13, 26, 39)
FINAL_WEEK = 52

DEFAULT_STATS = {
    STAT_HEALTH: 50,
    STAT_IMMUNE: 50,
    STAT_SANITY: 50,
    STAT_MONEY: 50,
}

RECENT_CARD_EXCLUDE = 3
THEME_COOLDOWN = 2
RARITY_WEIGHTS = {
    "common": 1.0,
    "uncommon": 0.7,
    "rare": 0.4,
    "legendary": 0.2,
}

# CHAPTER_THEME_WEIGHTS moved to assets/game_rules.json

DEATH_ENDINGS = {
    "immune_low": "infection",
    "immune_high": "flare_storm",
    "health_low": "perforation",
    "sanity_low": "give_up",
    "sanity_high": "burnout",
    "money_low": "financial_toxicity",
    "money_high": "workaholic",
    "health_high": "false_confidence",
}

OVERCONFIDENCE_HEALTH_RESET = 80
OVERCONFIDENCE_IMMUNE_SPIKE = 50

STRESS_COUPLING_THRESHOLD = -15
STRESS_COUPLING_IMMUNE_DELTA = 10

IMMUNE_DAMAGE_THRESHOLD = 15
IMMUNE_DAMAGE_HEALTH_DELTA = -10

HEALING_LAG_CAP = 2
SCAR_THRESHOLD = 20
SCAR_CAP_REDUCTION = 5

STEROID_DEPENDENCE_IMMUNE_RISE = 10

TOXICITY_THRESHOLD = 100
TOXICITY_RESET = 20

REMISSION_STREAK_TARGET = 4
REMISSION_BUFF_TAG = "MUCOSAL_REPAIR"
REMISSION_BUFF_HEALTH_BONUS = 5
REMISSION_BUFF_DURATION = 3

BASE_FATIGUE_DRAIN = 1
FATIGUE_GROWTH_PER_WEEK = 0.05

WINTER_IMMUNE_VOLATILITY_MULT = 1.2

BIOLOGIC_RESISTANCE_THRESHOLD = 10
BIOLOGIC_FAILURE_PROB = 0.1

INFECTION_PROB_DEFAULT = 0.2

# --- Flare Cycle Mechanics ---
FLARE_IMMUNE_THRESHOLD = 70       # Immune >= this triggers flare state
FLARE_HEALTH_DRAIN = 3            # Extra HEALTH drain per turn during flare
FLARE_SANITY_DRAIN = 2            # Extra SANITY drain per turn during flare
FLARE_COOLDOWN_TURNS = 4          # Minimum turns between flare episodes
FLARE_TAG = "ACTIVE_FLARE"

# --- Diet Impact ---
DIET_RISKY_HEALTH_PENALTY = 5     # HEALTH penalty for risky food during flare
DIET_SAFE_HEALTH_BONUS = 2        # HEALTH bonus for safe diet choices

# --- Sleep Deprivation ---
SLEEP_DEPRIVED_IMMUNE_PENALTY = 3   # Extra immune instability when sleep deprived
SLEEP_DEPRIVED_SANITY_DRAIN = 2
SLEEP_DEPRIVED_TAG = "SLEEP_DEPRIVED"
SLEEP_DEPRIVED_DURATION = 3         # Turns the debuff lasts

# --- Medication Adherence ---
ADHERENCE_GOOD_THRESHOLD = 0.8      # >= 80% adherence = good outcome
ADHERENCE_POOR_THRESHOLD = 0.5      # < 50% = poor, triggers complications
ADHERENCE_POOR_FLARE_PROB = 0.3     # Probability of flare if adherence is poor

# --- Seasonal Flare Triggers ---
SEASON_CHANGE_WEEKS = (13, 26, 39)  # Season transitions
SEASON_CHANGE_IMMUNE_JITTER = 5     # Random immune perturbation at season change

# --- Steroid Side Effects ---
STEROID_CUMULATIVE_THRESHOLD = 3    # After N steroid uses, gain MOON_FACE tag
STEROID_MOON_FACE_TAG = "MOON_FACE"
STEROID_BONE_LOSS_THRESHOLD = 6     # After N uses, HEALTH cap reduction
STEROID_BONE_LOSS_REDUCTION = 3

# --- Gut-Brain Axis ---
GUT_BRAIN_HEALTH_THRESHOLD = 30     # HEALTH < this amplifies SANITY loss
GUT_BRAIN_SANITY_MULT = 1.5         # Multiplier on SANITY deltas when gut is bad

# --- Comorbidity Cascade ---
EIM_TAGS = {"JOINT_PAIN", "SKIN_EIM", "EYE_EIM", "ANEMIA"}  # EIM tracking tags
EIM_COMPLICATION_WEIGHT_BONUS = 0.3   # +30% complication weight per active EIM

# --- Malnutrition ---
MALNUTRITION_HEALTH_THRESHOLD = 25
MALNUTRITION_MONEY_THRESHOLD = 20
MALNUTRITION_TAG = "MALNOURISHED"
MALNUTRITION_IMMUNE_PENALTY = 3
MALNUTRITION_HEALTH_DRAIN = 2

# --- Dynamic Checkup ---
CHECKUP_RESULT_GOOD = "checkup_good"
CHECKUP_RESULT_CONCERN = "checkup_concern"
CHECKUP_RESULT_ESCALATE = "checkup_escalate"

# --- Round 4: Diet & Surgery ---
DIET_HIGH_THRESHOLD = 5         # High diet score accelerates healing
DIET_LOW_THRESHOLD = -5         # Low diet score triggers inflammation
DIET_HEALING_BONUS = 2          # Weekly health bonus for good diet
DIET_IMMUNE_PENALTY = 3         # Weekly immune penalty (instability) for bad diet
OSTOMY_TAG = "OSTOMY_BAG"       # Player has an ostomy
OSTOMY_CARE_THRESHOLD = 3       # Skill needed to avoid leaks
OSTOMY_LEAK_SANITY_DRAIN = 5    # Sanity hit on leak
OSTOMY_LEAK_PROB_BASE = 0.4     # Base probability of leak (reduced by skill)
