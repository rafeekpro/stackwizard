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