"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, Resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.functions._BaseFn import BaseFn


@pytest.fixture(scope="module")
def rule():
    rule = BaseFn()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={"MyResource": Resource({"Type": "Foo", "Properties": {"A": "B"}})},
        parameters={"MyParameter": Parameter({"Type": "String"})},
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,path,expected",
    [
        (
            "Valid for resources",
            deque(["Resources", "MyResource", "Properties", "A"]),
            "Resources/Foo/Properties/A",
        ),
        (
            "Valid for parameters",
            deque(["Parameters", "MyParameter", "Type"]),
            "Parameters/String/Type",
        ),
        (
            "Valid for outputs",
            deque(["Outputs", "MyOutput", "Value"]),
            "Outputs/MyOutput/Value",
        ),
        (
            "Valid for Resources",
            deque(
                [
                    "Resources",
                ]
            ),
            "Resources",
        ),
        ("Valid for Resources", deque(["Resources", "Metadata"]), "Resources/Metadata"),
        (
            "Non existent resource",
            deque(["Resources", "AnotherResource", "Properties", "A"]),
            "Resources/AnotherResource/Properties/A",
        ),
        (
            "Non existent Parameter",
            deque(["Parameters", "AnotherParameter", "Type"]),
            "Parameters/AnotherParameter/Type",
        ),
    ],
)
def test_get_keyword(name, path, expected, rule, validator):
    for p in path:
        validator = validator.evolve(context=validator.context.evolve(path=p))
    keyword = rule.get_keyword(validator)
    assert keyword == expected, f"Test {name!r} got {keyword!r}"
