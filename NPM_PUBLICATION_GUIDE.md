# 📦 NPM Publication Guide for StackWizard

This guide provides step-by-step instructions for publishing the StackWizard CLI to npm.

## 📋 Pre-Publication Checklist

Before publishing, ensure you have:
- [ ] An npm account (create one at https://www.npmjs.com/signup)
- [ ] Node.js 16+ and npm 7+ installed
- [ ] All tests passing
- [ ] Updated version number in package.json
- [x] ✅ Package name updated to `@rafeekpro/stackwizard`

## 🔧 Preparation Steps

### 1. ✅ Package Name Updated

The package name has been set to `@rafeekpro/stackwizard` in package.json.
All placeholders have been replaced with your NPM username: `rafeekpro`

### 2. Verify Package Configuration

```bash
# Check package.json is valid
npm run lint

# View what will be published
npm pack --dry-run

# Check package size
npm pack --dry-run 2>&1 | grep "npm notice package size"
```

## 🚀 Publication Commands

### Step 1: Login to npm

```bash
# Login to npm registry
npm login

# Verify you're logged in
npm whoami
```

### Step 2: Test Locally

```bash
# Create a global link for testing
npm link

# Test the CLI command
stackwizard --version

# Create a test project
cd /tmp
stackwizard test-project

# Unlink after testing
npm unlink -g @rafeekpro/stackwizard
```

### Step 3: Publish to npm

```bash
# For scoped packages (@username/package), use --access public
npm publish --access public

# The command will:
# 1. Run prepublishOnly scripts (format check & lint)
# 2. Pack the package
# 3. Upload to npm registry
```

### Step 4: Verify Publication

```bash
# Check if package is available
npm view @rafeekpro/stackwizard

# Test installation from npm
npx @rafeekpro/stackwizard --version
```

## 📝 Complete Command Sequence

Here's the complete sequence for publishing:

```bash
# 1. Ensure you're on the correct branch
git checkout feature/npm-publication

# 2. ✅ Username already updated to rafeekpro
# (Skip this step - already done)

# 4. Login to npm
npm login

# 5. Test the package locally
npm link
cd /tmp && stackwizard test-local-project
cd - && npm unlink -g @rafeekpro/stackwizard

# 6. Publish to npm (first time publication)
npm publish --access public

# 7. Verify publication
npm view @rafeekpro/stackwizard
npx @rafeekpro/stackwizard --version
```

## 🔄 Updating the Package

For future updates:

```bash
# 1. Update version in package.json
npm version patch  # or minor/major

# 2. Commit version bump
git add package.json package-lock.json
git commit -m "chore: Bump version to $(node -p "require('./package.json').version")"

# 3. Publish update
npm publish

# 4. Create git tag
git tag v$(node -p "require('./package.json').version")
git push origin --tags
```

## 📊 Post-Publication

After successful publication:

1. **Check npm page**: Visit `https://www.npmjs.com/package/@rafeekpro/stackwizard`
2. **Update GitHub**: Push changes and create a release
3. **Test installation**: `npx @rafeekpro/stackwizard`
4. **Monitor downloads**: Check npm stats at `https://npm-stat.com/`

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. "402 Payment Required"
- **Cause**: Trying to publish a scoped package without `--access public`
- **Solution**: Add `--access public` flag to publish command

#### 2. "403 Forbidden"
- **Cause**: Package name already taken or not logged in
- **Solution**: Check name availability or run `npm login`

#### 3. "E404 Not Found"
- **Cause**: Scope doesn't match npm username
- **Solution**: Ensure package name matches `@your-npm-username/package-name`

#### 4. Large Package Size Warning
- **Cause**: Including unnecessary files
- **Solution**: Check `.npmignore` and `files` field in package.json

## 🎉 Success Checklist

After publication, users can:
- [ ] Run `npx @rafeekpro/stackwizard` without installation
- [ ] Install globally with `npm i -g @rafeekpro/stackwizard`
- [ ] View package on npmjs.com
- [ ] See proper README on npm page
- [ ] Use all CLI features

## 📚 Additional Resources

- [npm Documentation](https://docs.npmjs.com/)
- [Publishing Scoped Packages](https://docs.npmjs.com/creating-and-publishing-scoped-public-packages)
- [npm Best Practices](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)
- [Semantic Versioning](https://semver.org/)

---

**Note**: All placeholders have been updated to use your NPM username: `rafeekpro`