@users @profile @regression
Feature: User Profile Management
  As a logged-in user
  I want to manage my profile
  So that I can keep my information up to date

  Background:
    Given I am logged in as a regular user
    And I navigate to my profile page

  @smoke @happy-path
  Scenario: View user profile information
    Then I should see my profile information:
      | field    | value                  |
      | email    | testuser@example.com   |
      | username | testuser               |
      | fullName | Test User              |
    And I should see my account status as "Active"
    And I should see my account creation date

  @update
  Scenario: Successfully update profile information
    When I click the "Edit Profile" button
    And I update my profile with:
      | field    | value           |
      | fullName | Updated Name    |
      | username | updateduser     |
    And I click the "Save Changes" button
    Then I should see a success message "Profile updated successfully"
    And I should see the updated information in my profile

  @update @validation
  Scenario: Cannot update to existing username
    Given another user exists with username "existinguser"
    When I click the "Edit Profile" button
    And I update my username to "existinguser"
    And I click the "Save Changes" button
    Then I should see an error message "Username is already taken"

  @password
  Scenario: Change password successfully
    When I click the "Change Password" button
    And I enter my current password "TestUser123!"
    And I enter new password "NewPassword123!"
    And I confirm new password "NewPassword123!"
    And I click the "Update Password" button
    Then I should see a success message "Password changed successfully"
    And I should be logged out for security
    When I login with my new password "NewPassword123!"
    Then I should be logged in successfully

  @password @validation
  Scenario: Cannot change password with wrong current password
    When I click the "Change Password" button
    And I enter my current password "WrongPassword123!"
    And I enter new password "NewPassword123!"
    And I confirm new password "NewPassword123!"
    And I click the "Update Password" button
    Then I should see an error message "Current password is incorrect"

  @avatar
  Scenario: Upload profile avatar
    When I click the "Change Avatar" button
    And I upload an image file "avatar.jpg"
    Then I should see a preview of the image
    When I click the "Save Avatar" button
    Then I should see a success message "Avatar updated successfully"
    And I should see my new avatar in the profile

  @avatar @validation
  Scenario: Reject invalid file types for avatar
    When I click the "Change Avatar" button
    And I try to upload a file "document.pdf"
    Then I should see an error message "Only image files are allowed"

  @preferences
  Scenario: Update notification preferences
    When I navigate to the "Preferences" tab
    And I toggle the following preferences:
      | preference           | value |
      | Email notifications  | off   |
      | Push notifications   | on    |
      | Newsletter          | off   |
    And I click the "Save Preferences" button
    Then I should see a success message "Preferences updated"
    And the preferences should be saved correctly

  @privacy
  Scenario: Update privacy settings
    When I navigate to the "Privacy" tab
    And I set my profile visibility to "Private"
    And I enable two-factor authentication
    And I click the "Save Privacy Settings" button
    Then I should see a success message "Privacy settings updated"
    And I should receive a confirmation email

  @delete
  Scenario: Deactivate account
    When I navigate to the "Account" tab
    And I click the "Deactivate Account" button
    Then I should see a warning dialog
    When I type "DELETE" in the confirmation field
    And I enter my password "TestUser123!"
    And I click the "Confirm Deactivation" button
    Then I should see a message "Account deactivated successfully"
    And I should be logged out
    When I try to login with my credentials
    Then I should see an error message "Account is deactivated"

  @sessions
  Scenario: View and manage active sessions
    When I navigate to the "Security" tab
    Then I should see a list of active sessions
    And I should see the current session marked
    When I click "Terminate" on another session
    Then I should see a success message "Session terminated"
    And that session should be removed from the list

  @export
  Scenario: Export personal data
    When I navigate to the "Data & Privacy" tab
    And I click the "Export My Data" button
    Then I should see export options:
      | format |
      | JSON   |
      | CSV    |
      | PDF    |
    When I select "JSON" format
    And I click the "Download" button
    Then a file should be downloaded containing my data

  @activity
  Scenario: View account activity log
    When I navigate to the "Activity" tab
    Then I should see my recent account activity:
      | action           | timestamp          |
      | Login            | Today at 10:00 AM  |
      | Profile Updated  | Yesterday          |
      | Password Changed | 3 days ago         |
    And I should be able to filter by activity type
    And I should be able to search activities