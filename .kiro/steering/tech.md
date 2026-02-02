# Technology Stack

## Language & Runtime

- **Python 3.9-3.13** - Core language
- **Type hints** - Use throughout codebase

## Core Dependencies

- **boto3** - AWS SDK for schema updates
- **jsonschema** - Base for custom validator
- **PyYAML** - YAML parsing
- **networkx** - Dependency graph analysis
- **regex** - Advanced pattern matching

## Optional Dependencies

- **pydot** - Graph visualization (`cfn-lint[graph]`)
- **junit-xml** - JUnit output format (`cfn-lint[junit]`)
- **jschema-to-python** - SARIF output (`cfn-lint[sarif]`)

## Testing

- **pytest** - Test framework
- **pytest-xdist** - Parallel test execution
- **coverage** - Code coverage tracking

## Development Tools

- **ruff** - Linting and formatting
- **mypy** - Static type checking
- **pre-commit** - Git hooks

## AWS Integration

- Schemas generated from AWS CloudFormation resource provider schemas
- Updated via boto3 CloudFormation client
- Per-region schema support
- Pricing API for instance type validation

## Architecture Patterns

- Custom JSON Schema validator with CloudFormation extensions
- Rule-based validation system
- Template transformation pipeline (decode → transform → validate)
- Context-aware validation with condition scenarios
