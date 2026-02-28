Feature: Traditional Chinese Localization
  All UI and content are served in zh-TW.

  Scenario: UI strings from zh-TW file
    Given the UI loads
    Then all visible labels are loaded from i18n/zh_TW.json

  Scenario: Card content localization
    Given a card is displayed
    Then its text and options are rendered in Traditional Chinese

  Scenario: Stat labels localization
    Given the status bar is shown
    Then the stat labels use Traditional Chinese terms

  Scenario: Consistent units and typography
    Given the UI is rendered
    Then line height is between 1.4 and 1.6
    And base font size is at least 16px
