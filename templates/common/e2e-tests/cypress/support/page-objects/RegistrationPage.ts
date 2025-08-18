export default class RegistrationPage {
  private selectors = {
    emailInput: '[data-cy=register-email], #register-email',
    usernameInput: '[data-cy=register-username], #register-username',
    passwordInput: '[data-cy=register-password], #register-password',
    confirmPasswordInput: '[data-cy=register-confirm-password], #confirm-password',
    fullNameInput: '[data-cy=register-fullname], #fullname',
    termsCheckbox: '[data-cy=terms-checkbox], #terms',
    registerButton: '[data-cy=register-button], button[type="submit"]',
    passwordStrengthIndicator: '[data-cy=password-strength], .password-strength',
    errorMessage: '[data-cy=error-message], .error-message',
    successMessage: '[data-cy=success-message], .success-message',
  };

  visit(): void {
    cy.visit('/register');
  }

  getEmailField(): Cypress.Chainable {
    return cy.get(this.selectors.emailInput);
  }

  getUsernameField(): Cypress.Chainable {
    return cy.get(this.selectors.usernameInput);
  }

  getPasswordField(): Cypress.Chainable {
    return cy.get(this.selectors.passwordInput);
  }

  getConfirmPasswordField(): Cypress.Chainable {
    return cy.get(this.selectors.confirmPasswordInput);
  }

  getFullNameField(): Cypress.Chainable {
    return cy.get(this.selectors.fullNameInput);
  }

  getPasswordStrengthIndicator(): Cypress.Chainable {
    return cy.get(this.selectors.passwordStrengthIndicator);
  }

  fillRegistrationForm(data: {
    email?: string;
    username?: string;
    password?: string;
    confirmPass?: string;
    fullName?: string;
  }): void {
    if (data.email) {
      this.getEmailField().clear().type(data.email);
    }
    if (data.username) {
      this.getUsernameField().clear().type(data.username);
    }
    if (data.password) {
      this.getPasswordField().clear().type(data.password);
    }
    if (data.confirmPass) {
      this.getConfirmPasswordField().clear().type(data.confirmPass);
    }
    if (data.fullName) {
      this.getFullNameField().clear().type(data.fullName);
    }
  }

  acceptTerms(): void {
    cy.get(this.selectors.termsCheckbox).check();
  }

  clickRegisterButton(): void {
    cy.get(this.selectors.registerButton).click();
  }

  register(email: string, username: string, password: string): void {
    this.fillRegistrationForm({
      email,
      username,
      password,
      confirmPass: password,
    });
    this.acceptTerms();
    this.clickRegisterButton();
  }

  verifyOnRegistrationPage(): void {
    cy.url().should('include', '/register');
    this.getEmailField().should('be.visible');
    this.getPasswordField().should('be.visible');
  }

  verifyErrorMessage(message: string): void {
    cy.get(this.selectors.errorMessage).should('contain', message);
  }

  verifySuccessMessage(message: string): void {
    cy.get(this.selectors.successMessage).should('contain', message);
  }
}