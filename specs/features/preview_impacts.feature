Feature: Impact Preview and Risk Signaling
  Players can preview the exact magnitude of stat changes.

  Scenario: Press-and-hold preview panel
    Given a card is displayed
    When the player presses and holds an option
    Then the preview panel shows each stat delta as a signed number

  Scenario: Magnitude visualization
    Given a preview panel is shown
    Then deltas are categorized as small, medium, or large
    And the category is visualized with arrows or bars

  Scenario: Tiered hint mode
    Given the player is in basic hint mode
    Then only impacted stats and magnitude tiers are shown
    Given the player is in advanced hint mode
    Then exact numeric deltas are shown

  Scenario: High-risk alert
    Given a preview shows any delta above the risk threshold
    Then a high-risk badge appears

  Scenario: Placebo clarity
    Given a placebo card is previewed
    Then the preview shows zero change
    And no positive color is applied
