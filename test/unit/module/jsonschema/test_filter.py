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
    "name,instance,schema,path,expected",
    [
        (
            "Don't validate dynamic references inside of function",
            "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}",
            {"enum": "Foo"},
            deque(["Foo", "Test", "Fn::Sub"]),
            [],
        ),
        (
            "Validate dynamic references",
            "{{resolve:ssm:secret}}",
            {"enum": "Foo"},
            deque(["Foo", "Test"]),
            [
                ("{{resolve:ssm:secret}}", {"dynamicReference": {"enum": "Foo"}}),
            ],
        ),
    ],
)
def test_filter(name, instance, schema, path, expected, filter):
    validator = CfnTemplateValidator(
        context=Context(regions=["us-east-1"], path=Path(path)),
        schema=schema,
    )
    results = list(filter.filter(validator, instance, schema))

    assert results == expected, f"For test {name} got {results!r}"
