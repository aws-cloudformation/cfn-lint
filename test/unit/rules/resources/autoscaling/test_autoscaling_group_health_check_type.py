"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.autoscaling.AutoScalingGroupHealthCheckType import (
    AutoScalingGroupHealthCheckType,
)


@pytest.fixture(scope="module")
def rule():
    rule = AutoScalingGroupHealthCheckType()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        ("EC2", []),
        ("ELB", []),
        ("ELB,EBS", []),
        ("ELB,EBS,VPC_LATTICE", []),
        (
            "EC2,ELB",
            [
                ValidationError(
                    "EC2 cannot be combined with other health check types. "
                    "Got 'EC2,ELB'"
                ),
            ],
        ),
        (
            "ELB,EC2,EBS",
            [
                ValidationError(
                    "EC2 cannot be combined with other health check types. "
                    "Got 'ELB,EC2,EBS'"
                ),
            ],
        ),
        ({"Ref": "Param"}, []),
        (123, []),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, None, instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
