import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor';
import LoginPage from '../../support/page-objects/LoginPage';
import RegistrationPage from '../../support/page-objects/RegistrationPage';
import DashboardPage from '../../support/page-objects/DashboardPage';
import PasswordResetPage from '../../support/page-objects/PasswordResetPage';

const loginPage = new LoginPage();
const registrationPage = new RegistrationPage();
const dashboardPage = new DashboardPage();
const passwordResetPage = new PasswordResetPage();

// Navigation steps
Given('I am on the login page', () => {
  loginPage.visit();
});

Given('I am on the registration page', () => {
  registrationPage.visit();
});

Given('I am logged in as a regular user', () => {
  cy.login(Cypress.env('testUserEmail'), Cypress.env('testUserPassword'));
});

Given('I am logged in as an admin', () => {
  cy.login(Cypress.env('adminEmail'), Cypress.env('adminPassword'));
});

// Login steps
When('I enter email {string}', (email: string) => {
  loginPage.enterEmail(email);
});

When('I enter password {string}', (password: string) => {
  loginPage.enterPassword(password);
});

When('I click the login button', () => {
  loginPage.clickLoginButton();
});

When('I check the {string} checkbox', (checkboxLabel: string) => {
  loginPage.checkRememberMe();
});

Then('I should be redirected to the dashboard', () => {
  dashboardPage.verifyOnDashboard();
});

Then('I should see a welcome message', () => {
  dashboardPage.verifyWelcomeMessage();
});

Then('I should see my user profile in the navigation', () => {
  dashboardPage.verifyUserProfile();
});

Then('I should see an error message {string}', (message: string) => {
  cy.contains(message).should('be.visible');
});

Then('I should remain on the login page', () => {
  loginPage.verifyOnLoginPage();
});

// Registration steps
When('I fill in the registration form with:', (dataTable: any) => {
  const data = dataTable.rowsHash();
  registrationPage.fillRegistrationForm(data);
});

When('I accept the terms and conditions', () => {
  registrationPage.acceptTerms();
});

When('I do not accept the terms and conditions', () => {
  // Intentionally not checking the terms checkbox
});

When('I click the register button', () => {
  registrationPage.clickRegisterButton();
});

Then('I should see a success message {string}', (message: string) => {
  cy.contains(message).should('be.visible');
});

Then('an verification email should be sent to {string}', (email: string) => {
  // This would typically check a test email service or mock
  cy.task('checkEmail', email).then((emailSent) => {
    expect(emailSent).to.be.true;
  });
});

Then('I should be redirected to the login page', () => {
  loginPage.verifyOnLoginPage();
});

// Validation steps
Then('I should see validation error {string}', (errorMessage: string) => {
  cy.contains(errorMessage).should('be.visible');
});

// Password field steps
Then('the password field should be of type {string}', (fieldType: string) => {
  loginPage.getPasswordField().should('have.attr', 'type', fieldType);
});

Then('the password should not be visible', () => {
  loginPage.getPasswordField().should('have.attr', 'type', 'password');
});

// Keyboard navigation steps
When('I press Tab key', () => {
  cy.focused().tab();
});

When('I press Enter key', () => {
  cy.focused().type('{enter}');
});

Then('the email field should be focused', () => {
  loginPage.getEmailField().should('be.focused');
});

Then('the password field should be focused', () => {
  loginPage.getPasswordField().should('be.focused');
});

Then('the login form should be submitted', () => {
  // Verify form submission (could check network request)
  cy.wait('@loginRequest');
});

// Session steps
When('my session expires', () => {
  // Simulate session expiration
  cy.clearCookies();
  cy.clearLocalStorage();
});

When('I try to access a protected page', () => {
  dashboardPage.visit();
});

Then('a persistent session cookie should be created', () => {
  cy.getCookie('session').should('exist').and('have.property', 'expiry');
});

// Rate limiting steps
When('I attempt to login with invalid credentials {int} times', (attempts: number) => {
  for (let i = 0; i < attempts; i++) {
    loginPage.enterEmail('invalid@example.com');
    loginPage.enterPassword('WrongPassword123!');
    loginPage.clickLoginButton();
    cy.wait(100); // Small delay between attempts
  }
});

Then('I should see a rate limit error message', () => {
  cy.contains(/too many attempts|rate limit/i).should('be.visible');
});

Then('the login button should be disabled for {int} seconds', (seconds: number) => {
  loginPage.getLoginButton().should('be.disabled');
  // Optionally verify it's enabled after the timeout
  cy.wait(seconds * 1000);
  loginPage.getLoginButton().should('not.be.disabled');
});

// Password reset steps
When('I click on {string} link', (linkText: string) => {
  cy.contains(linkText).click();
});

Then('I should be on the password reset page', () => {
  passwordResetPage.verifyOnPasswordResetPage();
});

When('I enter my email {string}', (email: string) => {
  passwordResetPage.enterEmail(email);
});

When('I click the {string} button', (buttonText: string) => {
  cy.contains('button', buttonText).click();
});

Then('a password reset email should be sent to {string}', (email: string) => {
  cy.task('checkPasswordResetEmail', email).then((emailSent) => {
    expect(emailSent).to.be.true;
  });
});

When('I click the reset link in the email', () => {
  // Simulate clicking the reset link
  cy.task('getPasswordResetToken').then((token) => {
    cy.visit(`/reset-password?token=${token}`);
  });
});

Then('I should be on the password reset form', () => {
  passwordResetPage.verifyOnPasswordResetForm();
});

When('I enter new password {string}', (password: string) => {
  passwordResetPage.enterNewPassword(password);
});

When('I confirm new password {string}', (password: string) => {
  passwordResetPage.confirmNewPassword(password);
});

When('I login with email {string} and new password {string}', (email: string, password: string) => {
  loginPage.visit();
  loginPage.enterEmail(email);
  loginPage.enterPassword(password);
  loginPage.clickLoginButton();
});

Then('I should be logged in successfully', () => {
  dashboardPage.verifyOnDashboard();
});

// User existence steps
Given('a user exists with email {string}', (email: string) => {
  cy.task('createUser', { email });
});

Given('a user exists with username {string}', (username: string) => {
  cy.task('createUser', { username });
});

// Password strength indicator steps
When('I start typing in the password field', () => {
  registrationPage.getPasswordField().click();
});

Then('I should see a password strength indicator', () => {
  registrationPage.getPasswordStrengthIndicator().should('be.visible');
});

Then('the password strength should show {string}', (strength: string) => {
  registrationPage.getPasswordStrengthIndicator()
    .should('contain', strength);
});

// Email verification steps
Given('I have registered with email {string}', (email: string) => {
  cy.task('createUnverifiedUser', { email });
});

When('I click the verification link in the email', () => {
  cy.task('getVerificationToken').then((token) => {
    cy.visit(`/verify-email?token=${token}`);
  });
});

Then('I should be redirected to the verification success page', () => {
  cy.url().should('include', '/verification-success');
});

Then('my account should be marked as verified', () => {
  cy.task('checkUserVerified').then((isVerified) => {
    expect(isVerified).to.be.true;
  });
});

// Password reset token steps
Given('I have requested a password reset for {string} {int} hours ago', (email: string, hours: number) => {
  cy.task('createExpiredPasswordResetToken', { email, hoursAgo: hours });
});

When('I click the expired reset link', () => {
  cy.task('getExpiredPasswordResetToken').then((token) => {
    cy.visit(`/reset-password?token=${token}`);
  });
});

When('I navigate to password reset with invalid token {string}', (token: string) => {
  cy.visit(`/reset-password?token=${token}`);
});

Given('I am on the password reset form with valid token', () => {
  cy.task('createPasswordResetToken').then((token) => {
    cy.visit(`/reset-password?token=${token}`);
  });
});

Given('my current password is {string}', (password: string) => {
  cy.task('setUserPassword', password);
});

Given('I have a valid password reset token', () => {
  cy.task('createPasswordResetToken').as('resetToken');
});

When('I successfully reset my password using the token', () => {
  cy.get('@resetToken').then((token) => {
    cy.visit(`/reset-password?token=${token}`);
    passwordResetPage.enterNewPassword('NewPassword123!');
    passwordResetPage.confirmNewPassword('NewPassword123!');
    cy.contains('button', 'Reset Password').click();
  });
});

When('I try to use the same token again', () => {
  cy.get('@resetToken').then((token) => {
    cy.visit(`/reset-password?token=${token}`);
  });
});

When('I request password reset for {string} {int} times within {int} minute', 
  (email: string, times: number, minutes: number) => {
  for (let i = 0; i < times; i++) {
    passwordResetPage.enterEmail(email);
    cy.contains('button', 'Send Reset Link').click();
    cy.wait(100);
  }
});

Then('no email should be sent', () => {
  cy.task('checkEmailSent').then((emailSent) => {
    expect(emailSent).to.be.false;
  });
});

Then('the {string} button should be disabled', (buttonText: string) => {
  cy.contains('button', buttonText).should('be.disabled');
});