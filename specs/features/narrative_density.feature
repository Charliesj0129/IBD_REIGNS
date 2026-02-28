Feature: Narrative Density Enhancements
  Cards carry richer character context and story continuity.

  Scenario: Character name and background
    Given a card is displayed
    Then it includes a character name
    And it includes a short role background (doctor, colleague, family)

  Scenario: Seasonal chapters and thematic pools
    Given the week changes into a new season
    Then the event pool switches to the season chapter
    And events are tagged by theme (diet, treatment, social)

  Scenario: Multi-card story chains
    Given a character arc starts
    When the player sees the first card
    Then the next 2 cards in the chain are scheduled

  Scenario: Foreshadowed text changes
    Given the player made a specific earlier choice
    When a later card is shown
    Then the card text reflects that prior choice

  Scenario: Social consequence follow-up
    Given the player made a social decision
    When the next week starts
    Then a recap card appears describing the consequence

  Scenario: Ending summary
    Given the game ends
    Then the summary lists the top 3 critical mistakes
    And each mistake links to the medical education entry

  Scenario: Small victory story
    Given the player holds stable balance for 4 weeks
    When the streak completes
    Then a small positive story card is shown

  Scenario: Antagonist events
    Given flare or symptoms are triggered
    Then the event is framed as a disruptive antagonist

  Scenario: Emotional support branch
    Given SANITY is low
    Then emotional support cards become eligible

  Scenario: Worldbuilding glossary
    Given the player opens help
    Then a gut-kingdom glossary is available
