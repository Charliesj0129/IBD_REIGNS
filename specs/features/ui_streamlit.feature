Feature: Streamlit UI Layout
  The UI mimics swipe decisions using two buttons.

  Scenario: Top status bars render
    Given a game is active
    When the UI renders
    Then four progress bars are shown for HEALTH, IMMUNE, SANITY, MONEY
    And each bar reflects its current value

  Scenario: Card presentation
    Given a card is active
    When the UI renders
    Then the card text is centered
    And an optional emoji placeholder is shown

  Scenario: Two-button decision controls
    Given a card is active
    When the UI renders
    Then a LEFT button is shown for option A
    And a RIGHT button is shown for option B

  Scenario: Disabled option styling
    Given an option is locked
    When the UI renders
    Then the locked button is disabled
    And a short reason is shown under it

  Scenario: Education panel behavior
    Given a heavy feedback event is triggered
    When the UI renders the feedback
    Then the panel blocks further input until confirmed
