"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context.parameters import ParameterSet
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.functions._BaseFn import BaseFn, _schema_needs_resolution


class _ChildRule(CloudFormationLintRule):
    id = "XXXXX"


@pytest.fixture(scope="module")
def rule(request):
    rule = BaseFn(resolved_rule="XXXXX")
    rule._schema = request.param.get("schema")

    rule.child_rules["XXXXX"] = _ChildRule()
    yield rule


@pytest.fixture
def template():
    return {"Parameters": {"MyString": {"Type": "String"}}}


@pytest.mark.parametrize(
    "name,rule,instance,parameters,expected",
    [
        (
            "Dynamic references are ignored",
            {
                "schema": {
                    "enum": ["Foo"],
                },
            },
            {"Fn::Sub": "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}"},
            [],
            [],
        ),
        (
            "Everything is fine",
            {"schema": {"enum": ["Foo"]}},
            {"Fn::Sub": "Foo"},
            {},
            [],
        ),
        (
            "Resolved Fn::Sub has no strict type validation",
            {
                "schema": {"type": ["integer"]},
            },
            {"Fn::Sub": "2"},
            [],
            [],
        ),
        (
            "Standard error",
            {
                "schema": {"enum": ["Foo"]},
            },
            {"Fn::Sub": "Bar"},
            [],
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': 'Bar'} is not one of ['Foo'] when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["enum"]),
                    rule=_ChildRule(),
                )
            ],
        ),
        (
            "Errors with context error",
            {
                "schema": {"anyOf": [{"enum": ["Foo"]}]},
            },
            {"Fn::Sub": "Bar"},
            [],
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': 'Bar'} is not valid "
                        "under any of the given schemas "
                        "when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["anyOf"]),
                    rule=_ChildRule(),
                    context=[
                        ValidationError(
                            message=(
                                "{'Fn::Sub': 'Bar'} is not one of "
                                "['Foo'] when '' is resolved"
                            ),
                            path=deque([]),
                            validator="enum",
                            schema_path=deque([0, "enum"]),
                            rule=_ChildRule(),
                        )
                    ],
                )
            ],
        ),
        (
            "Ref of a parameter with parameter set",
            {
                "schema": {"enum": ["Foo"]},
            },
            {"Ref": "MyString"},
            [
                ParameterSet(
                    parameters={"MyString": "Bar"},
                    source=None,
                )
            ],
            [
                ValidationError(
                    message=(
                        "{'Ref': 'MyString'} is not one of "
                        "['Foo'] when '' is resolved to 'Bar'"
                    ),
                    path=deque(["Ref"]),
                    validator="",
                    schema_path=deque(["enum"]),
                    rule=_ChildRule(),
                )
            ],
        ),
        (
            "Fn::Sub of a parameter with parameter set",
            {
                "schema": {"enum": ["Foo"]},
            },
            {"Fn::Sub": "${MyString}"},
            [
                ParameterSet(
                    parameters={"MyString": "Bar"},
                    source=None,
                )
            ],
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': '${MyString}'} is not one of "
                        "['Foo'] when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["enum"]),
                    rule=_ChildRule(),
                )
            ],
        ),
    ],
    indirect=["rule", "parameters"],
)
def test_resolve(name, instance, parameters, rule, expected, validator):
    errs = list(rule.resolve(validator, rule._schema, instance, {}))
    assert errs == expected, f"{name!r} failed and got errors {errs!r}"


class TestSchemaResolutionOptimization:
    """Test the _schema_needs_resolution optimization function"""

    def test_schema_needs_resolution_false(self):
        """Test schemas that don't need resolution"""
        # Basic type only
        assert not _schema_needs_resolution({"type": "string"})
        assert not _schema_needs_resolution({"type": "number"})
        assert not _schema_needs_resolution({"type": "boolean"})
        assert not _schema_needs_resolution({"type": "array"})
        assert not _schema_needs_resolution({"type": "object"})

        # Type with description (no constraints)
        assert not _schema_needs_resolution(
            {"type": "string", "description": "A simple string"}
        )

        # Multiple types without constraints
        assert not _schema_needs_resolution({"type": ["string", "number"]})

        # Schema with non-constraint keywords
        assert not _schema_needs_resolution(
            {
                "type": "string",
                "title": "My String",
                "description": "A description",
                "examples": ["example1", "example2"],
            }
        )

    def test_schema_needs_resolution_true(self):
        """Test schemas that need resolution"""
        # String constraints
        assert _schema_needs_resolution({"type": "string", "minLength": 1})
        assert _schema_needs_resolution({"type": "string", "maxLength": 10})
        assert _schema_needs_resolution({"type": "string", "pattern": "^[a-z]+$"})
        assert _schema_needs_resolution({"type": "string", "format": "email"})

        # Number constraints
        assert _schema_needs_resolution({"type": "number", "minimum": 0})
        assert _schema_needs_resolution({"type": "number", "maximum": 100})
        assert _schema_needs_resolution({"type": "number", "exclusiveMinimum": 0})
        assert _schema_needs_resolution({"type": "number", "exclusiveMaximum": 100})
        assert _schema_needs_resolution({"type": "number", "multipleOf": 5})

        # Value matching
        assert _schema_needs_resolution({"enum": ["a", "b", "c"]})
        assert _schema_needs_resolution({"const": "specific_value"})

        # Array constraints
        assert _schema_needs_resolution({"type": "array", "minItems": 1})
        assert _schema_needs_resolution({"type": "array", "maxItems": 5})
        assert _schema_needs_resolution({"type": "array", "uniqueItems": True})
        assert _schema_needs_resolution(
            {"type": "array", "contains": {"type": "string"}}
        )

        # Object constraints
        assert _schema_needs_resolution({"type": "object", "minProperties": 1})
        assert _schema_needs_resolution({"type": "object", "maxProperties": 10})
        assert _schema_needs_resolution({"type": "object", "required": ["name"]})
        assert _schema_needs_resolution(
            {"type": "object", "dependentRequired": {"name": ["age"]}}
        )

    def test_schema_needs_resolution_edge_cases(self):
        """Test edge cases"""
        # Non-dict schemas
        assert not _schema_needs_resolution("string")
        assert not _schema_needs_resolution(None)
        assert not _schema_needs_resolution([])
        assert not _schema_needs_resolution(123)
        assert not _schema_needs_resolution(True)

        # Empty schema
        assert not _schema_needs_resolution({})

        # Mixed constraint and non-constraint keywords
        assert _schema_needs_resolution(
            {
                "type": "string",
                "description": "A string with constraints",
                "minLength": 1,  # This makes it need resolution
            }
        )


class TestBaseFnValidation:
    """Test BaseFn validation logic including optimization paths"""

    def test_validate_optimization_path_basic_schema(self):
        """Test that validation optimization works for basic schemas"""
        rule = BaseFn()
        rule.types = ["string"]

        # Mock required methods
        def mock_key_value(instance):
            return "Fn::Sub", "test"

        def mock_schema(validator, instance):
            return {"type": "string"}

        def mock_validator(validator, schema):
            class MockSubValidator:
                def descend(self, value, schema, path=None):
                    return []

            return MockSubValidator()

        def mock_resolve_type(validator, schema):
            return ["string"]

        def mock_fix_errors(errors):
            return list(errors)

        rule.key_value = mock_key_value
        rule.schema = mock_schema
        rule.validator = mock_validator
        rule.resolve_type = mock_resolve_type
        rule.fix_errors = mock_fix_errors

        # Track if resolve is called
        resolve_called = False

        def mock_resolve(*args, **kwargs):
            nonlocal resolve_called
            resolve_called = True
            return []

        rule.resolve = mock_resolve

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()

        # Basic schema that doesn't need resolution
        schema = {"type": "string"}
        instance = {"Fn::Sub": "test"}

        # This should NOT call resolve() due to optimization
        list(rule.validate(validator, schema, instance, {}))
        assert not resolve_called, (
            "resolve() should not be called for basic schemas without resolved_rule"
        )

    def test_validate_calls_resolution_when_resolved_rule_exists(self):
        """Test that validation always calls resolution when resolved_rule is set"""
        rule = BaseFn(resolved_rule="TEST")
        rule.types = ["string"]
        rule.child_rules = {"TEST": _ChildRule()}

        # Mock required methods
        def mock_key_value(instance):
            return "Fn::Sub", "test"

        def mock_schema(validator, instance):
            return {"type": "string"}

        def mock_validator(validator, schema):
            class MockSubValidator:
                def descend(self, value, schema, path=None):
                    return []

            return MockSubValidator()

        def mock_resolve_type(validator, schema):
            return ["string"]

        def mock_fix_errors(errors):
            return list(errors)

        rule.key_value = mock_key_value
        rule.schema = mock_schema
        rule.validator = mock_validator
        rule.resolve_type = mock_resolve_type
        rule.fix_errors = mock_fix_errors

        # Track if resolve is called
        resolve_called = False

        def mock_resolve(*args, **kwargs):
            nonlocal resolve_called
            resolve_called = True
            return []

        rule.resolve = mock_resolve

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()

        # Basic schema that normally wouldn't need resolution
        schema = {"type": "string"}
        instance = {"Fn::Sub": "test"}

        # This should call resolve() because resolved_rule is set
        list(rule.validate(validator, schema, instance, {}))
        assert resolve_called, (
            "resolve() should always be called when resolved_rule is set"
        )

    def test_validate_calls_resolution_for_constraint_schema(self):
        """Test that validation calls resolution for schemas with constraints"""
        rule = BaseFn()
        rule.types = ["string"]

        # Mock required methods
        def mock_key_value(instance):
            return "Fn::Sub", "test"

        def mock_schema(validator, instance):
            return {"type": "string"}

        def mock_validator(validator, schema):
            class MockSubValidator:
                def descend(self, value, schema, path=None):
                    return []

            return MockSubValidator()

        def mock_resolve_type(validator, schema):
            return ["string"]

        def mock_fix_errors(errors):
            return list(errors)

        rule.key_value = mock_key_value
        rule.schema = mock_schema
        rule.validator = mock_validator
        rule.resolve_type = mock_resolve_type
        rule.fix_errors = mock_fix_errors

        # Track if resolve is called
        resolve_called = False

        def mock_resolve(*args, **kwargs):
            nonlocal resolve_called
            resolve_called = True
            return []

        rule.resolve = mock_resolve

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()

        # Schema with constraints that needs resolution
        schema = {"type": "string", "minLength": 1}
        instance = {"Fn::Sub": "test"}

        # This should call resolve() due to constraints
        list(rule.validate(validator, schema, instance, {}))
        assert resolve_called, "resolve() should be called for schemas with constraints"


class TestBaseFnTypeValidation:
    """Test the enhanced type validation logic"""

    def test_type_validation_with_no_resolved_type(self):
        """Test type validation when resolve_type returns None"""
        rule = BaseFn()
        rule.types = ["string"]

        # Mock resolve_type to return None
        def mock_resolve_type(validator, schema):
            return None

        rule.resolve_type = mock_resolve_type

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()
        schema = {"type": "string"}
        instance = {"Fn::Sub": "test"}

        # Should not yield any errors when resolve_type returns None
        errors = list(rule.validate_fn_output_types(validator, schema, instance))
        assert len(errors) == 0

    def test_type_validation_compatibility_check(self):
        """Test basic type compatibility validation"""
        rule = BaseFn()
        rule.types = ["string"]

        # Mock resolve_type to return compatible type
        def mock_resolve_type(validator, schema):
            return ["string"]

        rule.resolve_type = mock_resolve_type

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()
        schema = {"type": "string"}
        instance = {"Fn::Sub": "test"}

        # Should not yield errors for compatible types
        errors = list(rule.validate_fn_output_types(validator, schema, instance))
        assert len(errors) == 0

    def test_type_validation_incompatible_types(self):
        """Test type validation with incompatible types"""
        rule = BaseFn()
        rule.types = ["array"]  # Function returns array

        # Mock resolve_type to return incompatible type
        def mock_resolve_type(validator, schema):
            return ["string"]  # Schema expects string but function returns array

        rule.resolve_type = mock_resolve_type

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()
        schema = {"type": "string"}
        instance = {"Fn::GetAtt": ["Resource", "Arn"]}

        # Should yield error for incompatible types
        errors = list(rule.validate_fn_output_types(validator, schema, instance))
        assert len(errors) == 1
        assert "is not of type" in str(errors[0])

    def test_type_validation_strict_object_with_properties(self):
        """Test strict type validation for objects with properties"""
        rule = BaseFn()
        rule.types = ["array"]

        # Mock resolve_type to return object type
        def mock_resolve_type(validator, schema):
            return ["object"]

        rule.resolve_type = mock_resolve_type

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        instance = {"Fn::GetAtt": ["Resource", "Arn"]}

        # Should yield error due to strict type checking with properties
        errors = list(rule.validate_fn_output_types(validator, schema, instance))
        assert len(errors) == 1
        assert "is not of type" in str(errors[0])

    def test_type_validation_array_object_compatibility(self):
        """Test array-object compatibility for bare object types"""
        rule = BaseFn()
        rule.types = ["array"]

        # Mock resolve_type to return object type
        def mock_resolve_type(validator, schema):
            return ["object"]

        rule.resolve_type = mock_resolve_type

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()
        schema = {"type": "object"}  # Bare object without properties
        instance = {"Fn::GetAtt": ["Resource", "Arn"]}

        # Should not yield error due to array-object compatibility
        errors = list(rule.validate_fn_output_types(validator, schema, instance))
        assert len(errors) == 0


class TestBaseFnEdgeCases:
    """Test edge cases and error conditions"""

    def test_validate_with_validation_errors(self):
        """Test validation when there are type validation errors"""
        rule = BaseFn()
        rule.types = ["array"]  # Function returns array

        # Mock methods to simulate validation errors
        def mock_key_value(instance):
            return "Fn::GetAtt", ["Resource", "Arn"]

        def mock_schema(validator, instance):
            return {"type": "array"}

        def mock_validator(validator, schema):
            class MockSubValidator:
                def descend(self, value, schema, path=None):
                    return []

            return MockSubValidator()

        def mock_resolve_type(validator, schema):
            return ["string"]  # Schema expects string but function returns array

        def mock_fix_errors(errors):
            return list(errors)

        rule.key_value = mock_key_value
        rule.schema = mock_schema
        rule.validator = mock_validator
        rule.resolve_type = mock_resolve_type
        rule.fix_errors = mock_fix_errors

        # Mock validator
        class MockValidator:
            pass

        validator = MockValidator()
        schema = {"type": "string"}  # Expects string
        instance = {"Fn::GetAtt": ["Resource", "Arn"]}  # Returns array

        # Should return early due to validation errors, not call resolve
        errors = list(rule.validate(validator, schema, instance, {}))
        assert len(errors) == 1  # Type validation error
        assert "is not of type" in str(errors[0])

    def test_schema_needs_resolution_all_constraint_keywords(self):
        """Test _schema_needs_resolution with all constraint keywords"""
        # Test all value-dependent keywords individually
        constraint_keywords = [
            "minLength",
            "maxLength",
            "pattern",
            "format",
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "multipleOf",
            "minItems",
            "maxItems",
            "uniqueItems",
            "contains",
            "minProperties",
            "maxProperties",
            "required",
            "dependentRequired",
            "enum",
            "const",
        ]

        for keyword in constraint_keywords:
            schema = {keyword: "test_value"}
            assert _schema_needs_resolution(schema), (
                f"Keyword '{keyword}' should require resolution"
            )
