# cfn-lint Architecture Guide

## Overview

cfn-lint is a CloudFormation template validator that validates YAML/JSON templates against AWS CloudFormation resource provider schemas and additional best practice rules. The codebase is ~133k LOC of Python supporting CloudFormation templates, SAM transforms, and language extensions.

## Core Architecture

### High-Level Flow
```
Template File(s) → Decode → Transform → Validate (Rules) → Format → Output
```

### Key Components

#### 1. **Entry Points** (`src/cfnlint/`)
- **CLI** (`runner/cli.py`): Main command-line interface, argument parsing, orchestration
- **API** (`api.py`): Programmatic interface with `lint()`, `lint_all()`, `lint_file()` functions
- **Config** (`config.py`): Configuration management from CLI args, config files, and template metadata

#### 2. **Template Processing Pipeline**

**Decode** (`src/cfnlint/decode/`)
- `cfn_yaml.py`: YAML parser with CloudFormation-specific constructs (GetAtt, Ref, etc.)
- `cfn_json.py`: JSON parser with position tracking for error reporting
- `node.py`: Creates dict/list/str node classes that preserve source location
- Outputs: Template with location metadata for precise error reporting

**Transform** (`src/cfnlint/template/transforms/`)
- `_sam.py`: AWS SAM (Serverless Application Model) transformation
- `_language_extensions.py`: Language extensions (Fn::ForEach, etc.)
- Transforms templates before validation
- Handles S3 URI resolution, managed policies, variable replacement

**Template** (`src/cfnlint/template/template.py`)
- Core `Template` class: Central data structure representing parsed template
- Methods for querying: `get_resources()`, `get_parameters()`, `get_conditions()`
- Condition evaluation: `get_conditions_from_path()`, `get_condition_scenarios_below_path()`
- Graph building: `build_graph()` for dependency analysis
- GetAtt resolution: `get_valid_getatts()`, `get_valid_refs()`

#### 3. **Validation Engine**

**Rules System** (`src/cfnlint/rules/`)
- Base class: `_rule.py` - `CloudFormationLintRule` with `match()` methods
- Collections: `_rules.py` - `Rules` and `RulesCollection` for managing rule sets
- Rule categories (subdirectories):
  - `resources/`: Resource-specific validation (EC2, RDS, Lambda, etc.)
  - `parameters/`: Parameter validation
  - `outputs/`: Output validation
  - `functions/`: Intrinsic function validation (Ref, GetAtt, Sub, etc.)
  - `conditions/`: Condition validation
  - `jsonschema/`: JSON Schema-based validation
  - `custom/`: Custom rule operators

**JSON Schema Validation** (`src/cfnlint/jsonschema/`)
- Custom JSON Schema validator implementation
- `validators.py`: Core `Validator` class with CloudFormation-specific extensions
- `_keywords.py`: Standard JSON Schema keywords (type, enum, pattern, etc.)
- `_keywords_cfn.py`: CloudFormation-specific keywords (cfnType, dynamicValidation)
- `_resolvers_cfn.py`: Resolves CloudFormation functions during validation
- `_filter.py`: Filters schemas based on conditions/functions
- `_format.py`: Format checkers (date, regex, IP addresses, etc.)

**Schema Management** (`src/cfnlint/schema/`)
- `manager.py`: `ProviderSchemaManager` - loads/caches AWS resource schemas
- `other_schema_manager.py`: Non-resource schemas (parameters, outputs, etc.)
- `_schema.py`: Schema wrapper with ref/getatt support
- `_getatts.py`: GetAtt attribute resolution from schemas
- `_patch.py`: Schema patching for corrections/enhancements
- `resolver/`: Schema reference resolution

#### 4. **Context System** (`src/cfnlint/context/`)
- `context.py`: `Context` class - tracks validation state (path, resources, parameters)
- `conditions/`: Condition evaluation and satisfiability checking
- `_mappings.py`: Mapping resolution
- `parameters.py`: Parameter tracking
- Provides context for rules during validation

#### 5. **Conditions Engine** (`src/cfnlint/conditions/`)
- `conditions.py`: `Conditions` class - manages condition logic
- `_condition.py`: Condition types (And, Or, Not, Equals)
- `_equals.py`: Equality comparisons
- `_rule.py`: Condition rules and assertions
- Determines satisfiability and builds scenarios for validation

#### 6. **Output Formatting** (`src/cfnlint/formatters/`)
- `base.py`: Base formatter interface
- Formats: `json.py`, `junit.py`, `sarif.py`, `pretty.py`, `parseable.py`, `quiet.py`
- `match.py`: Match/error data structure

#### 7. **Data & Schemas** (`src/cfnlint/data/`)
- `schemas/`: JSON Schema definitions
  - `providers/`: Per-region resource schemas (generated from AWS APIs)
  - `extensions/`: Schema extensions for additional validation
  - `patches/`: Schema corrections
  - `other/`: Non-resource schemas (functions, conditions, parameters, etc.)
- `AdditionalSpecs/`: Additional specifications
- `Serverless/`: SAM-related data

## Key Workflows

### Template Validation Flow
1. **Parse Config**: CLI args + config file + environment → `Config` object
2. **Discover Templates**: Glob patterns → list of template files
3. **For each template**:
   - **Decode**: YAML/JSON → Template with location nodes
   - **Transform**: Apply SAM/language extensions if present
   - **Initialize Context**: Create validation context
   - **Run Rules**: Execute enabled rules against template
     - Rules query template structure
     - Rules validate against schemas
     - Rules check best practices
   - **Collect Matches**: Gather errors/warnings/info
4. **Format Output**: Matches → formatted output (JSON/JUnit/SARIF/etc.)
5. **Exit**: Exit code based on severity

### Rule Execution
1. **Filter Rules**: Apply include/exclude/mandatory filters
2. **Initialize Rules**: Call `initialize()` on rules needing setup
3. **For each rule**:
   - Check if enabled for current context
   - Call `match()` or `validate()` method
   - Rule queries template via Template API
   - Rule validates using JSON Schema validator
   - Rule returns list of `Match` objects
4. **Deduplicate**: Remove duplicate matches
5. **Return**: All matches for formatting

### Schema Validation
1. **Get Schema**: Retrieve resource schema from manager
2. **Create Validator**: Initialize JSON Schema validator with CloudFormation extensions
3. **Validate**: Walk template structure
   - Resolve CloudFormation functions (Ref, GetAtt, etc.)
   - Check types, enums, patterns
   - Validate required properties
   - Check property constraints
4. **Convert Errors**: JSON Schema errors → cfn-lint Match objects

## Directory Structure

```
src/cfnlint/
├── runner/           # CLI and template runners
│   ├── cli.py        # Main CLI entry point
│   ├── template/     # Template validation runner
│   ├── parameter_file/  # Parameter file handling
│   └── deployment_file/ # Deployment file handling
├── decode/           # Template parsing
├── template/         # Template representation
│   └── transforms/   # SAM and language extensions
├── rules/            # Validation rules
│   ├── _rule.py      # Base rule class
│   ├── _rules.py     # Rule collections
│   ├── resources/    # Resource rules
│   ├── parameters/   # Parameter rules
│   ├── functions/    # Function rules
│   ├── jsonschema/   # Schema-based rules
│   └── custom/       # Custom rule operators
├── jsonschema/       # JSON Schema validator
├── schema/           # Schema management
│   └── resolver/     # Schema reference resolution
├── context/          # Validation context
│   └── conditions/   # Condition evaluation
├── conditions/       # Condition logic engine
├── formatters/       # Output formatters
├── data/             # Schemas and specifications
│   └── schemas/
│       ├── providers/     # AWS resource schemas
│       ├── extensions/    # Schema extensions
│       ├── patches/       # Schema patches
│       └── other/         # Non-resource schemas
├── config.py         # Configuration management
├── api.py            # Public API
├── core.py           # Core validation logic
├── match.py          # Match/error data structure
└── helpers.py        # Utility functions

scripts/              # Maintenance scripts
├── boto/             # Schema generation from boto3
├── release/          # Release automation
└── update_*.py       # Schema update scripts

test/                 # Test suite
├── unit/             # Unit tests (mirrors src structure)
├── integration/      # Integration tests
└── fixtures/         # Test fixtures
```

## Important Classes

### Template (`template/template.py`)
- Central data structure for parsed templates
- Methods: `get_resources()`, `get_parameters()`, `get_conditions()`, `get_values()`
- Condition evaluation and scenario generation
- Graph building for dependency analysis

### CloudFormationLintRule (`rules/_rule.py`)
- Base class for all rules
- Key methods: `match()`, `validate()`, `configure()`, `is_enabled()`
- Properties: `id`, `shortdesc`, `description`, `severity`

### Rules (`rules/_rules.py`)
- Manages collection of rules
- Filtering, registration, execution
- Methods: `run()`, `run_check()`, `filter()`, `extend()`

### Validator (`jsonschema/validators.py`)
- CloudFormation-aware JSON Schema validator
- Methods: `validate()`, `iter_errors()`, `descend()`, `resolve_value()`
- Handles CloudFormation functions during validation

### Context (`context/context.py`)
- Tracks validation state
- Properties: `resources`, `parameters`, `path`, `transforms`
- Methods: `evolve()`, `descend()`

### Conditions (`conditions/conditions.py`)
- Manages condition logic
- Methods: `satisfiable()`, `build_scenarios()`, `check_implies()`

### ProviderSchemaManager (`schema/manager.py`)
- Loads and caches AWS resource schemas
- Methods: `get_resource_schema()`, `update()`, `patch()`

## Extension Points

### Custom Rules
1. **Python Rules**: Create class extending `CloudFormationLintRule` in `--append-rules` path
2. **Custom Rule Files**: Text file with format `<ResourceType> <Property> <Operator> <Value>`
3. Operators: `EQUALS`, `NOT_EQUALS`, `IN_SET`, `NOT_IN_SET`, `REGEX_MATCH`, etc.

### Schema Extensions
- Add JSON Schema files to `data/schemas/extensions/<resource_type>/`
- Use `if/then` for conditional validation
- Extend base AWS schemas with additional constraints

### Schema Patches
- Override/fix AWS schemas via `data/schemas/patches/`
- Applied during schema loading

### Custom Formatters
- Extend `BaseFormatter` class
- Implement `_format()` or `print_matches()` method

## Data Flow Examples

### Example: Validating EC2 Instance
1. Template decoded → `Template` object with EC2::Instance resource
2. Rules filtered → EC2-specific rules enabled
3. Schema loaded → EC2::Instance schema from `providers/<region>.py`
4. Rule execution:
   - `ResourceType` rule checks type exists
   - `Properties` rule validates against schema
   - `InstanceImageId` rule checks ImageId format
   - `PreviousGenerationInstanceType` warns on old instance types
5. Schema validation:
   - Validator checks `InstanceType` enum
   - Validator checks required properties
   - Validator resolves Ref/GetAtt functions
6. Matches collected → formatted → output

### Example: Condition Evaluation
1. Template has condition: `IsProduction: !Equals [!Ref Environment, "prod"]`
2. Conditions engine builds scenarios: `{IsProduction: True}`, `{IsProduction: False}`
3. Resource has `Condition: IsProduction`
4. Rules validate resource in both scenarios
5. Errors reported with condition context

## Testing Strategy

### Unit Tests (`test/unit/`)
- Mirror source structure
- Test individual rules, functions, components
- Use fixtures from `test/fixtures/`
- Pytest-based

### Integration Tests (`test/integration/`)
- End-to-end template validation
- Test against real CloudFormation templates
- QuickStart templates, good/bad templates
- Schema validation tests

### Test Fixtures (`test/fixtures/`)
- `templates/`: Sample CloudFormation templates
- `results/`: Expected validation results
- `schemas/`: Test schemas
- `rules/`: Custom rule examples

## Schema Update Process

Schemas are generated from AWS APIs and updated regularly:

1. **Boto3 Update** (`scripts/boto/update_schemas_from_boto.py`):
   - Fetches resource schemas from boto3
   - Generates per-region schema files
   - Applies automated patches

2. **Manual Patches** (`scripts/boto/_manual_patches.py`):
   - Hand-crafted schema corrections
   - Applied during generation

3. **API Updates** (`scripts/update_schemas_from_aws_api.py`):
   - Fetches additional data from AWS APIs (RDS, ElastiCache)
   - Updates engine versions, instance types

4. **Pricing Updates** (`scripts/update_specs_from_pricing.py`):
   - Fetches instance types from AWS Pricing API

## Performance Considerations

- **Schema Caching**: Schemas loaded once and cached
- **Rule Filtering**: Only enabled rules execute
- **Lazy Evaluation**: Conditions evaluated only when needed
- **Parallel Processing**: Multiple templates can be validated in parallel (external)

## Common Patterns

### Adding a New Rule
1. Create class in appropriate `rules/` subdirectory
2. Extend `CloudFormationLintRule` or `CfnLintJsonSchema`
3. Implement `match()` or `validate()` method
4. Set `id`, `shortdesc`, `description`, `severity`
5. Add unit tests in `test/unit/rules/`

### Adding Schema Extension
1. Create JSON Schema file in `data/schemas/extensions/<resource_type>/`
2. Use `if/then` for conditional validation
3. Reference AWS documentation in comments
4. Add test cases

### Querying Template in Rules
```python
# Get all resources of type
resources = template.get_resources(['AWS::EC2::Instance'])

# Get resource properties
for resource_name, resource_values in resources.items():
    properties = resource_values.get('Properties', {})

# Get values considering conditions
for value in template.get_values(properties, 'InstanceType'):
    # value is tuple: (value, path)
```

## Key Files to Know

- `src/cfnlint/runner/cli.py`: CLI entry point
- `src/cfnlint/template/template.py`: Core template representation
- `src/cfnlint/rules/_rule.py`: Base rule class
- `src/cfnlint/jsonschema/validators.py`: JSON Schema validator
- `src/cfnlint/schema/manager.py`: Schema management
- `src/cfnlint/config.py`: Configuration handling
- `scripts/boto/update_schemas_from_boto.py`: Schema generation

## Debugging Tips

1. **Enable Debug Logging**: Use `-D` flag for detailed rule execution logs
2. **Enable Info Logging**: Use `-I` flag for template processing info
3. **Test Single Rule**: Use `-c <rule_id>` to run only specific rule
4. **Ignore Rules**: Use `-i <rule_id>` to exclude problematic rules
5. **Check Schema**: Use `--info` to see SAM transformation details
6. **Validate Schema**: Integration tests in `test/integration/test_schema_files.py`

## Version Information

- Python: 3.9-3.13 supported
- Dependencies: boto3, jsonschema, pydot (optional), junit-xml (optional)
- AWS Regions: All public regions + GovCloud + China + ISO regions
