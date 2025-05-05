"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._keywords_cfn import (
    _raw_type,
    _raw_type_strict,
    additionalProperties,
    cfn_type,
    cfnContext,
    dynamicValidation,
)


@pytest.mark.parametrize(
    "instance,schema,context_params,expected",
    [
        # Function allowed in context
        (
            {"Ref": "MyParam"},
            {"cfnContext": {"functions": ["Ref"], "schema": {"type": "object"}}},
            {},
            [],
        ),
        # Function not allowed in context
        (
            {"Fn::GetAtt": ["MyResource", "Arn"]},
            {"cfnContext": {"functions": ["Ref"], "schema": {"type": "string"}}},
            {},
            [
                ValidationError(
                    "{'Fn::GetAtt': ['MyResource', 'Arn']} is not of type 'string'",
                    path=deque([]),
                    schema_path=deque(["schema", "type"]),
                    validator="type",
                )
            ],
        ),
        # Valid schema in context
        (
            "test",
            {"cfnContext": {"functions": [], "schema": {"type": "string"}}},
            {},
            [],
        ),
        # Invalid schema in context
        (
            123,
            {"cfnContext": {"functions": [], "schema": {"type": "string"}}},
            {},
            [
                ValidationError(
                    "123 is not of type 'string'",
                    path=deque([]),
                    schema_path=deque(["schema", "type"]),
                    validator="type",
                )
            ],
        ),
        # Test with pseudoParameters
        (
            "AWS::Region",
            {
                "cfnContext": {
                    "functions": [],
                    "schema": {"type": "string"},
                    "pseudoParameters": ["AWS::Region", "AWS::AccountId"],
                }
            },
            {},
            [],
        ),
        # Test with references
        (
            {"Ref": "MyResource"},
            {
                "cfnContext": {
                    "functions": ["Ref"],
                    "schema": {"type": "object"},
                    "references": ["Parameters"],
                }
            },
            {},
            [],
        ),
        # Test with references including Resources
        (
            {"Ref": "MyResource"},
            {
                "cfnContext": {
                    "functions": ["Ref"],
                    "schema": {"type": "object"},
                    "references": ["Parameters", "Resources"],
                }
            },
            {},
            [],
        ),
        # Test with function object without $ref
        (
            {"Ref": "MyParam"},
            {
                "cfnContext": {
                    "functions": {"key": "value"},  # Object without $ref
                    "schema": {"type": "object"},
                }
            },
            {},
            [],
        ),
        # Test with null functions
        (
            {"Ref": "MyParam"},
            {"cfnContext": {"functions": None, "schema": {"type": "object"}}},
            {},
            [],
        ),
        # Test with null pseudoParameters
        (
            "AWS::Region",
            {
                "cfnContext": {
                    "functions": [],
                    "schema": {"type": "string"},
                    "pseudoParameters": None,
                }
            },
            {},
            [],
        ),
    ],
)
def test_cfn_context(instance, schema, context_params, expected, validator):
    if context_params:
        validator = validator.evolve(context=validator.context.evolve(**context_params))

    errs = list(cfnContext(validator, schema["cfnContext"], instance, schema))
    assert errs == expected


@pytest.mark.parametrize(
    "instance,schema,mock_resolver,expected",
    [
        # Test with functions as object with $ref
        (
            {"Ref": "MyParam"},
            {
                "cfnContext": {
                    "functions": {"$ref": "#/definitions/functions"},
                    "schema": {"type": "object"},
                }
            },
            {"#/definitions/functions": ["Ref"]},
            [],
        ),
    ],
)
def test_cfn_context_with_refs(instance, schema, mock_resolver, expected, validator):
    # Mock resolver for $ref resolution
    class MockResolver:
        def resolve(self, ref):
            return "", mock_resolver.get(ref, {})

    validator = validator.evolve(resolver=MockResolver())
    errs = list(cfnContext(validator, schema["cfnContext"], instance, schema))
    assert errs == expected


@pytest.mark.parametrize(
    "instance,schema,functions,expected",
    [
        # Test case where function matches and should be allowed
        (
            {"Ref": "MyParam", "Fn::GetAtt": ["Resource", "Attr"]},
            {"additionalProperties": False, "properties": {"Ref": {}}},
            ["Ref", "Fn::GetAtt"],
            [
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "('Fn::GetAtt' was unexpected)"
                    ),
                    path=deque(["Fn::GetAtt"]),
                )
            ],
        ),
        # Test with empty instance
        (
            {},
            {"additionalProperties": False, "properties": {"Ref": {}}},
            ["Ref"],
            [],
        ),
        # Test with function in context.functions
        (
            {"Ref": "MyParam"},
            {"additionalProperties": False, "properties": {}},
            ["Ref"],
            [],
        ),
    ],
)
def test_additional_properties_with_functions(
    instance, schema, functions, expected, validator
):
    # Set up validator with functions
    validator = validator.evolve(context=validator.context.evolve(functions=functions))
    errs = list(additionalProperties(validator, False, instance, schema))
    assert errs == expected


@pytest.mark.parametrize(
    "template,path,instance,schema,context_params,expected",
    [
        # Transform check fails when transform is missing
        (
            {},
            {},
            "any_value",
            {"dynamicValidation": {"transformCheck": "AWS::LanguageExtensions"}},
            {},
            [
                ValidationError(
                    (
                        "Transform 'AWS::LanguageExtensions' is "
                        "required but not present in the template"
                    ),
                    path=deque([]),
                )
            ],
        ),
        # Transform check passes when transform is present
        (
            {"Transform": "AWS::LanguageExtensions"},
            {},
            "any_value",
            {"dynamicValidation": {"transformCheck": "AWS::LanguageExtensions"}},
            {},
            [],
        ),
        # Valid condition reference
        (
            {"Conditions": {"Condition1": {}, "Condition2": {}}},
            {},
            "Condition1",
            {"dynamicValidation": {"context": "conditions"}},
            {},
            [],
        ),
        # Invalid condition reference
        (
            {"Conditions": {"Condition1": {}, "Condition2": {}}},
            {},
            "InvalidCondition",
            {"dynamicValidation": {"context": "conditions"}},
            {},
            [
                ValidationError(
                    "'InvalidCondition' is not one of ['Condition1', 'Condition2']",
                    schema_path=deque(["enum"]),
                    path=deque([]),
                    validator="enum",
                )
            ],
        ),
        # Path check passes with matching pattern
        (
            {},
            {"path": ["Resources", "MyResource", "Properties", "InstanceType"]},
            "any_value",
            {
                "dynamicValidation": {
                    "pathCheck": "Resources/MyResource/Properties/InstanceType"
                }
            },
            {},
            [],
        ),
        # Path check fails with non-matching pattern
        (
            {},
            {"path": ["Parameters", "MyParam"]},
            "any_value",
            {"dynamicValidation": {"pathCheck": "Resources/MyResource/Properties"}},
            {},
            [
                ValidationError(
                    (
                        "'Parameters/MyParam' does not match "
                        "'^Resources/MyResource/Properties.*$'"
                    ),
                    schema_path=deque(["pattern"]),
                    path=deque([]),
                    validator="pattern",
                )
            ],
        ),
        # Test with non-object dynamicValidation value
        (
            {},
            {},
            "test",
            {"dynamicValidation": "not-an-object"},
            {},
            [],
        ),
        # Test with mappings context
        (
            {},
            {},
            "MyMapping",
            {"dynamicValidation": {"context": "mappings"}},
            {
                "mappings": type(
                    "obj",
                    (object,),
                    {"maps": {}, "mappings": {}},  # Empty mappings for this test
                )()
            },
            [
                ValidationError(
                    "'MyMapping' is not one of []",
                    schema_path=deque(["enum"]),
                    path=deque([]),
                    validator="enum",
                )
            ],
        ),
        # Test with context that's not a string
        (
            {},
            {},
            "test",
            {"dynamicValidation": {"context": 123}},  # Not a string
            {},
            [],
        ),
        # Test with context that doesn't match any collection
        (
            {},
            {},
            "test",
            {"dynamicValidation": {"context": "unknown_context"}},
            {},
            [],
        ),
    ],
    indirect=["template", "path"],
)
def test_dynamic_validation(
    template, path, instance, schema, context_params, expected, validator
):
    if context_params:
        validator = validator.evolve(context=validator.context.evolve(**context_params))

    errs = list(
        dynamicValidation(validator, schema["dynamicValidation"], instance, schema)
    )
    assert errs == expected


@pytest.mark.parametrize(
    "type_name,instance,strict,expected_result",
    [
        # _raw_type tests (strict=False)
        ("object", {}, False, True),
        ("array", [], False, True),
        ("null", None, False, True),
        ("string", "test", False, True),
        ("string", {}, False, False),
        ("string", [], False, False),
        ("number", 123, False, True),
        ("number", "123", False, True),
        ("number", True, False, False),
        ("integer", 123, False, True),
        ("integer", "123", False, True),
        ("integer", True, False, False),
        ("boolean", True, False, True),
        ("boolean", "true", False, True),
        ("boolean", "false", False, True),
        # _raw_type_strict tests (strict=True)
        ("object", {}, True, True),
        ("string", "test", True, True),
        ("number", 123, True, True),
        ("number", "123", True, False),
        ("integer", 123, True, True),
        ("integer", "123", True, False),
        ("boolean", True, True, True),
        ("boolean", "true", True, False),
        # Edge cases for number type
        ("number", "not-a-number", False, False),  # Will cause ValueError in float()
        ("number", {"key": "value"}, False, False),  # Will cause TypeError in float()
        # Edge cases for integer type
        ("integer", "not-an-integer", False, False),  # Will cause ValueError in int()
        ("integer", {"key": "value"}, False, False),  # Will cause TypeError in int()
        # Edge case for boolean type
        ("boolean", "not-a-boolean", False, False),  # Not in BOOLEAN_STRINGS
        # Additional edge cases
        ("unknown-type", "test", False, False),  # Unknown type
        ("null", "null", False, False),  # String "null" is not None
    ],
)
def test_raw_type_functions(validator, type_name, instance, strict, expected_result):
    if strict:
        assert _raw_type_strict(validator, type_name, instance) == expected_result
    else:
        assert _raw_type(validator, type_name, instance) == expected_result


@pytest.mark.parametrize(
    "instance,type_value,strict_types,expected",
    [
        # Test with strict_types=True
        (
            "123",
            "number",
            True,
            [
                ValidationError(
                    "'123' is not of type 'number'",
                    path=deque([]),
                )
            ],
        ),
        # Test with strict_types=False
        (
            "123",
            "number",
            False,
            [],
        ),
        # Test with multiple types
        (
            "test",
            ["string", "number"],
            True,
            [],
        ),
        # Test with invalid type
        (
            123,
            "string",
            True,
            [
                ValidationError(
                    "123 is not of type 'string'",
                    path=deque([]),
                )
            ],
        ),
        # Test with complex type combinations
        (
            {"key": "value"},
            ["string", "number", "boolean", "object"],
            True,
            [],
        ),
        # Test with non-matching complex types
        (
            {"key": "value"},
            ["string", "number", "boolean"],
            True,
            [
                ValidationError(
                    "{'key': 'value'} is not of type 'string', 'number', 'boolean'",
                    path=deque([]),
                )
            ],
        ),
        # Test with null instance
        (
            None,
            "null",
            True,
            [],
        ),
        # Test with boolean instance and string type
        (
            True,
            "string",
            False,
            [],  # With strict_types=False, True can be considered a string
        ),
    ],
)
def test_cfn_type_function(instance, type_value, strict_types, expected, validator):
    validator = validator.evolve(
        context=validator.context.evolve(strict_types=strict_types)
    )
    errs = list(cfn_type(validator, type_value, instance, {}))
    assert errs == expected
