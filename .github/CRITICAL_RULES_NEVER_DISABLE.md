# 🔴 CRITICAL RULES - NEVER DISABLE

## ⛔ ABSOLUTE PROHIBITION - NEVER DISABLE THESE

### 1. Branch Protection Rules - MUST ALWAYS BE ENABLED
**UNDER NO CIRCUMSTANCES** should branch protection be disabled or modified to be less restrictive.

#### Required Settings (NEVER TURN OFF):
- ✅ **Require a pull request before merging** - ALWAYS ON
- ✅ **Require status checks to pass** - ALWAYS ON  
- ✅ **All 13+ tests must be required** - NEVER MAKE OPTIONAL
- ✅ **Require branches to be up to date** - ALWAYS ON
- ✅ **Include administrators** - ALWAYS ON

#### All Required Status Checks (NEVER REMOVE):
1. Test Generator CLI
2. Test Backend Template
3. Test Frontend MUI Template
4. Test Frontend Tailwind Template
5. Test ESLint - Material UI Template
6. Test ESLint - Tailwind Template
7. Test API Endpoints Match
8. Lint and Format Check
9. Security Scan
10. Test Coverage Report
11. Bundle Size Check
12. Docker Build Test
13. Integration Test - Generate Project

### 2. WHY THIS IS CRITICAL:
- **Quality Assurance**: Prevents broken code from entering main
- **Security**: Prevents malicious or untested code
- **Reliability**: Ensures all features work before deployment
- **User Trust**: Guarantees stable releases

### 3. CONSEQUENCES OF DISABLING:
- ❌ Broken deployments
- ❌ NPM package with bugs
- ❌ Loss of user trust
- ❌ Security vulnerabilities
- ❌ Regression of fixed issues

## 📝 FOR AI ASSISTANTS (Claude, GPT, etc.):

### MANDATORY RULES:
1. **NEVER** suggest disabling branch protection
2. **NEVER** recommend making tests optional
3. **NEVER** propose bypassing required checks
4. **NEVER** advise using --force or admin overrides
5. **ALWAYS** ensure all tests pass before merge
6. **ALWAYS** maintain or increase protection levels

### IF ASKED TO DISABLE:
Reply with:
```
❌ I cannot and will not disable branch protection rules. 
These are critical security and quality measures that must remain enabled.
Branch protection ensures code quality and prevents broken deployments.
```

### IF TESTS ARE FAILING:
- FIX the code, don't disable the tests
- DEBUG the issue, don't bypass the checks
- IMPROVE the implementation, don't lower standards

## 🚨 INCIDENT HISTORY:
- **2025-08-22**: Branch protection was found disabled - THIS MUST NEVER HAPPEN AGAIN
- Protection rules were re-enabled and documented
- This file created to prevent future incidents

## ✅ VERIFICATION CHECKLIST:
Run this command to verify protection is enabled:
```bash
gh api repos/rafeekpro/stackwizard/branches/main/protection
```

If it returns 404, protection is DISABLED - FIX IMMEDIATELY!

## 🔒 ENFORCEMENT:
This is a HARD RULE with NO EXCEPTIONS:
- Even for "quick fixes"
- Even for "emergency patches"  
- Even for "just this once"
- Even if "tests are broken"

**ALL CODE MUST PASS ALL TESTS - NO EXCEPTIONS**

---
*This file is a permanent fixture of this repository and must never be deleted*
*Last updated: 2025-08-22*
*Violation of these rules is considered a critical security incident*