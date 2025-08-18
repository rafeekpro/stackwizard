export default class PasswordResetPage {
  private selectors = {
    emailInput: '[data-cy=reset-email], #reset-email',
    newPasswordInput: '[data-cy=new-password], #new-password',
    confirmPasswordInput: '[data-cy=confirm-new-password], #confirm-new-password',
    sendResetButton: '[data-cy=send-reset-button], button:contains("Send Reset Link")',
    resetPasswordButton: '[data-cy=reset-password-button], button:contains("Reset Password")',
    successMessage: '[data-cy=success-message], .success-message',
    errorMessage: '[data-cy=error-message], .error-message',
  };

  visit(): void {
    cy.visit('/password-reset');
  }

  visitWithToken(token: string): void {
    cy.visit(`/password-reset?token=${token}`);
  }

  getEmailField(): Cypress.Chainable {
    return cy.get(this.selectors.emailInput);
  }

  getNewPasswordField(): Cypress.Chainable {
    return cy.get(this.selectors.newPasswordInput);
  }

  getConfirmPasswordField(): Cypress.Chainable {
    return cy.get(this.selectors.confirmPasswordInput);
  }

  enterEmail(email: string): void {
    this.getEmailField().clear().type(email);
  }

  enterNewPassword(password: string): void {
    this.getNewPasswordField().clear().type(password);
  }

  confirmNewPassword(password: string): void {
    this.getConfirmPasswordField().clear().type(password);
  }

  clickSendResetLink(): void {
    cy.get(this.selectors.sendResetButton).click();
  }

  clickResetPassword(): void {
    cy.get(this.selectors.resetPasswordButton).click();
  }

  verifyOnPasswordResetPage(): void {
    cy.url().should('include', '/password-reset');
    this.getEmailField().should('be.visible');
  }

  verifyOnPasswordResetForm(): void {
    cy.url().should('include', 'token=');
    this.getNewPasswordField().should('be.visible');
    this.getConfirmPasswordField().should('be.visible');
  }

  verifySuccessMessage(message: string): void {
    cy.get(this.selectors.successMessage).should('contain', message);
  }

  verifyErrorMessage(message: string): void {
    cy.get(this.selectors.errorMessage).should('contain', message);
  }

  requestPasswordReset(email: string): void {
    this.enterEmail(email);
    this.clickSendResetLink();
  }

  resetPassword(newPassword: string): void {
    this.enterNewPassword(newPassword);
    this.confirmNewPassword(newPassword);
    this.clickResetPassword();
  }
}