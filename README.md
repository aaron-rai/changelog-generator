# PR Changelog Generator

A GitHub Action that automatically generates organized changelogs from Pull Request descriptions.

## Features

- Extracts changelog sections from PR descriptions
- Multiple organizational formats:
  - Separate changelogs per version and type (client-facing vs. internal)
  - Unified changelogs per version (all changes in one file per version)
  - Single changelog file (all versions and changes in one file)
- Includes date in version numbers (e.g., "v1.2.3 (2023-05-15)")
- Associates changes with PR numbers and related issues
- Categorizes changes (Added, Changed, Fixed, etc.)
- Automatically commits generated changelog files

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
| `single_file` | Use a single file for all versions | `false` |
| `single_filename` | Filename to use for single file mode | `CHANGELOG.md` |
| `include_date_in_version` | Include date in version headers | `true` |
| `date_format` | Format for dates | `%Y-%m-%d` |
| `commit_changes` | Whether to commit changes to the repo | `true` |
| `commit_message` | Commit message for changelog updates | `Update changelog for PR #{pr_number}` |

## Output Formats

The action supports three different changelog formats:

### 1. Separate Changelogs (Default)

When `unified_changelog` and `single_file` are both set to `false`, it creates two types of changelog files per version:

1. `${changelog_dir}/${client_subdirectory}/${version}.md` - Client-facing changes
2. `${changelog_dir}/${internal_subdirectory}/${version}.md` - Internal technical changes

### 2. Unified Changelog Per Version

When `unified_changelog` is set to `true` and `single_file` is set to `false`, it creates a single changelog file per version:

`${changelog_dir}/${version}.md`

### 3. Single Changelog File

When `single_file` is set to `true`, it creates one changelog file for all versions:

`${changelog_dir}/${single_filename}`

## Example Workflow File

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
          include_date_in_version: true
          date_format: "%Y-%m-%d"
```

## Example Output Formats

### Separate Changelogs (Default)

**Client Changelog (`changelog/client/v1.2.0.md`):**
```markdown
# v1.2.0 (2023-05-15) Client Changelog

## Added

- Login and registration forms with email verification
- Password reset functionality

## Fixed

- Account settings page not saving changes properly
```

**Internal Changelog (`changelog/internal/v1.2.0.md`):**
```markdown
# v1.2.0 (2023-05-15) Internal Changelog

## PR #123: Add user authentication features

**Related Issues:** #100, #115, PROJ-456

## Added

- Authentication service with JWT implementation
- User repository module

## Fixed

- Race condition in concurrent user updates
```

### Unified Changelog Per Version (`changelog/v1.2.0.md`)

```markdown
# v1.2.0 (2023-05-15) Changelog

## Added

- Login and registration forms with email verification
- Password reset functionality
- Authentication service with JWT implementation
- User repository module

## Fixed

- Account settings page not saving changes properly
- Race condition in concurrent user updates
```

### Single Changelog File (`changelog/CHANGELOG.md`)

```markdown
# Changelog

## v1.2.0 (2023-05-15)

### Added

- Login and registration forms with email verification
- Password reset functionality
- Authentication service with JWT implementation
- User repository module

### Fixed

- Account settings page not saving changes properly
- Race condition in concurrent user updates

## v1.1.0 (2023-04-10)

### Added

- New dashboard widgets
...
```
