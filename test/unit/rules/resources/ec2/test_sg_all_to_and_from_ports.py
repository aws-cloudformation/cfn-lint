"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.SecurityGroupAllToAndFromPorts import (
    SecurityGroupAllToAndFromPorts,
)


@pytest.fixture(scope="module")
def rule():
    rule = SecurityGroupAllToAndFromPorts()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "ToPort": -1,
                "FromPort": -1,
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "ToPort": "-1",
                "FromPort": -1,
            },
            [],
        ),
        (
            {
                "IpProtocol": 1,
                "ToPort": -1,
                "FromPort": 8,
            },
            [],
        ),
        (
            {
                "ToPort": -1,
            },
            [
                ValidationError(
                    ("Both ['FromPort', 'ToPort'] must " "be -1 when one is -1"),
                    rule=SecurityGroupAllToAndFromPorts(),
                    path=deque([]),
                    validator="required",
                    validator_value=["FromPort"],
                    instance={"ToPort": -1},
                    schema={
                        "properties": {"FromPort": {"enum": [-1, "-1"]}},
                        "required": ["FromPort"],
                    },
                    schema_path=deque(["else", "allOf", 0, "then", "required"]),
                )
            ],
        ),
        (
            {
                "FromPort": -1,
            },
            [
                ValidationError(
                    ("Both ['FromPort', 'ToPort'] must " "be -1 when one is -1"),
                    rule=SecurityGroupAllToAndFromPorts(),
                    path=deque([]),
                    validator="required",
                    validator_value=["ToPort"],
                    instance={"FromPort": -1},
                    schema={
                        "properties": {"ToPort": {"enum": [-1, "-1"]}},
                        "required": ["ToPort"],
                    },
                    schema_path=deque(["else", "allOf", 1, "then", "required"]),
                )
            ],
        ),
        (
            {
                "ToPort": -1,
                "FromPort": 5,
            },
            [
                ValidationError(
                    ("Both ['FromPort', 'ToPort'] must " "be -1 when one is -1"),
                    rule=SecurityGroupAllToAndFromPorts(),
                    path=deque(["FromPort"]),
                    validator="enum",
                    validator_value=[-1, "-1"],
                    instance=5,
                    schema={"enum": [-1, "-1"]},
                    schema_path=deque(
                        ["else", "allOf", 0, "then", "properties", "FromPort", "enum"]
                    ),
                )
            ],
        ),
        (
            {
                "ToPort": 5,
                "FromPort": -1,
            },
            [
                ValidationError(
                    ("Both ['FromPort', 'ToPort'] must " "be -1 when one is -1"),
                    rule=SecurityGroupAllToAndFromPorts(),
                    path=deque(["ToPort"]),
                    validator="enum",
                    validator_value=[-1, "-1"],
                    instance=5,
                    schema={"enum": [-1, "-1"]},
                    schema_path=deque(
                        ["else", "allOf", 1, "then", "properties", "ToPort", "enum"]
                    ),
                )
            ],
        ),
        (
            {
                "IpProtocol": "icmp",
                "ToPort": 8,
                "FromPort": -1,
            },
            [
                ValidationError(
                    ("Both ['FromPort', 'ToPort'] must " "be -1 when one is -1"),
                    rule=SecurityGroupAllToAndFromPorts(),
                    path=deque(["ToPort"]),
                    validator="enum",
                    validator_value=[-1, "-1"],
                    instance=5,
                    schema={"enum": [-1, "-1"]},
                    schema_path=deque(["then", "then", "properties", "ToPort", "enum"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
