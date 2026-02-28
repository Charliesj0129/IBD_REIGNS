Feature: Interaction Feel and Gesture Controls
  Mobile interaction mimics swipe decisions and provides rich feedback.

  Scenario: Swipe or drag gesture input
    Given a card is active on mobile
    When the user drags left or right
    Then the choice is previewed
    And releasing commits the choice

  Scenario: Edge tap decision zones
    Given a card is active
    When the user taps the left edge
    Then the left option is selected
    When the user taps the right edge
    Then the right option is selected

  Scenario: Long-press preview
    Given a card option is available
    When the user long-presses the option
    Then a preview panel shows affected stats and magnitude

  Scenario: Floating delta animation
    Given a choice is resolved
    Then floating delta numbers appear near each stat

  Scenario: Near-death warning
    Given a stat approaches a death threshold
    Then the screen briefly flashes or shakes

  Scenario: Auto-advance rhythm
    Given a non-blocking event resolves
    Then the next card appears after 0.5 seconds

  Scenario: CTA interactions
    Given the game ends
    Then CTA buttons allow share, copy link, and QR display

  Scenario: Haptic feedback
    Given the user taps a decision
    Then a short vibration feedback occurs

  Scenario: Critical confirmation
    Given a critical decision is selected
    Then a confirm prompt appears before commit

  Scenario: Post-death suggestion
    Given the player dies
    Then the UI shows a next attempt suggestion
