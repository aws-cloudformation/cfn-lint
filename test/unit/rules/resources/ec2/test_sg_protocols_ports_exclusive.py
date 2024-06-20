"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.SecurityGroupProtocolsAndPortsExclusive import (
    SecurityGroupProtocolsAndPortsExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = SecurityGroupProtocolsAndPortsExclusive()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "IpProtocol": -1,
            },
            [],
        ),
        (
            {
                "IpProtocol": 9,
            },
            [],
        ),
        (
            {
                "IpProtocol": "TCP",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "IpProtocol": -1,
                "FromPort": -1,
                "ToPort": -1,
            },
            [
                ValidationError(
                    (
                        "['FromPort', 'ToPort'] are ignored when using "
                        "'IpProtocol' value -1"
                    ),
                    rule=SecurityGroupProtocolsAndPortsExclusive(),
                    path=deque(["FromPort"]),
                    instance=-1,
                    schema=False,
                    validator=None,
                    validator_value=None,
                    schema_path=deque(["then", "properties", "FromPort"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
