Feature: Endings and Autopsy Report
  The game ends by thresholds or by the annual evaluation.

  Scenario: Immediate death ending
    Given a stat reaches a death threshold
    When death checks run
    Then the game ends immediately
    And a death reason is stored

  Scenario: Final endoscopy scoring
    Given the week counter reaches 52
    When the final endoscopy runs
    Then an ending tier is chosen based on mucosal score history

  Scenario: Fake win detection
    Given the player reaches week 52 using symptom-suppression only
    When the final endoscopy runs
    Then the result is marked as BAD_END

  Scenario: Post-mortem analysis
    Given the game ends by death
    When the autopsy report is shown
    Then the top 3 contributing decisions are listed
    And each decision links to its educational entry

  Scenario: New Game Plus perks
    Given the player achieved a TOP_TIER ending
    When starting a new game
    Then the player may choose one perk
