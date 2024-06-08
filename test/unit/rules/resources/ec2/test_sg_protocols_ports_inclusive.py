"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.SecurityGroupProtocolsAndPortsInclusive import (
    SecurityGroupProtocolsAndPortsInclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = SecurityGroupProtocolsAndPortsInclusive()
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
            [],  # wrong type
            [],
        ),
        (
            {
                "IpProtocol": "tcp",
                "FromPort": 1,
            },
            [
                ValidationError(
                    (
                        "['FromPort', 'ToPort'] are required properties "
                        "when using 'IpProtocol' value 'tcp'"
                    ),
                    rule=SecurityGroupProtocolsAndPortsInclusive(),
                    path=deque([]),
                    instance={"IpProtocol": "tcp", "FromPort": 1},
                    validator="required",
                    validator_value=["FromPort", "ToPort"],
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
