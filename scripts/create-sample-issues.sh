#!/bin/bash

# Script to create sample User Stories and Tasks in GitHub Issues

echo "📝 Creating sample User Stories and Tasks..."

# User Story 1: PostgreSQL/MySQL Support
gh issue create \
  --title "US: As a developer, I want to choose between PostgreSQL and MySQL during setup" \
  --body "## User Story
As a **developer**,  
I want **to choose between PostgreSQL and MySQL during project generation**,  
So that **I can use my preferred database system**.

## Acceptance Criteria
- [ ] CLI prompts for database choice (PostgreSQL/MySQL)
- [ ] Generated docker-compose uses selected database
- [ ] Backend ORM configured for selected database
- [ ] Migration scripts work with both databases
- [ ] Connection strings properly configured
- [ ] Tests pass with both database options

## Technical Notes
- Need to create separate Alembic configs
- Update SQLAlchemy connection strings
- Modify docker-compose templates
- Test with both database engines

## Tasks
- [ ] Add database selection to CLI prompts
- [ ] Create MySQL Docker template
- [ ] Update backend database configuration
- [ ] Create database-specific migration templates
- [ ] Update connection string generation
- [ ] Add tests for both database types

## Story Points
8

## Priority
High

## Sprint
v1.1.0" \
  --label "user-story,backend,docker,priority: high,sp: 8"

# User Story 2: TypeScript Frontend
gh issue create \
  --title "US: As a developer, I want TypeScript option for frontend templates" \
  --body "## User Story
As a **frontend developer**,  
I want **to use TypeScript in my React application**,  
So that **I have better type safety and IDE support**.

## Acceptance Criteria
- [ ] CLI asks if user wants TypeScript
- [ ] TypeScript configured for selected UI library
- [ ] All components properly typed
- [ ] tsconfig.json properly configured
- [ ] Build process handles TypeScript
- [ ] No TypeScript errors in generated code

## Technical Notes
- Need separate templates or conversion script
- Update webpack/build configuration
- Add type definitions for API responses
- Consider using .tsx extensions

## Tasks
- [ ] Add TypeScript prompt to CLI
- [ ] Create TypeScript React templates
- [ ] Add proper type definitions
- [ ] Configure build tools for TS
- [ ] Update documentation
- [ ] Test TypeScript compilation

## Story Points
5

## Priority
Medium

## Sprint
v1.2.0" \
  --label "user-story,frontend,enhancement,priority: medium,sp: 5"

# Task 1: Database selection CLI
gh issue create \
  --title "TASK: Add database selection prompt to CLI" \
  --body "## Task Description
Add a new prompt to the CLI that allows users to select their preferred database (PostgreSQL or MySQL).

## Parent User Story
Related to PostgreSQL/MySQL support US

## Definition of Done
- [ ] Prompt added to inquirer questions
- [ ] Validation for database selection
- [ ] Selected database passed to template generation
- [ ] Tests written for new prompt
- [ ] Documentation updated

## Technical Details
- Add to src/index.js inquirer prompts
- Store selection in config object
- Pass to template replacement logic

## Estimated Time
4 hours

## Blocked By
None" \
  --label "task,cli,status: ready"

# Bug Report Example
gh issue create \
  --title "BUG: Docker Compose fails on M1 Macs with platform error" \
  --body "## Bug Description
Docker Compose fails to start on M1 Macs with platform compatibility error

## To Reproduce
Steps to reproduce the behavior:
1. Run 'stackwizard' on M1 Mac
2. Generate project with default options
3. Run 'docker-compose up'
4. See platform error

## Expected Behavior
Docker containers should start successfully on ARM64 architecture

## Actual Behavior
Error: no matching manifest for linux/arm64/v8

## Environment
- OS: macOS 14.0 (M1)
- Node version: 18.17.0
- StackWizard version: 1.0.16
- Docker version: 24.0.2

## Possible Solution
Add platform specification to docker-compose.yml" \
  --label "bug,docker,priority: high"

# Feature Request Example
gh issue create \
  --title "FEATURE: Add GraphQL API option alongside REST" \
  --body "## Feature Description
Option to generate GraphQL API in addition to or instead of REST API

## Problem Statement
Some developers prefer GraphQL for its flexibility and efficiency in data fetching

## Proposed Solution
- Add prompt for API style (REST/GraphQL/Both)
- Generate GraphQL schema from models
- Include GraphQL playground
- Generate resolvers and types

## User Impact
Developers who prefer GraphQL can use StackWizard

## Implementation Considerations
- [x] Backend changes required
- [ ] Frontend changes required
- [ ] Database changes required
- [ ] Breaking changes
- [x] Documentation needed

## Additional Context
GraphQL is becoming increasingly popular for modern APIs" \
  --label "enhancement,backend,needs-discussion"

echo "✅ Sample issues created! Check them at: https://github.com/rafeekpro/stackwizard/issues"