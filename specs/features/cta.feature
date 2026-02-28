Feature: Dynamic Call To Action (CTA)
  Endings determine which next-step actions are shown.

  Scenario: CTA for knowledge-related bad ending
    Given the game ends with a knowledge-related bad ending
    When the end screen is rendered
    Then the CTA title reflects urgency
    And a guideline download action is shown
    And a specialist directory action is shown

  Scenario: CTA for support-related bad ending
    Given the game ends with a social or financial collapse ending
    When the end screen is rendered
    Then the CTA title reflects support
    And a community join action is shown
    And a welfare resources action is shown

  Scenario: CTA for good ending
    Given the game ends with a top tier or good ending
    When the end screen is rendered
    Then the CTA title reflects celebration
    And a donation action is shown
    And a share action is shown

  Scenario: CTA is rendered after autopsy report
    Given the end screen includes an autopsy report
    When the report is shown
    Then the CTA section is rendered below it
    And the CTA includes a footer attribution
