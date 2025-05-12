# PR Changelog Generator

A GitHub Action that automatically generates organized changelogs from Pull Request descriptions.

## Features

- Extracts changelog sections from PR descriptions
- Organizes changes by version and type (client-facing vs internal)
- Associates changes with PR numbers and related issues
- Categorizes changes (Added, Changed, Fixed, etc.)
- Automatically commits generated changelog files

## How It Works

This action:

1. Triggers when a PR is merged to your main branch
2. Extracts changelog information from the PR description
3. Organizes entries by version and change type
4. Generates or updates markdown files in your changelog directory
5. Optionally commits the changes back to your repository

## Setup

### Step 1: Create PR Template

Ensure your PR template includes structured sections for changes:

```markdown
## Summary

...

## Change Log

### Client-Facing Changes

<!-- Use plain, non-technical language for stakeholders or clients -->
- **Added**: [New user-visible feature or enhancement]
- **Changed**: [Updated behavior the client might notice]
- **Removed**: [Removed features or functionality]
- **Fixed**: [Bug fixes impacting users]

### Internal Changes

<!-- Use technical detail for devs or contributors -->
- **Added**: [New modules, utilities, or functions]
- **Changed**: [Refactors, optimizations, or internal behavior changes]
- **Deprecated**: [Marked features/code for future removal]
- **Removed**: [Deleted internal code or legacy features]
- **Fixed**: [Internal bug or logic fix]
- **Security**: [Patches to vulnerabilities or hardening measures]

## Target Version

<!-- Example: v1.3.0 -->
[Insert target release version here]
```

### Step 2: Add Workflow File

Create a workflow file in your repository at `.github/workflows/generate-changelog.yml`:

```yaml
name: Generate Changelog

permissions:
  contents: write
  pull-requests: read

on:
  pull_request:
    types: [closed]

jobs:
  generate-changelog:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      # Use the changelog generator action
      - name: Generate Changelog
        uses: aaron-rai/changelog-generator@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          pr_number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
```

## Configuration Options

| Input | Description | Default |
|-------|-------------|---------|
| `token` | GitHub token | `${{ github.token }}` |
| `pr_number` | Pull request number | Required |
| `repo` | Repository name (e.g. owner/repo) | `${{ github.repository }}` |
| `changelog_dir` | Directory to store changelog files | `changelog` |
| `client_subdirectory` | Subdirectory for client-facing changelogs | `client` |
| `internal_subdirectory` | Subdirectory for internal changelogs | `internal` |
| `unified_changelog` | Use a single changelog instead of separate types | `false` |
| `unified_format` | Format to use for unified changelog (`client` or `internal`) | `client` |
| `commit_changes` | Whether to commit changes to the repo | `true` |
| `commit_message` | Commit message for changelog updates | `Update changelog for PR #{pr_number}` |

## Output Format

The action generates changelog files in one of two ways:

### Option 1: Separate Changelogs (Default)

When `unified_changelog` is set to `false`, it creates two types of changelog files:

1. `${changelog_dir}/${client_subdirectory}/${version}.md` - Client-facing changes
2. `${changelog_dir}/${internal_subdirectory}/${version}.md` - Internal technical changes

Example client-facing output:

```markdown
# v1.2.0

## 2023-05-15

### Added

- Login and registration forms with email verification
- Password reset functionality

### Fixed

- Account settings page not saving changes properly
```

Example internal output:

```markdown
# v1.2.0 Internal Changelog

## PR #123: Add user authentication features (2023-05-15)

**Related Issues:** #100, #115, PROJ-456

### Added

- Authentication service with JWT implementation
- User repository module

### Fixed

- Race condition in concurrent user updates
```

### Option 2: Unified Changelog

When `unified_changelog` is set to `true`, it creates a single changelog file:

`${changelog_dir}/${version}.md`

The format depends on the `unified_format` setting:

- With `unified_format: client` (default), it uses the simpler client-facing format
- With `unified_format: internal`, it uses the more detailed format with PR information

## Development

### Local Testing

To test this action locally:

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set the required environment variables
4. Run the test script: `python test_changelog_locally.py`

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.