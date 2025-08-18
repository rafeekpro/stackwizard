@authentication @regression
Feature: User Login
  As a user
  I want to be able to login to the application
  So that I can access protected features

  Background:
    Given I am on the login page

  @smoke @happy-path
  Scenario: Successful login with valid credentials
    When I enter email "testuser@example.com"
    And I enter password "TestUser123!"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message
    And I should see my user profile in the navigation

  @negative
  Scenario: Failed login with invalid credentials
    When I enter email "invalid@example.com"
    And I enter password "WrongPassword123!"
    And I click the login button
    Then I should see an error message "Invalid email or password"
    And I should remain on the login page

  @negative
  Scenario: Failed login with empty fields
    When I click the login button
    Then I should see validation error "Email is required"
    And I should see validation error "Password is required"

  @security
  Scenario: Password is masked in the input field
    When I enter password "TestPassword123!"
    Then the password field should be of type "password"
    And the password should not be visible

  @accessibility
  Scenario: Login form is accessible via keyboard
    When I press Tab key
    Then the email field should be focused
    When I enter email "test@example.com"
    And I press Tab key
    Then the password field should be focused
    When I enter password "Password123!"
    And I press Enter key
    Then the login form should be submitted

  @remember-me
  Scenario: Remember me functionality
    When I enter email "testuser@example.com"
    And I enter password "TestUser123!"
    And I check the "Remember me" checkbox
    And I click the login button
    Then I should be logged in successfully
    And a persistent session cookie should be created

  @session
  Scenario: Session timeout redirect
    Given I am logged in as a regular user
    When my session expires
    And I try to access a protected page
    Then I should be redirected to the login page
    And I should see a message "Your session has expired"

  @rate-limiting
  Scenario: Rate limiting after multiple failed attempts
    When I attempt to login with invalid credentials 5 times
    Then I should see a rate limit error message
    And the login button should be disabled for 60 seconds