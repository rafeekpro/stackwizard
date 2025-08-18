export default class LoginPage {
  private selectors = {
    emailInput: '[data-cy=email-input], #email',
    passwordInput: '[data-cy=password-input], #password',
    loginButton: '[data-cy=login-button], button[type="submit"]',
    rememberMeCheckbox: '[data-cy=remember-me], #remember-me',
    forgotPasswordLink: '[data-cy=forgot-password], a:contains("Forgot Password")',
    errorMessage: '[data-cy=error-message], .error-message',
    validationError: '[data-cy=validation-error], .validation-error',
  };

  visit(): void {
    cy.visit('/login');
  }

  getEmailField(): Cypress.Chainable {
    return cy.get(this.selectors.emailInput);
  }

  getPasswordField(): Cypress.Chainable {
    return cy.get(this.selectors.passwordInput);
  }

  getLoginButton(): Cypress.Chainable {
    return cy.get(this.selectors.loginButton);
  }

  enterEmail(email: string): void {
    this.getEmailField().clear().type(email);
  }

  enterPassword(password: string): void {
    this.getPasswordField().clear().type(password);
  }

  clickLoginButton(): void {
    this.getLoginButton().click();
  }

  checkRememberMe(): void {
    cy.get(this.selectors.rememberMeCheckbox).check();
  }

  clickForgotPassword(): void {
    cy.get(this.selectors.forgotPasswordLink).click();
  }

  login(email: string, password: string): void {
    this.enterEmail(email);
    this.enterPassword(password);
    this.clickLoginButton();
  }

  verifyOnLoginPage(): void {
    cy.url().should('include', '/login');
    this.getEmailField().should('be.visible');
    this.getPasswordField().should('be.visible');
  }

  getErrorMessage(): Cypress.Chainable {
    return cy.get(this.selectors.errorMessage);
  }

  getValidationError(): Cypress.Chainable {
    return cy.get(this.selectors.validationError);
  }

  verifyErrorMessage(message: string): void {
    this.getErrorMessage().should('contain', message);
  }

  verifyValidationError(message: string): void {
    this.getValidationError().should('contain', message);
  }
}