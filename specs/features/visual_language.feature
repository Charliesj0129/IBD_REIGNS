Feature: Unified Visual Language
  The UI uses a cohesive art direction inspired by Reigns.

  Scenario: Restricted color palette
    Given the UI theme is loaded
    Then the palette uses 4 to 6 base colors
    And one primary color is defined
    And one warning color is defined

  Scenario: Custom medieval or handwritten font
    Given the UI theme is loaded
    Then the primary font is not a system default
    And the font style feels medieval or handwritten

  Scenario: Parchment card texture
    Given a card is displayed
    Then the card background shows paper texture or subtle noise
    And the card has a defined border and shadow

  Scenario: Silhouette character system
    Given a card includes a character
    Then the character is rendered as a silhouette or single-color pixel art

  Scenario: Unified stat icons
    Given the status bar is shown
    Then HEALTH, IMMUNE, SANITY, MONEY use a consistent icon set

  Scenario: Custom status visualization
    Given the status bar is shown
    Then stats use dot bars or segmented bars
    And native progress bars are not used

  Scenario: Education panel style
    Given a detailed education panel is shown
    Then it is styled like a scroll or doctor note

  Scenario: Ending badge style
    Given an ending screen is shown
    Then a seal or badge is displayed for Good/Bad endings

  Scenario: Micro-animations
    Given a card is shown
    Then card entrance uses a subtle animation
    And result feedback uses a brief animation

  Scenario: Soundscape
    Given a player interacts with a button
    Then a short click sound is played
    And warning and ending sounds are distinct
