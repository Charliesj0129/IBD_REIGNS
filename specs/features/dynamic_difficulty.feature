Feature: Dynamic Difficulty and Streaks
  Difficulty shifts over time and by player stability.

  Scenario: Remission streak bonus
    Given IMMUNE stays between 40 and 60 for 4 turns
    When the streak completes
    Then the player gains a MUCOSAL_REPAIR buff
    And HEALTH increases by a bonus each turn while the buff lasts

  Scenario: Fatigue stacking over time
    Given the week counter increases
    When a turn ends
    Then a baseline SANITY drain is applied
    And the drain increases as the year progresses

  Scenario: Immune inertia during flares
    Given IMMUNE is above 75
    When a mild treatment card is chosen
    Then the IMMUNE reduction is halved
