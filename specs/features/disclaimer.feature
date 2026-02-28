Feature: Disclaimer Blocking Screen
  A mandatory disclaimer protects users and the organization.

  Scenario: Block gameplay until acceptance
    Given the user opens the app for the first time
    When the disclaimer has not been accepted
    Then only the disclaimer screen is shown
    And no game UI is rendered

  Scenario: Disclaimer content requirements
    Given the disclaimer screen is shown
    Then it includes a not-medical-advice statement
    And it explains the simulation is fictional
    And it states the privacy policy for data collection

  Scenario: Acceptance unlocks the game
    Given the disclaimer screen is shown
    When the user clicks the accept button
    Then a session flag accepted_disclaimer is set to true
    And the app reruns
    And the game UI becomes available

  Scenario: Acceptance persists for the session
    Given accepted_disclaimer is true in session state
    When the app reruns
    Then the disclaimer screen is skipped
    And the game UI loads directly
