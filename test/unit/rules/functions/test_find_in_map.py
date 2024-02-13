"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from test.unit.rules import BaseRuleTestCase

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Map
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.FindInMap import FindInMap


class TestRulesFindInMap(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesFindInMap, self).setUp()
        self.collection.register(FindInMap())
        self.success_templates = [
            "test/fixtures/templates/good/functions_findinmap.yaml",
            "test/fixtures/templates/good/functions_findinmap_enhanced.yaml",
            "test/fixtures/templates/good/functions_findinmap_default_value.yaml",
        ]


@pytest.fixture(scope="module")
def rule():
    rule = FindInMap()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        mappings={
            "A": Map({"B": {"C": "Value"}}),
        },
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::FindInMap",
            {"Fn::FindInMap": ["A", "B", "C"]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::FindInMap too long",
            {"Fn::FindInMap": ["foo", "bar", "key", "key2"]},
            {"type": "string"},
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
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyResource.Arn'} is not of type 'string'",
                    path=deque(["Fn::FindInMap", 0]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_findinmap(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
