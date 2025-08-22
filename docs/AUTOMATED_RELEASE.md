# 🚀 Automated Release Pipeline

This project uses GitHub Actions for automated NPM publishing and version management.

## 📦 Automatic NPM Publishing

The package is **automatically published to NPM** when:
1. A PR is merged to `main` branch
2. The `package.json` version is different from the published NPM version

### How it works:
1. **Check Version**: Compares package.json version with NPM registry
2. **Run Tests**: Ensures all tests pass before publishing
3. **Publish**: Publishes to NPM with public access
4. **Create Release**: Creates a GitHub release with the new version tag

## 🔄 Version Bump Workflow

To bump the version, you have two options:

### Option 1: Manual Trigger (Recommended)
1. Go to [Actions → Version Bump](https://github.com/rafeekpro/stackwizard/actions/workflows/version-bump.yml)
2. Click "Run workflow"
3. Select version type:
   - `patch`: 1.0.5 → 1.0.6 (bug fixes)
   - `minor`: 1.0.5 → 1.1.0 (new features)
   - `major`: 1.0.5 → 2.0.0 (breaking changes)
4. The workflow will:
   - Create a new release branch
   - Bump the version
   - Create a PR
5. Once PR is merged, NPM publish will trigger automatically

### Option 2: Manual Process
1. Create a new branch: `git checkout -b release/vX.X.X`
2. Bump version: `npm version patch/minor/major`
3. Push and create PR
4. Merge PR → Auto-publish triggers

## 🔑 Required Secrets

The following secrets must be configured in GitHub repository settings:

### NPM_TOKEN
1. Log in to npmjs.com
2. Go to Access Tokens → Generate New Token
3. Select "Automation" type
4. Copy the token
5. Add to GitHub: Settings → Secrets → Actions → New repository secret
   - Name: `NPM_TOKEN`
   - Value: Your NPM token

## 📋 Release Checklist

Before releasing:
- [ ] All tests pass
- [ ] ESLint has no errors
- [ ] Documentation is updated
- [ ] Breaking changes are documented
- [ ] Version bump type is appropriate

## 🔍 Monitoring

### Check Publishing Status
- [GitHub Actions](https://github.com/rafeekpro/stackwizard/actions/workflows/npm-publish.yml)
- [NPM Package Page](https://www.npmjs.com/package/@rafeekpro/stackwizard)
- [GitHub Releases](https://github.com/rafeekpro/stackwizard/releases)

### Troubleshooting

**Publishing Failed?**
1. Check GitHub Actions logs
2. Verify NPM_TOKEN is set correctly
3. Ensure version doesn't already exist on NPM
4. Check npm audit for vulnerabilities

**Version Already Exists?**
- NPM doesn't allow republishing the same version
- Bump to next version and try again

## 📊 Current Status

- **Latest NPM Version**: Check [npmjs.com](https://www.npmjs.com/package/@rafeekpro/stackwizard)
- **Latest GitHub Release**: Check [Releases](https://github.com/rafeekpro/stackwizard/releases)
- **CI Status**: Check [Actions](https://github.com/rafeekpro/stackwizard/actions)

## 🤖 Automation Benefits

1. **No Manual Publishing**: Reduces human error
2. **Consistent Releases**: Same process every time
3. **Automatic Tagging**: Git tags created automatically
4. **Release Notes**: GitHub releases created automatically
5. **Version Checking**: Prevents duplicate publishes
6. **Quality Gates**: Tests must pass before publishing

---

*This automated pipeline ensures reliable, consistent releases with minimal manual intervention.*