# Testing Standards

## Test Structure

### Unit Tests
- Mirror source structure in `test/unit/`
- One test file per rule: `test_<rule_name>.py`
- Test class: `Test<RuleName>`
- Use pytest fixtures for common setup

### Test Methods
- Name pattern: `test_<scenario>`
- Examples: `test_valid_template`, `test_invalid_instance_type`, `test_with_conditions`
- One assertion focus per test

## Rule Testing Pattern

```python
from cfnlint.rules.resources.service.RuleName import RuleName

class TestRuleName:
    def test_valid_template(self):
        rule = RuleName()
        template = {...}  # Valid template
        matches = rule.match(template)
        assert len(matches) == 0

    def test_invalid_property(self):
        rule = RuleName()
        template = {...}  # Invalid template
        matches = rule.match(template)
        assert len(matches) == 1
        assert matches[0].rule.id == "E3XXX"
```

## Fixtures

### Template Fixtures
- Location: `test/fixtures/templates/`
- Organized by category: `good/`, `bad/`, `quickstart/`
- Use YAML for readability
- Include minimal required properties

### Inline Templates
- Prefer inline for simple test cases
- Use dict literals for clarity
- Include only relevant properties

## Assertions

- Check match count: `assert len(matches) == expected`
- Verify rule ID: `assert matches[0].rule.id == "E3XXX"`
- Check path: `assert matches[0].path == ["Resources", "MyResource", "Properties", "Property"]`
- Validate message: `assert "expected text" in matches[0].message`

## Coverage

- Aim for 100% line coverage on rules
- Test both valid and invalid cases
- Test edge cases and boundary conditions
- Test with CloudFormation functions (Ref, GetAtt, Sub)
- Test with conditions when applicable

## Running Tests

- All tests: `pytest`
- Specific test: `pytest test/unit/rules/resources/service/test_rule.py`
- With coverage: `pytest --cov=cfnlint`
- Parallel: `pytest -n auto`

## Test Data

- Keep templates minimal
- Use realistic AWS resource configurations
- Include comments explaining test purpose
- Reuse common fixtures when possible
