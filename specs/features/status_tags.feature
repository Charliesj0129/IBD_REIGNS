Feature: Status Tags (Buffs and Debuffs)
  Tags persist across turns and modify card effects or text.

  Scenario: Gain a tag from a choice
    Given a card option adds the tag MOON_FACE
    When the option is selected
    Then the player gains the MOON_FACE tag

  Scenario: Tag modifies future card text
    Given the player has the tag MOON_FACE
    When a social photo card appears
    Then the option text is replaced with a self-conscious variant

  Scenario: Tag modifies numerical effects
    Given the player has the tag ANEMIA
    When a work reward is applied
    Then the MONEY gain is reduced by 50 percent

  Scenario: Steroid dependence forces immune rise
    Given the player has the tag STEROID_DEPENDENT
    When a turn ends without steroid use
    Then IMMUNE increases by a fixed amount
