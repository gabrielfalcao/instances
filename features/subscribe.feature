Feature: Subscribing for beta
  As an open source developer
  In order to enjoy instanc.es
  I want to subscribe for the public beta

  Scenario: Subscribe for public beta
    Given that an anonymous user goes to "/"
    When I fill up the "email" with "foo@bar.com"
    And submit the form
    Then the email "foo@bar.com" is recorded as subscriber

  Scenario: Subscribe for private beta
    Given that an anonymous user goes to "/"
    When I fill up the "email" with "foo@bar.com"
    And check the option "I want to donate and get in the private beta"
    Then the email "foo@bar.com" is recorded as beta donator
