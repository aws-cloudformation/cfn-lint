# cfn-lint (v2)

A fast [CloudFormation](https://aws.amazon.com/cloudformation/) template linter
with a Rust engine and Python bindings.

`cfn-lint` validates CloudFormation templates (JSON and YAML) against the
resource provider schemas and a large set of rules covering template structure,
intrinsic functions, conditions, mappings, outputs, and resource-specific
checks.

## Installation

```bash
pip install cfn-lint
```

## Command line

```bash
cfn-lint -t template.yaml
# or with positional paths
cfn-lint template.yaml another-template.json
```

Useful flags:

| Flag | Description |
| --- | --- |
| `-t, --template` | Template file(s) to validate |
| `-f, --format` | Output format (default: `parseable`) |
| `-r, --regions` | AWS regions to validate against |
| `-i, --ignore-checks` | Rule IDs to ignore |
| `-c, --include-checks` | Rule IDs to include |
| `-l, --list-rules` | List all rules and exit |
| `-u, --update-schemas` | Download the latest CloudFormation schemas |

Run `cfn-lint --help` for the full list.

## Python API

```python
import cfn_lint

# Lint a template string.
matches = cfn_lint.lint(
    """
    AWSTemplateFormatVersion: '2010-09-09'
    Resources:
      Bucket:
        Type: AWS::S3::Bucket
    """
)

# Lint a template file.
matches = cfn_lint.lint_file("template.yaml")

for m in matches:
    print(m.rule_id, m.severity, m.message, m.line_start)
```

Each returned `Match` exposes `rule_id`, `message`, `severity`, `line_start`,
`column_start`, `line_end`, and `column_end`.

Optional keyword arguments for both `lint` and `lint_file`: `regions`,
`ignore_checks`, `include_checks`, `include_experimental`, `configure_rules`,
and `mandatory_checks`.

## License

Licensed under the MIT-0 License. See [`LICENSE`](LICENSE).
