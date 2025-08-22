# 📝 CRITICAL RULE: Always Update CHANGELOG.md

## ⚠️ MANDATORY: Update Documentation with Every Change

### Required Updates for EVERY Pull Request:

1. **CHANGELOG.md** - MUST be updated with:
   - All bug fixes
   - New features  
   - Breaking changes
   - Improvements
   - Documentation changes
   
2. **Version Bumping** - When releasing:
   - Update version in `package.json`
   - Move "Unreleased" items to new version section in CHANGELOG
   - Follow semantic versioning

3. **Documentation** - Update when needed:
   - README.md for user-facing changes
   - API documentation for endpoint changes
   - Wiki pages for major features
   - Code comments for complex logic

### CHANGELOG Format:

```markdown
## [Unreleased]

### 🐛 Bug Fixes
- **Component**: Description of fix

### ✨ Improvements  
- **Feature**: What was improved

### 📚 Documentation
- **Doc Type**: What was documented
```

### Version Categories:
- 🎉 **New Features**: New functionality added
- 🐛 **Bug Fixes**: Issues resolved
- ✨ **Improvements**: Enhancements to existing features
- 📚 **Documentation**: Documentation updates
- 🔧 **Maintenance**: Internal changes, refactoring
- ⚠️ **Breaking Changes**: Changes requiring user action
- 🔒 **Security**: Security-related updates

## 🚨 NO EXCEPTIONS

**Every PR MUST include:**
1. Updated CHANGELOG.md in "Unreleased" section
2. Clear, descriptive entries
3. Proper categorization
4. User impact description

## 📋 PR Checklist:
- [ ] CHANGELOG.md updated
- [ ] Version bumped (if release)
- [ ] Documentation updated (if needed)
- [ ] Tests added/updated
- [ ] CI passes

## 🔴 ENFORCEMENT

PRs without CHANGELOG updates will be:
1. Automatically flagged
2. Blocked from merging
3. Returned for revision

---

*This rule ensures complete project history and helps users understand changes.*