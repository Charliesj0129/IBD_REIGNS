Feature: Core Stats and Coupling
  Four pillars create tradeoffs and coupled dynamics.

  Scenario: Clamp stats to valid range
    Given a stat value is below 0
    When effects are applied
    Then the stat value is set to 0

  Scenario: Immune too low causes infection
    Given IMMUNE is 0 or less
    When death checks run
    Then the game ends with the infection ending

  Scenario: Immune too high causes flare storm
    Given IMMUNE is 100 or more
    When death checks run
    Then the game ends with the flare storm ending

  Scenario: Health too low causes perforation
    Given HEALTH is 0 or less
    When death checks run
    Then the game ends with the perforation ending

  Scenario: Sanity too low causes give-up ending
    Given SANITY is 0 or less
    When death checks run
    Then the game ends with the give-up ending

  Scenario: Sanity too high causes burnout
    Given SANITY is 100 or more
    When death checks run
    Then the game ends with the burnout ending

  Scenario: Money too low causes financial toxicity
    Given MONEY is 0 or less
    When death checks run
    Then the game ends with the financial toxicity ending

  Scenario: Money too high causes workaholic collapse
    Given MONEY is 100 or more
    When death checks run
    Then the game ends with the workaholic ending

  Scenario: Health overconfidence trap
    Given HEALTH is 100 or more
    When the next turn starts
    Then a forced overconfidence event is queued
    And HEALTH is reduced to a safe level
    And IMMUNE is increased by a large amount

  Scenario: Coupling between SANITY and IMMUNE
    Given SANITY decreased sharply in a turn
    When coupling rules are applied
    Then IMMUNE increases by a stress factor

  Scenario: Coupling between IMMUNE and HEALTH
    Given IMMUNE increases sharply in a turn
    When coupling rules are applied
    Then HEALTH decreases by a damage factor

  Scenario: Healing lag
    Given IMMUNE is in the ideal range for 2 consecutive turns
    When a turn ends
    Then HEALTH can only recover by a small capped amount

  Scenario: Scar accumulation
    Given HEALTH drops below 20 in a turn
    When the turn resolves
    Then the maximum HEALTH cap is reduced permanently
