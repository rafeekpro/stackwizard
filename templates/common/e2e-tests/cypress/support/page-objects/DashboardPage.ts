export default class DashboardPage {
  private selectors = {
    welcomeMessage: '[data-cy=welcome-message], .welcome-message',
    userProfile: '[data-cy=user-profile], .user-profile',
    userAvatar: '[data-cy=user-avatar], .user-avatar',
    userName: '[data-cy=user-name], .user-name',
    logoutButton: '[data-cy=logout-button], button:contains("Logout")',
    navigationMenu: '[data-cy=nav-menu], nav',
    dashboardContent: '[data-cy=dashboard-content], .dashboard',
  };

  visit(): void {
    cy.visit('/dashboard');
  }

  verifyOnDashboard(): void {
    cy.url().should('include', '/dashboard');
    cy.get(this.selectors.dashboardContent).should('be.visible');
  }

  verifyWelcomeMessage(): void {
    cy.get(this.selectors.welcomeMessage).should('be.visible');
  }

  verifyUserProfile(): void {
    cy.get(this.selectors.userProfile).should('be.visible');
  }

  getUserName(): Cypress.Chainable {
    return cy.get(this.selectors.userName);
  }

  clickLogout(): void {
    cy.get(this.selectors.logoutButton).click();
  }

  navigateToSection(section: string): void {
    cy.get(this.selectors.navigationMenu)
      .contains(section)
      .click();
  }

  verifyUserIsLoggedIn(username: string): void {
    this.getUserName().should('contain', username);
  }
}