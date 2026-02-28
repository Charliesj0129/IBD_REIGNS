Feature: Game Loop and Time
  The game is a fast decision loop with weekly turns and seasonal phases.

  Scenario: Start a new game
    Given a new game session
    When the game initializes
    Then the week counter is set to 1
    And all four stats are set to 50
    And the active card is drawn from the early-game pool

  Scenario: Resolve a turn
    Given an active card is shown
    When the player selects LEFT or RIGHT
    Then the option effects are applied to stats
    And stat values are clamped to 0..100
    And tags are updated
    And the week counter increases by 1
    And the next card is drawn

  Scenario: Seasonal rotation
    Given the week counter is within a season range
    When a new card is drawn
    Then the card is drawn from the season-specific pool

  Scenario: Winter difficulty modifier
    Given the week counter is between 40 and 52
    When a card is resolved
    Then winter modifiers are applied to IMMUNE volatility
    And joint-pain events are more likely

  Scenario: Quarterly checkups
    Given the week counter is 13 or 26 or 39
    When the next card would be drawn
    Then a forced checkup event is inserted
    And the checkup evaluates recent IMMUNE averages
    And the deck is adjusted based on that evaluation

  Scenario: Final endoscopy on week 52
    Given the week counter reaches 52
    When the turn resolves
    Then the final endoscopy evaluation is triggered
    And a yearly ending is selected
