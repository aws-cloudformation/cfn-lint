---
description: Guidelines for creating cfn-lint schema extensions
globs: src/cfnlint/data/schemas/extensions/**/*.json
---
# Creating Schema Extensions for cfn-lint

<rule>
name: schema_extension_creation
description: Guidelines for creating and maintaining schema extensions for cfn-lint
filters:
  - type: file_extension
    pattern: "\.json$"
  - type: path
    pattern: "src/cfnlint/data/schemas/extensions/"

actions:
  - type: suggest
    message: |
      When creating schema extensions for cfn-lint:

      1. **Follow JSON Schema structure**:
         - Use standard JSON Schema with `if/then` conditional validation
         - Properly validate property types in the `if` clause
         - Use `false` as a schema value to disallow properties
         - Use descriptive file names that indicate what aspect is being validated

      2. **Base extensions on AWS documentation**:
         - Read the official AWS CloudFormation documentation thoroughly
         - Focus on property constraints not covered by the base schema
         - Validate relationships between properties (e.g., when X is Y, Z must be A)
         - Document the source of the validation rule with comments or commit messages

      3. **Organize extensions properly**:
         - Place extensions in the correct resource type directory
         - Create new directories for resource types if needed
         - Follow the existing naming conventions

      4. **Test your extensions**:
         - Create test cases that should pass and fail
         - Ensure the error messages are clear and helpful

examples:
  - input: |
      {
        "if": {
          "properties": {
            "TargetType": {
              "enum": ["lambda"]
            }
          }
        },
        "then": {
          "properties": {
            "Protocol": {
              "enum": ["HTTP", "HTTPS"]
            }
          }
        }
      }
    output: |
      {
        "if": {
          "properties": {
            "TargetType": {
              "enum": ["lambda"]
            },
            "Protocol": {
              "type": "string"
            }
          },
          "required": ["TargetType"]
        },
        "then": {
          "properties": {
            "Protocol": false,
            "Port": false,
            "HealthCheckPath": false
          }
        }
      }

metadata:
  priority: high
  version: 1.0
</rule>
