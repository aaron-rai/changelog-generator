# Changelog Generator

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

## How It Works

This action:

1. Triggers when a PR is merged to your main branch
2. Extracts changelog information from the PR description
3. Organizes entries by version and change type
4. Generates or updates markdown files in your changelog directory
5. Optionally commits the changes back to your repository

## Setup

### Step 1: Create PR Template

Create a PR template that includes the following structured sections:

```markdown
## Summary

[Your PR summary here]

---

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

---

## Target Version

v1.0.0

---

## Related Issues

<!-- Link related issues or tickets -->
#123
JIRA-456
```
> [!CAUTION]
> The PR template **must** include the sections "Client-Facing Changes", "Internal Changes", and "Target Version" for the changelog generator to work properly.

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
          # Required parameters
          token: ${{ secrets.GITHUB_TOKEN }}
          pr_number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          
          # Optional parameters with their default values
          changelog_dir: "changelog"
          client_subdirectory: "client"
          internal_subdirectory: "internal"
          unified_changelog: "false"
          unified_format: "client"
          single_file: "false"
          single_filename: "CHANGELOG.md"
          include_date_in_version: "true"
          date_format: "%Y-%m-%d"
          commit_changes: "true"
          commit_message: "Update changelog for PR #{pr_number}"
```

- For more examples of this workflow in use, refer to the [examples.md](docs/examples.md).

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

## Example Output Formats

### Separate Changelogs (Default)

**Client Changelog (`changelog/client/v1.2.0.md`):**
```markdown
# v1.2.0 (2023-05-15)

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

## Development

### Local Testing

To test this action locally:

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set the required environment variables
4. Run the test script: `python test_changelog.py`

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
