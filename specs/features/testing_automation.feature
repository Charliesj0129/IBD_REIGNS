Feature: Automated Testing Coverage
  The project provides full automated test coverage with E2E.

  Scenario: E2E flow test
    Given the game is runnable
    When the E2E suite runs
    Then it completes a full 52-week loop
    And it reaches an ending and CTA

  Scenario: Simulation stress test
    Given the simulation runner is available
    When it runs 1000 games with fixed seeds
    Then no crashes occur

  Scenario: Card coverage test
    Given events.json is loaded
    When tests run
    Then every card is drawn at least once

  Scenario: Translation coverage test
    Given zh_TW translations are loaded
    When tests run
    Then all UI keys are present

  Scenario: Snapshot UI test
    Given UI snapshots are configured
    When the snapshot test runs
    Then the preview panel and ending screen match baseline
