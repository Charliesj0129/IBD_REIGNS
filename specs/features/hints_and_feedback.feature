Feature: Hints and Educational Feedback
  Players see impacted stats but not the direction, and receive feedback.

  Scenario: Hint dots show impacted stats only
    Given a card option affects IMMUNE and SANITY
    When the option is highlighted
    Then the hint shows IMMUNE and SANITY
    And the hint does not reveal positive or negative direction

  Scenario: Light feedback for routine events
    Given a routine card without high impact
    When the player chooses an option
    Then a brief toast message is shown
    And the next turn begins without a pause

  Scenario: Heavy feedback for high impact events
    Given a high impact card is flagged as EDUCATIONAL
    When the player chooses an option
    Then a blocking info panel is shown
    And the player must confirm to continue

  Scenario: Optional consult button
    Given a card provides a CONSULT hint
    When the player activates consult
    Then SANITY is reduced by the consult cost
    And the consult hint text is revealed

  Scenario: Placebo hint deception
    Given a placebo card is flagged as DECEPTIVE_HINT
    When the player views the hint
    Then the hint indicates a benefit
    But the actual effect is zero
