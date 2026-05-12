"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.VpnGatewayType import VpnGatewayType


@pytest.fixture(scope="module")
def rule():
    rule = VpnGatewayType()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            "ipsec.1",
            [],
        ),
        (
            "other-value",
            [
                ValidationError(
                    "'other-value' is not one of ['ipsec.1']",
                    rule=VpnGatewayType(),
                    schema_path=deque(["enum"]),
                    validator="enum",
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
