Feature: Hidden Toxicity Meter
  A hidden variable tracks accumulated gut stress.

  Scenario: Toxicity increases on risky diet choices
    Given a choice is tagged TOXICITY_PLUS
    When the option is selected
    Then hidden TOXICITY increases by the specified amount

  Scenario: Toxicity decreases on relief choices
    Given a choice is tagged TOXICITY_MINUS
    When the option is selected
    Then hidden TOXICITY decreases by the specified amount

  Scenario: Toxicity threshold triggers megacolon event
    Given hidden TOXICITY reaches the threshold
    When the next turn begins
    Then a megacolon event is forced
    And hidden TOXICITY is reset to a safe level
