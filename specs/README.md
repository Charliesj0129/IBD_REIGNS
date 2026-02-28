Gut Reigns - BDD Specifications
================================

This folder contains Gherkin-style BDD specs for the Gut Reigns concept.
All content is ASCII-only for portability. In-game text can be localized later.

Index
-----
- specs/features/game_loop.feature
- specs/features/stats_system.feature
- specs/features/card_engine.feature
- specs/features/hints_and_feedback.feature
- specs/features/mobile_ux.feature
- specs/features/disclaimer.feature
- specs/features/medical_mechanics.feature
- specs/features/cta.feature
- specs/features/analytics_tracking.feature
- specs/features/visual_language.feature
- specs/features/narrative_density.feature
- specs/features/interaction_feel.feature
- specs/features/preview_impacts.feature
- specs/features/i18n_zh_tw.feature
- specs/features/testing_automation.feature
- specs/features/dynamic_difficulty.feature
- specs/features/social_economy.feature
- specs/features/status_tags.feature
- specs/features/hidden_toxicity.feature
- specs/features/endings.feature
- specs/features/ui_streamlit.feature
- specs/features/data_schema.feature

Global Definitions
------------------
Stats (range 0..100):
- HEALTH: mucosal barrier integrity (higher is better)
- IMMUNE: immune activity (middle range is ideal)
- SANITY: mental state and autonomic balance (middle range is ideal)
- MONEY: financial and social capital (higher is safer)

Default start values:
- HEALTH=50, IMMUNE=50, SANITY=50, MONEY=50

Death rules (baseline):
- IMMUNE <= 0: opportunistic infection / sepsis
- IMMUNE >= 100: flare storm / cytokine storm
- HEALTH <= 0: perforation
- SANITY <= 0: give up / depression
- SANITY >= 100: burnout
- MONEY <= 0: financial toxicity / forced stop of treatment
- MONEY >= 100: workaholic collapse

Special rules:
- HEALTH >= 100 does not kill immediately; it triggers a forced "overconfidence" event
  that spikes IMMUNE and resets HEALTH to a safe level.

Time model:
- 1 turn = 1 week, 52 turns = 1 year
- Seasons: 1-13 spring, 14-26 summer, 27-39 fall, 40-52 winter
- Quarterly checkups on turns 13, 26, 39
- Final endoscopy on turn 52

Notation
--------
- Hints show which stats are affected, never the direction.
- Card options are LEFT and RIGHT.
- Effects are applied as deltas, then clamped to 0..100.
- Tags are status flags that persist across turns.
