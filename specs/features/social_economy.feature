Feature: Social and Economic Pressure
  Social capital constrains choices and adds stress.

  Scenario: Financial lock on premium treatments
    Given MONEY is below 10
    When a premium treatment card appears
    Then the paid option is disabled
    And only the covered option is selectable

  Scenario: Urgency override
    Given an urgency event is triggered
    When the event is rendered
    Then only one forced action is available
    And SANITY and MONEY are reduced accordingly

  Scenario: Dr Google misinformation
    Given a misinformation card appears
    When the player chooses to believe it
    Then SANITY increases briefly
    And HEALTH decreases significantly

  Scenario: Work strain increases immune activity
    Given a heavy overtime event is selected
    When effects resolve
    Then SANITY decreases
    And IMMUNE increases via stress coupling
