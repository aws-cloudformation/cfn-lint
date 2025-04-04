---
description: Amazon Q Rules Location
globs: .amazonq/rules/**/*.md
---
# Amazon Q Rules Location

Rules for placing and organizing Amazon Q markdown files in the repository.

<rule>
name: amazonq_rules_location
description: Standards for placing Amazon Q markdown files in the correct directory
filters:
  # Match any .md files
  - type: file_extension
    pattern: "\.md$"
  # Match file creation events
  - type: event
    pattern: "file_create"

actions:
  - type: reject
    conditions:
      - pattern: "^(?!\\.amazonq\\/rules\\/.*\\.md$)"
        message: "Amazon Q markdown files must be placed in the .amazonq/rules directory"

  - type: suggest
    message: |
      When creating Amazon Q files:

      1. Always place markdown files in PROJECT_ROOT/.amazonq/rules/:
         ```
         .amazonq/rules/
         ├── your-rule.md
         ├── another-rule.md [[1]](https://docs.aws.amazon.com/amazonq/latest/api-reference/API_Rule.html)
         └── ...
         ```

      2. Follow the naming convention:
         - Use kebab-case for filenames
         - Always use .md extension
         - Make names descriptive of the file's purpose

      3. Directory structure:
         ```
         PROJECT_ROOT/
         ├── .amazonq/
         │   └── rules/
         │       ├── your-rule.md
         │       └── ...
         └── ...
         ```

      4. Never place markdown files:
         - In the project root
         - In subdirectories outside .amazonq/rules
         - In any other location

examples:
  - input: |
      # Bad: File in wrong location
      rules/my-rule.md
      my-rule.md
      .rules/my-rule.md

      # Good: File in correct location
      .amazonq/rules/my-rule.md
    output: "Correctly placed Amazon Q markdown file"

metadata:
  priority: high
  version: 1.0
</rule>
