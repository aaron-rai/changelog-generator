## Workflow Examples

### Complete Example with All Parameters

This example shows all available parameters with their default values:

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

### Example: Single Changelog File

This example configures the action to generate a single changelog file for all versions:

```yaml
name: Generate Single Changelog File

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
      
      - name: Generate Changelog
        uses: aaron-rai/changelog-generator@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          pr_number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          single_file: "true"
          single_filename: "CHANGELOG.md"
```

### Example: Unified Changelog Per Version

This example configures the action to generate a single file per version that contains both client-facing and internal changes:

```yaml
name: Generate Unified Changelog

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
      
      - name: Generate Changelog
        uses: aaron-rai/changelog-generator@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          pr_number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          unified_changelog: "true"
          unified_format: "client"
```

### Example: Custom Date Format

This example uses a custom date format for the changelog entries:

```yaml
name: Generate Changelog with Custom Date Format

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
      
      - name: Generate Changelog
        uses: aaron-rai/changelog-generator@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          pr_number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          include_date_in_version: "true"
          date_format: "%B %d, %Y"  # Example: "May 15, 2023"
```

### Example: No Date in Version

This example disables adding the date to the version number:

```yaml
name: Generate Changelog Without Date in Version

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
      
      - name: Generate Changelog
        uses: aaron-rai/changelog-generator@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          pr_number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          include_date_in_version: "false"
```
