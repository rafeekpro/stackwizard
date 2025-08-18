@authentication @password-reset @regression
Feature: Password Reset
  As a user who forgot my password
  I want to be able to reset my password
  So that I can regain access to my account

  Background:
    Given I am on the login page

  @smoke @happy-path
  Scenario: Successful password reset flow
    When I click on "Forgot Password?" link
    Then I should be on the password reset page
    When I enter my email "user@example.com"
    And I click the "Send Reset Link" button
    Then I should see a success message "Password reset instructions have been sent to your email"
    And a password reset email should be sent to "user@example.com"
    When I click the reset link in the email
    Then I should be on the password reset form
    When I enter new password "NewSecurePass123!"
    And I confirm new password "NewSecurePass123!"
    And I click the "Reset Password" button
    Then I should see a success message "Password has been reset successfully"
    And I should be redirected to the login page
    When I login with email "user@example.com" and new password "NewSecurePass123!"
    Then I should be logged in successfully

  @validation
  Scenario: Password reset with invalid email
    When I click on "Forgot Password?" link
    And I enter my email "nonexistent@example.com"
    And I click the "Send Reset Link" button
    Then I should see a message "If this email is registered, you will receive password reset instructions"
    And no email should be sent

  @validation
  Scenario: Password reset with invalid email format
    When I click on "Forgot Password?" link
    And I enter my email "invalid-email"
    And I click the "Send Reset Link" button
    Then I should see validation error "Please enter a valid email address"

  @security
  Scenario: Expired password reset token
    Given I have requested a password reset for "user@example.com" 25 hours ago
    When I click the expired reset link
    Then I should see an error message "This password reset link has expired"
    And I should see a button "Request New Reset Link"

  @security
  Scenario: Invalid password reset token
    When I navigate to password reset with invalid token "invalid-token-123"
    Then I should see an error message "Invalid or expired reset token"
    And I should be redirected to the password reset request page

  @validation
  Scenario Outline: New password validation in reset form
    Given I am on the password reset form with valid token
    When I enter new password "<password>"
    And I confirm new password "<password>"
    And I click the "Reset Password" button
    Then I should see validation error "<errorMessage>"

    Examples:
      | password      | errorMessage                                    |
      | short         | Password must be at least 8 characters long    |
      | password123   | Password must contain at least one uppercase   |
      | PASSWORD123   | Password must contain at least one lowercase   |
      | Password      | Password must contain at least one number      |

  @security
  Scenario: Cannot use previous password
    Given I am on the password reset form with valid token
    And my current password is "OldPassword123!"
    When I enter new password "OldPassword123!"
    And I confirm new password "OldPassword123!"
    And I click the "Reset Password" button
    Then I should see an error message "New password cannot be the same as your current password"

  @security
  Scenario: Password reset token can only be used once
    Given I have a valid password reset token
    When I successfully reset my password using the token
    And I try to use the same token again
    Then I should see an error message "This password reset link has already been used"

  @rate-limiting
  Scenario: Rate limiting for password reset requests
    When I click on "Forgot Password?" link
    And I request password reset for "user@example.com" 5 times within 1 minute
    Then I should see an error message "Too many password reset requests. Please try again later"
    And the "Send Reset Link" button should be disabled