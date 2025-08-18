@admin @user-management @regression
Feature: Admin User Management
  As an administrator
  I want to manage user accounts
  So that I can maintain system security and user access

  Background:
    Given I am logged in as an admin
    And I navigate to the admin dashboard
    And I go to the "Users" section

  @smoke @happy-path
  Scenario: View all users list
    Then I should see a list of all users
    And I should see the following columns:
      | column        |
      | ID            |
      | Email         |
      | Username      |
      | Full Name     |
      | Status        |
      | Role          |
      | Created Date  |
      | Actions       |
    And I should see pagination controls
    And I should see a search bar

  @search
  Scenario: Search for users
    When I search for "john"
    Then I should see only users matching "john" in their:
      | field    |
      | email    |
      | username |
      | fullName |
    When I clear the search
    Then I should see all users again

  @filter
  Scenario: Filter users by status
    When I filter users by status "Active"
    Then I should see only active users
    When I filter users by status "Inactive"
    Then I should see only inactive users
    When I filter users by status "All"
    Then I should see all users

  @filter
  Scenario: Filter users by role
    When I filter users by role "Admin"
    Then I should see only admin users
    When I filter users by role "User"
    Then I should see only regular users

  @sort
  Scenario: Sort users by different columns
    When I click on the "Email" column header
    Then users should be sorted by email ascending
    When I click on the "Email" column header again
    Then users should be sorted by email descending
    When I click on the "Created Date" column header
    Then users should be sorted by creation date

  @create
  Scenario: Create a new user as admin
    When I click the "Add New User" button
    And I fill in the new user form with:
      | field       | value                |
      | email       | newadmin@example.com |
      | username    | newadmin             |
      | fullName    | New Admin User       |
      | password    | TempPass123!         |
      | role        | Admin                |
      | status      | Active               |
    And I check "Send welcome email"
    And I click the "Create User" button
    Then I should see a success message "User created successfully"
    And the new user should appear in the users list
    And a welcome email should be sent to "newadmin@example.com"

  @edit
  Scenario: Edit existing user details
    Given a user "edituser@example.com" exists
    When I click the edit button for user "edituser@example.com"
    And I update the user details:
      | field    | value         |
      | fullName | Updated User  |
      | role     | Admin         |
      | status   | Active        |
    And I click the "Save Changes" button
    Then I should see a success message "User updated successfully"
    And the user details should be updated in the list

  @activate
  Scenario: Activate a deactivated user
    Given a deactivated user "inactive@example.com" exists
    When I click the action menu for user "inactive@example.com"
    And I select "Activate User"
    Then I should see a confirmation dialog
    When I confirm the action
    Then I should see a success message "User activated successfully"
    And the user status should show as "Active"

  @deactivate
  Scenario: Deactivate an active user
    Given an active user "active@example.com" exists
    When I click the action menu for user "active@example.com"
    And I select "Deactivate User"
    Then I should see a confirmation dialog
    When I confirm the action
    Then I should see a success message "User deactivated successfully"
    And the user status should show as "Inactive"

  @permissions
  Scenario: Grant admin privileges to a user
    Given a regular user "regular@example.com" exists
    When I click the action menu for user "regular@example.com"
    And I select "Make Admin"
    Then I should see a warning dialog about granting admin privileges
    When I confirm the action
    Then I should see a success message "Admin privileges granted"
    And the user role should show as "Admin"

  @permissions
  Scenario: Revoke admin privileges from a user
    Given an admin user "admin@example.com" exists
    When I click the action menu for user "admin@example.com"
    And I select "Remove Admin"
    Then I should see a warning dialog about revoking admin privileges
    When I confirm the action
    Then I should see a success message "Admin privileges revoked"
    And the user role should show as "User"

  @reset-password
  Scenario: Force password reset for a user
    Given a user "reset@example.com" exists
    When I click the action menu for user "reset@example.com"
    And I select "Force Password Reset"
    Then I should see a confirmation dialog
    When I confirm the action
    Then I should see a success message "Password reset email sent"
    And a password reset email should be sent to the user

  @verify
  Scenario: Manually verify user email
    Given an unverified user "unverified@example.com" exists
    When I click the action menu for user "unverified@example.com"
    And I select "Verify Email"
    Then I should see a success message "Email verified successfully"
    And the user should show as verified

  @bulk
  Scenario: Bulk actions on multiple users
    When I select multiple users using checkboxes
    And I click the "Bulk Actions" dropdown
    And I select "Deactivate Selected"
    Then I should see a confirmation dialog
    When I confirm the bulk action
    Then I should see a success message "3 users deactivated"
    And all selected users should be deactivated

  @export
  Scenario: Export users list
    When I click the "Export" button
    Then I should see export format options:
      | format |
      | CSV    |
      | Excel  |
      | JSON   |
    When I select "CSV" format
    And I click "Download"
    Then a CSV file with all users should be downloaded

  @audit
  Scenario: View user audit log
    Given a user "audit@example.com" exists
    When I click the action menu for user "audit@example.com"
    And I select "View Audit Log"
    Then I should see the user's activity history:
      | action              | performed_by | timestamp          |
      | Account Created     | System       | 2024-01-01 10:00   |
      | Password Changed    | User         | 2024-01-02 14:30   |
      | Role Updated        | Admin        | 2024-01-03 09:15   |

  @impersonate
  Scenario: Impersonate a user
    Given a user "impersonate@example.com" exists
    When I click the action menu for user "impersonate@example.com"
    And I select "Login as User"
    Then I should see a warning about impersonation
    When I confirm the impersonation
    Then I should be logged in as the user
    And I should see an impersonation banner
    When I click "End Impersonation"
    Then I should return to my admin account

  @statistics
  Scenario: View user statistics
    When I click the "Statistics" tab
    Then I should see user statistics:
      | metric                | value |
      | Total Users           | 150   |
      | Active Users          | 142   |
      | Inactive Users        | 8     |
      | Verified Users        | 135   |
      | Admin Users           | 5     |
      | New Users (This Month)| 12    |
    And I should see charts for user growth
    And I should see activity trends