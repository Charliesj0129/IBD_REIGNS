Feature: Card Engine and Deck Rules
  Cards are JSON-defined events with conditions and two choices.

  Scenario: Load deck from JSON
    Given an events.json file is present
    When the game loads the deck
    Then each card is validated against the schema
    And invalid cards are rejected with a clear error

  Scenario: Unlock conditions
    Given a card requires MIN_IMMUNE=60
    When IMMUNE is 59
    Then the card is not eligible to draw
    When IMMUNE is 60
    Then the card becomes eligible to draw

  Scenario: Required tags
    Given a card requires the tag STEROID_DEPENDENT
    When the player lacks that tag
    Then the card is not eligible to draw

  Scenario: Weighted randomness
    Given multiple eligible cards exist
    When the engine draws a card
    Then weights influence the selection probability

  Scenario: Prevent immediate repeats
    Given a card was shown last turn
    When a new card is drawn
    Then the same card is excluded for at least 1 turn

  Scenario: Option lock based on money
    Given a card option costs MONEY 30
    And the player has MONEY 20
    When the card is rendered
    Then that option is disabled
    And the player can only select the other option

  Scenario: Apply effects after choice
    Given the player chooses LEFT
    When the option effects are applied
    Then stat deltas are applied
    And tags are added or removed
    And any queued events are scheduled
