# StackWizard Development Makefile
# Run all tests locally before pushing to GitHub

.PHONY: help test test-all test-quick test-docker pre-commit clean

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "StackWizard Test Orchestration"
	@echo "=============================="
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

test-quick: ## Run quick tests (package, structure, lint)
	@echo "$(YELLOW)Running quick tests...$(NC)"
	@npm run lint
	@npm run format:check
	@npm run test:package
	@npm run test:structure
	@echo "$(GREEN)✅ Quick tests passed!$(NC)"

test-docker: ## Run Docker integration tests
	@echo "$(YELLOW)Running Docker tests...$(NC)"
	@npm run test:docker
	@npm run test:docker-deps
	@echo "$(GREEN)✅ Docker tests passed!$(NC)"

test-e2e: ## Run end-to-end tests
	@echo "$(YELLOW)Running E2E tests...$(NC)"
	@cd test && node test-e2e-login.js
	@cd test && node test-react-router-issues.js
	@echo "$(GREEN)✅ E2E tests passed!$(NC)"

test-generated: ## Test generated project
	@echo "$(YELLOW)Generating and testing project...$(NC)"
	@rm -rf ../test-project-make 2>/dev/null || true
	@echo "test-project-make\n\ntest_db\ntest_user\ntest_pass\n8000\n3000" | npm start
	@cd ../test-project-make && docker-compose up -d
	@sleep 10
	@curl -f http://localhost:8000/health || (cd ../test-project-make && docker-compose down && exit 1)
	@cd ../test-project-make && docker-compose down
	@rm -rf ../test-project-make
	@echo "$(GREEN)✅ Generated project works!$(NC)"

test: test-quick test-docker ## Run all standard tests

test-all: test test-e2e test-generated ## Run ALL tests including E2E and generation

pre-commit: ## Run all checks before committing
	@echo "$(YELLOW)Running pre-commit checks...$(NC)"
	@make test-quick
	@echo ""
	@echo "$(YELLOW)Checking for TODOs...$(NC)"
	@grep -r "TODO\|FIXME\|XXX" src/ templates/ --exclude-dir=node_modules || echo "$(GREEN)No TODOs found$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking package size...$(NC)"
	@npm pack --dry-run 2>&1 | grep "package size"
	@echo ""
	@echo "$(GREEN)✅ Ready to commit!$(NC)"

clean: ## Clean generated test artifacts
	@echo "$(YELLOW)Cleaning test artifacts...$(NC)"
	@rm -rf ../test-* 2>/dev/null || true
	@rm -rf coverage/ 2>/dev/null || true
	@rm -rf .nyc_output/ 2>/dev/null || true
	@echo "$(GREEN)✅ Cleaned!$(NC)"

ci-status: ## Check CI status for current branch
	@echo "$(YELLOW)Checking CI status...$(NC)"
	@gh pr checks --watch || echo "$(YELLOW)No PR found for current branch$(NC)"

release: ## Prepare for release (run all tests + version check)
	@echo "$(YELLOW)Preparing for release...$(NC)"
	@make test-all
	@echo ""
	@echo "$(YELLOW)Current version:$(NC)"
	@node -p "require('./package.json').version"
	@echo ""
	@echo "$(GREEN)✅ Ready for release! Don't forget to:$(NC)"
	@echo "  1. Update version in package.json"
	@echo "  2. Update CHANGELOG.md"
	@echo "  3. Create git tag"
	@echo "  4. Run: npm publish"

# Development workflow helpers
dev-setup: ## Setup development environment
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	@npm install
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

watch-tests: ## Watch and run tests on file changes
	@echo "$(YELLOW)Watching for changes...$(NC)"
	@npx nodemon --watch src --watch templates --exec "make test-quick"

# Docker helpers
docker-build-test: ## Build and test Docker images locally
	@echo "$(YELLOW)Building Docker images for testing...$(NC)"
	@cd templates/frontend-mui && docker build -t test-mui .
	@cd templates/frontend-tailwind && docker build -t test-tailwind .
	@cd templates/common/backend && docker build -t test-backend .
	@echo "$(GREEN)✅ Docker images built successfully!$(NC)"

# Cypress Visual Testing
cypress-install: ## Install Cypress and dependencies
	@echo "$(YELLOW)Installing Cypress...$(NC)"
	@npm install
	@npx cypress install
	@echo "$(GREEN)✅ Cypress installed!$(NC)"

cypress-open: ## Open Cypress Test Runner (interactive mode)
	@echo "$(YELLOW)Opening Cypress Test Runner...$(NC)"
	@echo "$(BLUE)Make sure your app is running on http://localhost:3000$(NC)"
	@npx cypress open

cypress-run: ## Run Cypress tests in headless mode
	@echo "$(YELLOW)Running Cypress tests...$(NC)"
	@npx cypress run

cypress-mui: ## Test MUI template with Cypress (visual mode)
	@echo "$(YELLOW)Starting MUI template for Cypress testing...$(NC)"
	@make generate-mui
	@cd ../test-cypress-mui && docker-compose up -d
	@echo "$(BLUE)Waiting for services to start...$(NC)"
	@sleep 15
	@echo "$(GREEN)Services started! Opening Cypress...$(NC)"
	@CYPRESS_baseUrl=http://localhost:3000 CYPRESS_env__template=mui npx cypress open
	@echo "$(YELLOW)After testing, run: cd ../test-cypress-mui && docker-compose down$(NC)"

cypress-tailwind: ## Test Tailwind template with Cypress (visual mode)
	@echo "$(YELLOW)Starting Tailwind template for Cypress testing...$(NC)"
	@make generate-tailwind
	@cd ../test-cypress-tailwind && docker-compose up -d
	@echo "$(BLUE)Waiting for services to start...$(NC)"
	@sleep 15
	@echo "$(GREEN)Services started! Opening Cypress...$(NC)"
	@CYPRESS_baseUrl=http://localhost:3000 CYPRESS_env__template=tailwind npx cypress open
	@echo "$(YELLOW)After testing, run: cd ../test-cypress-tailwind && docker-compose down$(NC)"

cypress-both: ## Run Cypress tests for both templates (headless)
	@echo "$(YELLOW)Testing both templates with Cypress...$(NC)"
	@make cypress-test-mui-headless
	@make cypress-test-tailwind-headless
	@echo "$(GREEN)✅ All Cypress tests completed!$(NC)"

cypress-test-mui-headless: ## Test MUI template headless
	@echo "$(YELLOW)Testing MUI template (headless)...$(NC)"
	@make generate-mui
	@cd ../test-cypress-mui && docker-compose up -d
	@sleep 15
	@CYPRESS_baseUrl=http://localhost:3000 CYPRESS_env__template=mui npx cypress run --spec "cypress/e2e/mui/**/*.cy.js"
	@cd ../test-cypress-mui && docker-compose down
	@rm -rf ../test-cypress-mui
	@echo "$(GREEN)✅ MUI tests passed!$(NC)"

cypress-test-tailwind-headless: ## Test Tailwind template headless
	@echo "$(YELLOW)Testing Tailwind template (headless)...$(NC)"
	@make generate-tailwind
	@cd ../test-cypress-tailwind && docker-compose up -d
	@sleep 15
	@CYPRESS_baseUrl=http://localhost:3000 CYPRESS_env__template=tailwind npx cypress run --spec "cypress/e2e/tailwind/**/*.cy.js"
	@cd ../test-cypress-tailwind && docker-compose down
	@rm -rf ../test-cypress-tailwind
	@echo "$(GREEN)✅ Tailwind tests passed!$(NC)"

generate-mui: ## Generate MUI test project
	@echo "$(YELLOW)Generating MUI test project...$(NC)"
	@rm -rf ../test-cypress-mui 2>/dev/null || true
	@echo "test-cypress-mui\n\ntest_db\ntest_user\ntest_pass\n8000\n3000" | npm start || true
	@if [ ! -d "../test-cypress-mui" ]; then \
		echo "$(RED)Failed to generate project with CLI, using manual copy...$(NC)"; \
		mkdir -p ../test-cypress-mui; \
		cp -r templates/frontend-mui ../test-cypress-mui/frontend; \
		cp -r templates/common/backend ../test-cypress-mui/backend; \
		cp templates/common/docker-compose.yml ../test-cypress-mui/; \
		cp templates/common/.env.example ../test-cypress-mui/.env; \
	fi
	@echo "$(GREEN)✅ MUI project generated!$(NC)"

generate-tailwind: ## Generate Tailwind test project
	@echo "$(YELLOW)Generating Tailwind test project...$(NC)"
	@rm -rf ../test-cypress-tailwind 2>/dev/null || true
	@echo "test-cypress-tailwind\n2\ntest_db\ntest_user\ntest_pass\n8000\n3000" | npm start || true
	@if [ ! -d "../test-cypress-tailwind" ]; then \
		echo "$(RED)Failed to generate project with CLI, using manual copy...$(NC)"; \
		mkdir -p ../test-cypress-tailwind; \
		cp -r templates/frontend-tailwind ../test-cypress-tailwind/frontend; \
		cp -r templates/common/backend ../test-cypress-tailwind/backend; \
		cp templates/common/docker-compose.yml ../test-cypress-tailwind/; \
		cp templates/common/.env.example ../test-cypress-tailwind/.env; \
	fi
	@echo "$(GREEN)✅ Tailwind project generated!$(NC)"

cypress-watch: ## Watch Cypress tests with live reload
	@echo "$(YELLOW)Starting Cypress in watch mode...$(NC)"
	@npx cypress open --e2e --browser chrome

cypress-record: ## Record Cypress test videos
	@echo "$(YELLOW)Recording Cypress test videos...$(NC)"
	@npx cypress run --record --key $(CYPRESS_RECORD_KEY)

# GitHub integration
gh-sync: ## Sync with GitHub (fetch + pull + prune)
	@echo "$(YELLOW)Syncing with GitHub...$(NC)"
	@git fetch --all --prune
	@git pull origin main
	@echo "$(GREEN)✅ Synced with GitHub!$(NC)"

# Parallel execution for speed
test-parallel: ## Run tests in parallel (faster)
	@echo "$(YELLOW)Running tests in parallel...$(NC)"
	@npx concurrently -k -s first \
		"npm:test:package" \
		"npm:test:structure" \
		"npm:lint" \
		"npm:format:check"
	@echo "$(GREEN)✅ All parallel tests passed!$(NC)"

# Kedro Pipeline Integration
kedro-install: ## Install Kedro pipeline dependencies
	@echo "$(YELLOW)Installing Kedro dependencies...$(NC)"
	@cd kedro-pipeline && pip install -r requirements.txt
	@echo "$(GREEN)✅ Kedro dependencies installed!$(NC)"

kedro-test: ## Run Kedro validation pipeline
	@echo "$(YELLOW)Running Kedro validation pipeline...$(NC)"
	@npm run test:kedro
	@echo "$(GREEN)✅ Kedro pipeline completed!$(NC)"

kedro-quick: ## Run quick Kedro pipeline (no Docker)
	@echo "$(YELLOW)Running quick Kedro pipeline...$(NC)"
	@npm run test:kedro:quick
	@echo "$(GREEN)✅ Quick pipeline completed!$(NC)"

kedro-release: ## Run Kedro release pipeline
	@echo "$(YELLOW)Running Kedro release pipeline...$(NC)"
	@npm run test:kedro:release
	@echo "$(GREEN)✅ Release pipeline completed!$(NC)"

kedro-viz: ## Launch Kedro visualization dashboard
	@echo "$(YELLOW)Starting Kedro Viz...$(NC)"
	@cd kedro-pipeline && kedro viz run
	
kedro-clean: ## Clean Kedro pipeline outputs
	@echo "$(YELLOW)Cleaning Kedro outputs...$(NC)"
	@rm -rf kedro-pipeline/data/* 2>/dev/null || true
	@rm -rf kedro-pipeline/logs/* 2>/dev/null || true
	@echo "$(GREEN)✅ Kedro outputs cleaned!$(NC)"