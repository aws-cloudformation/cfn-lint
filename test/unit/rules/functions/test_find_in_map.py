"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest.mock import MagicMock

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.context import Resource, Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.FindInMap import FindInMap
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = FindInMap()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Resources": {"MyResource": Resource({"Type": "AWS::SSM::Parameter"})},
            "Mappings": {"A": {"B": {"C": "Value"}}},
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,schema,context_evolve,ref_mock_values,expected",
    [
        (
            "Valid Fn::FindInMap",
            {"Fn::FindInMap": ["A", "B", "C"]},
            {"type": "string"},
            {},
            [],
            [],
        ),
        (
            "Invalid Fn::FindInMap too long",
            {"Fn::FindInMap": ["foo", "bar", "key", "key2"]},
            {"type": "string"},
            {},
            [],
            [
                ValidationError(
                    "['foo', 'bar', 'key', 'key2'] is too long (3)",
                    path=deque(["Fn::FindInMap"]),
                    schema_path=deque(["maxItems"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with wrong type",
            {"Fn::FindInMap": {"foo": "bar"}},
            {"type": "string"},
            {},
            [],
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'array'",
                    path=deque(["Fn::FindInMap"]),
                    schema_path=deque(["type"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with wrong function",
            {"Fn::FindInMap": [{"Fn::GetAtt": "MyResource.Arn"}, "foo", "bar"]},
            {"type": "string"},
            {},
            [],
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyResource.Arn'} is not of type 'string'",
                    path=deque(["Fn::FindInMap", 0]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Valid Fn::FindInMap",
            {"Fn::FindInMap": ["A", "B", "C", {"DefaultValue": "D"}]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
            [],
        ),
        (
            "Invalid Fn::FindInMap options not of type object",
            {"Fn::FindInMap": ["A", "B", "C", []]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap default keyword doesn't exist",
            {"Fn::FindInMap": ["A", "B", "C", {}]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
            [
                ValidationError(
                    "'DefaultValue' is a required property",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(["fn_items", "required"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap with a Ref to a resource",
            {"Fn::FindInMap": ["A", {"Ref": "MyResource"}, "C"]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [ValidationError("Foo")],
            [
                ValidationError(
                    "Foo",
                    path=deque(["Fn::FindInMap", 1]),
                    schema_path=deque(["fn_items", "ref"]),
                    validator="ref",
                ),
            ],
        ),
    ],
)
def test_validate(
    name,
    instance,
    schema,
    ref_mock_values,
    context_evolve,
    expected,
    rule,
    context,
    cfn,
):
    context = context.evolve(**context_evolve)
    ref_mock = MagicMock()
    ref_mock.return_value = iter(ref_mock_values)
    validator = CfnTemplateValidator({}).extend(validators={"ref": ref_mock})(
        context=context, cfn=cfn
    )
    errs = list(rule.fn_findinmap(validator, schema, instance, {}))
    assert ref_mock.call_count == len(ref_mock_values)
    assert errs == expected, f"Test {name!r} got {errs!r}"
