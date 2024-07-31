"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Path
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._filter import FunctionFilter


@pytest.fixture(scope="module")
def filter():
    filter = FunctionFilter()
    yield filter


@pytest.mark.parametrize(
    "name,instance,schema,path,functions,expected",
    [
        (
            "Don't validate dynamic references inside of function",
            "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}",
            {"enum": "Foo"},
            deque(["Foo", "Test", "Fn::Sub"]),
            [],
            [],
        ),
        (
            "Validate dynamic references",
            "{{resolve:ssm:secret}}",
            {"enum": "Foo"},
            deque(["Foo", "Test"]),
            [],
            [
                ("{{resolve:ssm:secret}}", {"dynamicReference": {"enum": "Foo"}}),
            ],
        ),
        (
            "Lack of functions returns the schema and instance",
            {
                "Foo": {"Ref": "AWS::NoValue"},
            },
            {"required": ["Foo"]},
            deque([]),
            [],
            [
                (
                    {
                        "Foo": {"Ref": "AWS::NoValue"},
                    },
                    {"required": ["Foo"]},
                ),
            ],
        ),
        (
            "Filtered schemas",
            {
                "Foo": {"Ref": "AWS::NoValue"},
            },
            {"required": ["Foo"]},
            deque([]),
            ["Ref", "Fn::If"],
            [
                (
                    {},
                    {"required": ["Foo"]},
                ),
                ({"Foo": {"Ref": "AWS::NoValue"}}, {"cfnLint": [""]}),
            ],
        ),
    ],
)
def test_filter(name, instance, schema, path, functions, expected, filter):
    validator = CfnTemplateValidator(
        context=Context(
            regions=["us-east-1"],
            path=Path(path),
            functions=functions,
        ),
        schema=schema,
    )
    results = list(filter.filter(validator, instance, schema))

    assert len(results) == len(expected), f"For test {name} got {len(results)} results"

    for result, (exp_instance, exp_schema) in zip(results, expected):
        assert result[0] == exp_instance, f"For test {name} got {result.instance!r}"
        assert result[1] == exp_schema, f"For test {name} got {result.schema!r}"
