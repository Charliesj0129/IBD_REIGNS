Feature: Medical Mechanics
  Medical choices model treatment effects and risks.

  Scenario: Steroid rebound after abrupt stop
    Given the player used a steroid card this turn
    When the next turn chooses a STOP_STEROID option
    Then IMMUNE increases sharply instead of decreasing
    And a rebound warning is recorded in the history

  Scenario: Induction dosing sequence
    Given the player starts a biologic therapy
    When the induction schedule begins
    Then the next turns at week+2 and week+6 are forced injection events
    And missing an injection adds RESISTANCE by a large amount

  Scenario: Resistance counter reduces drug efficacy
    Given a biologic card has been used 10 times
    When the same biologic is used again
    Then the effect may fail based on resistance probability

  Scenario: Opportunistic infection risk
    Given IMMUNE is below 20
    When a new turn begins
    Then an infection check occurs
    And an infection event may be forced

  Scenario: Surgery path after perforation
    Given HEALTH reaches 0 or less
    When the death check runs
    Then a forced surgery event is offered instead of immediate death
    And the deck switches to the post-surgery pool if accepted

  Scenario: Drug interaction warning
    Given the player has the tag ANTICOAGULANT
    When a supplement option is presented
    Then the option is flagged as high risk
    And choosing it triggers a bleeding event
