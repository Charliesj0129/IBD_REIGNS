Feature: Analytics and Data Tracking
  The game emits structured, privacy-preserving events for analysis.

  Background:
    Given analytics tracking is enabled
    And all events use anonymous session ids

  Scenario: Session start event
    Given the player opens the app
    When the disclaimer is accepted
    Then an event "session_start" is emitted
    And the event includes timestamp and session_id

  Scenario: Session end event
    Given the game ends
    When the end screen is shown
    Then an event "session_end" is emitted
    And it includes ending_id and weeks_survived

  Scenario: Card shown event
    Given a card is rendered
    Then an event "card_shown" is emitted
    And it includes card_id, week, pool, and available_options

  Scenario: Option chosen event
    Given the player selects an option
    Then an event "option_chosen" is emitted
    And it includes card_id, option_side, week
    And it includes stat_deltas and tags_added

  Scenario: Hint consulted event
    Given a card has a consult hint
    When the player opens the consult hint
    Then an event "consult_used" is emitted
    And it includes card_id and sanity_cost

  Scenario: Educational feedback event
    Given a high-impact card is resolved
    When a blocking education panel is shown
    Then an event "education_shown" is emitted
    And it includes education_id and card_id

  Scenario: CTA click event
    Given the CTA section is rendered
    When the player clicks a CTA button
    Then an event "cta_clicked" is emitted
    And it includes ending_id and cta_type

  Scenario: Autopsy report event
    Given the player reaches game over
    When the autopsy report is shown
    Then an event "autopsy_shown" is emitted
    And it includes top_mistakes and contributing_cards

  Scenario: Privacy constraints
    Given any analytics event is emitted
    Then no personal identifiers are included
    And no raw free-text input is captured

  Scenario: Local event buffer
    Given the network is unavailable
    When events are emitted
    Then events are buffered locally
    And flushed when connectivity returns

  Scenario: Data schema validation
    Given an event is emitted
    Then it is validated against the analytics schema
    And invalid events are discarded with a warning
