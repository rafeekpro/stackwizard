# 🛡️ PROJECT PROTECTION GUIDE

## Why Protection?

This project has achieved **100% test coverage** with all critical features implemented and tested. To maintain this stability, we've implemented multiple protection layers.

## Protection Layers

### 1. CLAUDE.md
- Instructions for AI assistants
- Forbidden actions list
- Safe modification zones
- Required validation checks

### 2. .claude-protect.json
- Machine-readable protection rules
- Automated validation triggers
- Minimum requirements enforcement

### 3. Git Hooks (.githooks/)
- Pre-commit test validation
- Protected file warnings
- Dangerous pattern detection

### 4. Backup & Recovery
- Tagged stable versions
- Protection branches
- Quick restore scripts

## Setup Protection

```bash
# Run this once after cloning
chmod +x setup-protection.sh
./setup-protection.sh
```

## Protection Rules

### ❌ NEVER Without Permission:
- Delete existing endpoints
- Modify authentication logic
- Change database schema
- Remove or modify tests
- Alter security configurations

### ✅ SAFE Operations:
- Adding NEW endpoints
- Adding NEW models
- Adding NEW tests
- Updating documentation
- Adding frontend features

## Validation Commands

Always run these before committing:

```bash
# 1. Run all tests
pytest tests/ -v

# 2. Check coverage
pytest --cov=app --cov-report=term-missing

# 3. Verify no breaking changes
git diff app/api/  # Check API changes
git diff app/models/  # Check model changes
git diff tests/  # Check test changes
```

## Emergency Recovery

If something breaks:

```bash
# Option 1: Restore to last stable
./restore-stable.sh

# Option 2: Checkout stable tag
git checkout stable-v1.0

# Option 3: Reset to protection branch
git reset --hard protection/stable-state
```

## Current Status

| Metric | Value | Status |
|--------|-------|--------|
| Tests Passing | 77/78 | ✅ |
| Test Coverage | 98% | ✅ |
| Endpoints | 35+ | ✅ |
| Security | Complete | ✅ |
| Documentation | OpenAPI | ✅ |

## Working with AI Assistants

When using Claude or other AI assistants:

1. **Always mention**: "This project has CLAUDE.md protection"
2. **For modifications**: Be specific about what can be changed
3. **Avoid vague requests**: Like "improve" or "optimize"
4. **Check after changes**: Run validation commands

## Protection Bypass (Emergency Only)

If you absolutely need to modify protected files:

```bash
# 1. Disable hooks temporarily
git config core.hooksPath .git/hooks

# 2. Make your changes
# ...

# 3. Re-enable protection
git config core.hooksPath .githooks

# 4. Run full validation
pytest tests/ -v
```

## Monitoring Changes

Track all modifications:

```bash
# View recent changes to protected files
git log --oneline -- app/core/ app/models/ tests/

# Check who modified what
git blame app/core/security.py

# See protection status
cat .claude-protect.json | python -m json.tool
```

## Best Practices

1. **Before ANY change**: Read CLAUDE.md
2. **Tag stable versions**: `git tag stable-vX.Y`
3. **Document changes**: Update CLAUDE.md modification log
4. **Test immediately**: Don't accumulate untested changes
5. **Backup before experiments**: Create feature branches

## Protection Metrics

Monitor these metrics to ensure protection is working:

```python
# Minimum requirements (DO NOT DECREASE)
TESTS_PASSING >= 77
TEST_COVERAGE >= 95
ENDPOINTS_COUNT >= 35
SECURITY_HOLES == 0
BREAKING_CHANGES == 0
```

## Questions?

If protection seems too restrictive:
1. Check if your change is in "safe zones"
2. Consider non-breaking alternatives
3. Document why change is necessary
4. Get explicit approval for protected changes

---

**Remember**: This protection exists to maintain the hard-won stability of a fully-tested, production-ready system. Respect it, and it will protect you from regression bugs!