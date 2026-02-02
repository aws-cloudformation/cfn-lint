# Rule Development Standards

## Rule Types

### 1. Template Path Rule (CfnLintKeyword)
- Validates values at specific template paths
- Use for: property value validation, format checking
- Extends: `CfnLintKeyword`
- Pattern: `keywords=["Resources/AWS::Service::Resource/Properties/PropertyName"]`

### 2. Schema-Based Rule (CfnLintJsonSchema)
- Validates using JSON Schema extensions
- **Requires both Python rule AND JSON schema file**
- Use for: complex property relationships, conditional validation
- Extends: `CfnLintJsonSchema` or `CfnLintJsonSchemaRegional`

### 3. JSON Schema Patch
- RFC 6902 patch operations on AWS schemas
- Use for: fixing schema bugs, adding constraints
- Location: `src/cfnlint/data/schemas/patches/extensions/all/<resource_type>/manual.json`

### 4. Custom Python Rule
- Full custom validation logic
- Use for: complex checks, resource relationships
- Extends: `CloudFormationLintRule`

## Rule Structure

```python
from cfnlint.rules import CloudFormationLintRule

class RuleName(CloudFormationLintRule):
    id = "E3XXX"  # Find next available in docs/rules.md
    shortdesc = "Brief description"
    description = "Detailed explanation with AWS documentation reference"
    source_url = "https://docs.aws.amazon.com/..."
    tags = ["resources", "service"]

    def match(self, cfn):
        matches = []
        # Validation logic
        return matches
```

## Rule Metadata

- **id**: Use correct category (E3XXX for resources)
- **shortdesc**: One line, no period
- **description**: Explain why this matters, link to AWS docs
- **source_url**: AWS documentation reference
- **tags**: Include resource category and service

## Validation Approach

1. **Search AWS documentation** for requirements
2. **Check existing schemas** for similar patterns
3. **Choose simplest rule type** that works
4. **Test with CloudFormation functions** (Ref, GetAtt, Sub)
5. **Handle conditions** if resource can be conditional

## Error Messages

- Be specific about what's wrong
- Include expected vs actual values
- Reference AWS documentation when helpful
- Example: "InstanceType 'm4.16xlarge' is a previous generation instance. Use current generation instances for better performance."

## Testing Requirements

- Test valid templates (no matches)
- Test invalid templates (expected matches)
- Test with CloudFormation functions
- Test with conditions (if applicable)
- Test edge cases

## Documentation

- Add rule to `docs/rules.md` with description and examples
- Include example of failing template
- Document any configuration options
- Link to AWS documentation

## Before Submitting

1. Run tests: `pytest test/unit/rules/resources/service/test_rule.py`
2. Check coverage: `pytest --cov=cfnlint.rules.resources.service.rule_name`
3. Run linter: `ruff check src/cfnlint/rules/resources/service/rule_name.py`
4. Type check: `mypy src/cfnlint/rules/resources/service/rule_name.py`
5. Test against real templates: `cfn-lint -c E3XXX template.yaml`
