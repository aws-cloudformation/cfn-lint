Help me create a new cfn-lint rule. Follow this process:

## Process

1. **Ask me what I want to validate** - Get the requirement first

2. **Search AWS CloudFormation documentation** for the resource type being validated to understand requirements and constraints

3. **Determine the rule type** based on the requirement

4. **Find the next available rule ID** by checking `docs/rules.md`

5. **Implement the rule** with proper structure

6. **Create test cases** with passing and failing templates

## Rule Types Reference

**1. Template Path Rule (CfnLintKeyword)**
- Validates values at specific CloudFormation template paths
- Triggered when validator reaches matching path (supports wildcards)
- Examples:
  - E3514: validates ARNs at `AWS::IAM::Policy/Properties/PolicyDocument/Statement/Resource`
  - E3038: checks `Resources/*/Type` for Serverless resources
- Location: `src/cfnlint/rules/resources/<service>/<RuleName>.py`
- Extends: `CfnLintKeyword`
- Pattern: `keywords=["path/to/validate"]` in `__init__`

**2. Schema-Based Rule (CfnLintJsonSchema)**
- Validates using JSON Schema loaded from extensions
- **REQUIRES both a Python rule AND a JSON schema file**
- For complex property relationship validation
- Examples:
  - E3680: Application load balancers require at least 2 subnets
  - E3652: Elasticsearch domain cluster instance type validation
- Python Location: `src/cfnlint/rules/resources/<service>/<RuleName>.py`
- Schema Location: `src/cfnlint/data/schemas/extensions/<resource_type>/<filename>.json`
- Extends: `CfnLintJsonSchema` or `CfnLintJsonSchemaRegional`
- Python Pattern:
```python
class MyRule(CfnLintJsonSchema):
    id = "E3XXX"
    shortdesc = "Short description"
    description = "Longer description"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Service::Resource/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_service_resource,
                filename="my_schema.json",
            ),
        )
```
- JSON Schema Pattern (if/then conditional validation):
```json
{
  "if": {
    "properties": {
      "Engine": {"const": "valkey"}
    },
    "required": ["Engine"]
  },
  "then": {
    "required": ["TransitEncryptionEnabled"]
  }
}
```

**3. JSON Schema Patch**
- JSON Patch operations (RFC 6902) to fix/enhance AWS schemas
- Location: `src/cfnlint/data/schemas/patches/extensions/all/<resource_type>/manual.json`
- Example:
```json
[
  {"op": "add", "path": "/properties/DelaySeconds/maximum", "value": 900},
  {"op": "add", "path": "/properties/DelaySeconds/minimum", "value": 0}
]
```

**4. Custom Python Rule**
- Full custom validation logic for complex checks
- Location: `src/cfnlint/rules/resources/<service>/<RuleName>.py`
- Extends: `CloudFormationLintRule`
- Use for: circular dependencies, resource relationships, template analysis

## Rule ID System

**Format: `[E|W|I]XXXX`**

**Categories:**
- `E0XXX` - Template structure (parsing, transforms)
- `E1XXX` - Functions (Ref, GetAtt, Sub, etc.)
- `E2XXX` - Parameters
- `E3XXX` - Resources
- `E4XXX` - Metadata
- `E6XXX` - Outputs
- `E7XXX` - Mappings
- `E8XXX` - Conditions
- `E9XXX` - Reserved for custom user rules

**Severity:**
- `E` (Error) - Will cause deployment failure
- `W` (Warning) - Best practice violation
- `I` (Info) - Informational (disabled by default, use `-c I`)

## File Locations

- Python rules: `src/cfnlint/rules/resources/<service>/<RuleName>.py`
- Schema extensions: `src/cfnlint/data/schemas/extensions/<resource_type>/<filename>.json`
- Schema patches: `src/cfnlint/data/schemas/patches/extensions/all/<resource_type>/manual.json`
- Tests: `test/unit/rules/resources/<service>/test_<rule_name>.py`

---

Now, what do you want to validate?
