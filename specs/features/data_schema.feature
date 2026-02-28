Feature: Data Schema for JSON Content
  Events and endings are defined in JSON for easy authoring.

  Scenario: Event card minimum fields
    Given an event card is defined
    Then it must include id, text, left, right
    And left and right must include label and effect

  Scenario: Optional event fields
    Given an event card is defined
    Then it may include emoji, tags, conditions, weight, education, hint

  Scenario: Conditions fields
    Given a card has conditions
    Then it may include min_week, max_week, min_immune, max_immune
    And it may include required_tags and forbidden_tags

  Scenario: Effect fields
    Given a card option effect is defined
    Then effect may include stat deltas for HEALTH, IMMUNE, SANITY, MONEY
    And effect may include add_tags and remove_tags
    And effect may include hidden toxicity delta

  Scenario: Education fields
    Given a card includes education
    Then education includes title, content, and source
    And education may include image_url

  Scenario: Endings schema
    Given an endings.json entry is defined
    Then it must include id, title, trigger, and description
