@authentication @registration @regression
Feature: User Registration
  As a new user
  I want to be able to create an account
  So that I can use the application

  Background:
    Given I am on the registration page

  @smoke @happy-path
  Scenario: Successful registration with valid data
    When I fill in the registration form with:
      | field       | value                    |
      | email       | newuser@example.com      |
      | username    | newuser123               |
      | password    | SecurePassword123!       |
      | confirmPass | SecurePassword123!       |
      | fullName    | John Doe                 |
    And I accept the terms and conditions
    And I click the register button
    Then I should see a success message "Registration successful! Please check your email to verify your account."
    And an verification email should be sent to "newuser@example.com"
    And I should be redirected to the login page

  @validation @negative
  Scenario Outline: Registration validation errors
    When I fill in the registration form with:
      | field       | value          |
      | email       | <email>        |
      | username    | <username>     |
      | password    | <password>     |
      | confirmPass | <confirmPass>  |
    And I click the register button
    Then I should see validation error "<errorMessage>"

    Examples:
      | email               | username  | password      | confirmPass   | errorMessage                                    |
      | invalid-email       | user123   | Pass123!      | Pass123!      | Please enter a valid email address             |
      | test@example.com    | us        | Pass123!      | Pass123!      | Username must be at least 3 characters long    |
      | test@example.com    | user123   | pass          | pass          | Password must be at least 8 characters long    |
      | test@example.com    | user123   | password123   | password123   | Password must contain at least one uppercase   |
      | test@example.com    | user123   | PASSWORD123   | PASSWORD123   | Password must contain at least one lowercase   |
      | test@example.com    | user123   | Password      | Password      | Password must contain at least one number      |
      | test@example.com    | user123   | Password123!  | Different123! | Passwords do not match                         |

  @duplicate
  Scenario: Registration with existing email
    Given a user exists with email "existing@example.com"
    When I fill in the registration form with:
      | field       | value                |
      | email       | existing@example.com |
      | username    | newusername          |
      | password    | Password123!         |
      | confirmPass | Password123!         |
    And I click the register button
    Then I should see an error message "Email is already registered"

  @duplicate
  Scenario: Registration with existing username
    Given a user exists with username "existinguser"
    When I fill in the registration form with:
      | field       | value               |
      | email       | newemail@example.com |
      | username    | existinguser        |
      | password    | Password123!        |
      | confirmPass | Password123!        |
    And I click the register button
    Then I should see an error message "Username is already taken"

  @password-strength
  Scenario: Password strength indicator
    When I start typing in the password field
    Then I should see a password strength indicator
    When I enter password "abc"
    Then the password strength should show "Weak"
    When I enter password "abcdefgh"
    Then the password strength should show "Fair"
    When I enter password "Abcdefgh123"
    Then the password strength should show "Good"
    When I enter password "Abcdefgh123!@#"
    Then the password strength should show "Strong"

  @terms
  Scenario: Cannot register without accepting terms
    When I fill in the registration form with valid data
    But I do not accept the terms and conditions
    And I click the register button
    Then I should see validation error "You must accept the terms and conditions"
    And the registration should not proceed

  @email-verification
  Scenario: Email verification process
    Given I have registered with email "verify@example.com"
    When I click the verification link in the email
    Then I should be redirected to the verification success page
    And I should see a message "Email verified successfully! You can now login."
    And my account should be marked as verified
    When I try to login with my credentials
    Then I should be able to login successfully