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

        # Type with description (no constraints)
        assert not _schema_needs_resolution(
            {"type": "string", "description": "A simple string"}
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
        assert _schema_needs_resolution({"type": "number", "multipleOf": 5})

        # Value matching
        assert _schema_needs_resolution({"enum": ["a", "b", "c"]})
        assert _schema_needs_resolution({"const": "specific_value"})

        # Array constraints
        assert _schema_needs_resolution({"type": "array", "minItems": 1})
        assert _schema_needs_resolution({"type": "array", "maxItems": 5})
        assert _schema_needs_resolution({"type": "array", "uniqueItems": True})

        # Object constraints
        assert _schema_needs_resolution({"type": "object", "minProperties": 1})
        assert _schema_needs_resolution({"type": "object", "required": ["name"]})

    def test_schema_needs_resolution_edge_cases(self):
        """Test edge cases"""
        # Non-dict schemas
        assert not _schema_needs_resolution("string")
        assert not _schema_needs_resolution(None)
        assert not _schema_needs_resolution([])

        # Empty schema
        assert not _schema_needs_resolution({})
