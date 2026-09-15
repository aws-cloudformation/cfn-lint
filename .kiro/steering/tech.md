# Technology Stack

## Language & Runtime

- **Python 3.10-3.14** - Core language (`requires-python = ">=3.10,<3.15"`)
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

- Resource provider schemas are sourced from the [resource-provider-enhanced-schemas](https://github.com/aws-cloudformation/resource-provider-enhanced-schemas) repo, downloaded as `schemas-cfn-lint.zip` from its `latest` release (see `src/cfnlint/schema/manager.py`; refresh with `cfn-lint --update-specs`)
- Per-region schema support
- boto3 is still used by supplemental scripts that enrich schemas with AWS API data (e.g. RDS/ElastiCache engine versions) and the Pricing API for instance-type validation

## Architecture Patterns

- Custom JSON Schema validator with CloudFormation extensions
- Rule-based validation system
- Template transformation pipeline (decode → transform → validate)
- Context-aware validation with condition scenarios
