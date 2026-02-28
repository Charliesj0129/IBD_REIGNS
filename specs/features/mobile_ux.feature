Feature: Mobile-First UX
  The UI is optimized for one-handed, fast play on phones.

  Scenario: Single-column layout on small screens
    Given the viewport width is less than 768px
    When the main screen renders
    Then the layout uses a single column
    And controls are stacked vertically

  Scenario: Thumb-friendly decision buttons
    Given a card is active
    When the options render on a phone
    Then the left and right buttons are full width
    And each button height is at least 48px
    And the primary action is placed within thumb reach

  Scenario: Minimal top chrome
    Given a phone viewport
    When the status bars render
    Then only compact labels are shown
    And the stat bars use minimal vertical space

  Scenario: Swipe-like interaction hints
    Given a phone viewport
    When options are shown
    Then the UI hints at left or right swipe direction

  Scenario: Accessibility tap targets
    Given a phone viewport
    When interactive elements render
    Then all tap targets are at least 44px in height
    And text contrast meets AA standards

  Scenario: Resume state on refresh
    Given a player has an active session
    When the app reruns
    Then the last active card is preserved
    And the current stats remain unchanged

  Scenario: Offline-friendly assets
    Given the player is on a slow connection
    When the UI renders
    Then only local assets are used for critical UI
    And no external media blocks gameplay
