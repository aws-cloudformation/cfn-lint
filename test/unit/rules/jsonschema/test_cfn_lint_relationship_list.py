"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.rules.jsonschema.CfnLintRelationship import CfnLintRelationship


@pytest.fixture
def rule():
    return CfnLintRelationship(
        keywords=[], relationship="Resources/AWS::EC2::Instance/Properties/Foo/*/Bar"
    )


@pytest.fixture
def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {
            "One": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "Foo": [
                        {
                            "Bar": "One",
                        },
                        {
                            "Bar": "Two",
                        },
                    ]
                },
            },
            "ParentOne": {
                "Type": "AWS::EC2::Instance",
                "Properties": {"ImageId": {"Fn::GetAtt": ["One", "ImageId"]}},
            },
        },
    }


@pytest.mark.parametrize(
    "name,path,status,expected",
    [
        (
            "One",
            deque(["Resources", "ParentOne", "Properties", "ImageId"]),
            {},
            [
                ("One", {}),
                ("Two", {}),
            ],
        ),
    ],
)
def test_get_relationships(name, path, status, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(path),
            conditions=validator.context.conditions.evolve(
                status=status,
            ),
        ),
    )
    results = list(rule.get_relationship(validator))
    assert len(results) == len(expected), f"Test {name!r} got {len(results)!r}"
    for result, exp in zip(results, expected):
        assert result[0] == exp[0], f"Test {name!r} got {result[0]!r}"
        assert (
            result[1].context.conditions.status == exp[1]
        ), f"Test {name!r} got {result[1].context.conditions.status!r}"
