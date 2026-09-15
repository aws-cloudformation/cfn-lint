# Project Structure

## Directory Organization

```
src/cfnlint/           # Source code
├── rules/             # Validation rules by category
│   ├── resources/     # Resource rules (organized by AWS service)
│   ├── parameters/    # Parameter validation
│   ├── functions/     # Intrinsic function validation
│   ├── jsonschema/    # Schema-based rules
│   └── custom/        # Custom rule operators
├── data/schemas/      # JSON schemas (sourced from resource-provider-enhanced-schemas)
│   ├── providers/     # Per-region index files: which resource types exist per region + content hashes
│   ├── resources/     # Content-addressed schema bodies (<hash>.json) — the actual resource schemas
│   └── extensions/    # Schema extensions (organized by resource type)
├── jsonschema/        # Custom JSON Schema validator
├── template/          # Template representation
├── schema/            # Schema management
├── context/           # Validation context
└── runner/            # CLI and execution

test/                  # Tests mirror src/ structure
├── unit/              # Unit tests
├── integration/       # Integration tests
└── fixtures/          # Test templates and data

scripts/               # Maintenance and schema updates
```

## Naming Conventions

### Rules
- **File**: `src/cfnlint/rules/resources/<service>/<RuleName>.py`
- **Class**: PascalCase matching filename (e.g., `InstanceImageId`)
- **Service folders**: Lowercase AWS service name (e.g., `ec2`, `rds`, `lambda`)

### Tests
- **File**: `test/unit/rules/resources/<service>/test_<rule_name>.py`
- **Class**: `Test<RuleName>`
- **Methods**: `test_<scenario>` (e.g., `test_valid_instance_type`)

### Schemas
- **Extensions**: `src/cfnlint/data/schemas/extensions/<resource_type>/<descriptive_name>.json`
- **Schema corrections/constraints**: add these in the [resource-provider-enhanced-schemas](https://github.com/aws-cloudformation/resource-provider-enhanced-schemas) repo (e.g. `schemas/patches/extensions/<resource_type>/manual.json`), NOT in this repo — cfn-lint consumes the assembled result.
- **Resource type format**: Lowercase with underscores (e.g., `aws_ec2_instance`)

## Import Patterns

- Absolute imports from `cfnlint` package
- Group imports: stdlib → third-party → cfnlint
- Type imports in `TYPE_CHECKING` block

## Rule ID System

- `E0XXX` - Template structure
- `E1XXX` - Functions
- `E2XXX` - Parameters
- `E3XXX` - Resources (most common)
- `E4XXX` - Metadata
- `E6XXX` - Outputs
- `E7XXX` - Mappings
- `E8XXX` - Conditions
- `E9XXX` - Reserved for user custom rules
- `W` prefix for warnings
- `I` prefix for informational (opt-in)

## File Organization

- One rule per file
- One test file per rule
- Schema extensions grouped by resource type
- Fixtures organized by test category
