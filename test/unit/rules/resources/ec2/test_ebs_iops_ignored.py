"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.EbsIopsIgnored import EbsIopsIgnored


@pytest.fixture(scope="module")
def rule():
    rule = EbsIopsIgnored()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"VolumeType": "gp3", "Iops": 3000},
            [],
        ),
        (
            {"VolumeType": "io1", "Iops": 3000},
            [],
        ),
        (
            {"VolumeType": "io2", "Iops": 3000},
            [],
        ),
        (
            {"VolumeType": "gp2", "VolumeSize": 100},
            [],
        ),
        (
            [],
            [],
        ),
        (
            {"VolumeType": "gp2", "Iops": 3000},
            [
                ValidationError(
                    "'Iops' is ignored when 'VolumeType' is 'gp2'",
                    path=deque(["Iops"]),
                )
            ],
        ),
        (
            {"VolumeType": "standard", "Iops": 100},
            [
                ValidationError(
                    "'Iops' is ignored when 'VolumeType' is 'standard'",
                    path=deque(["Iops"]),
                )
            ],
        ),
        (
            {"VolumeType": "st1", "Iops": 100},
            [
                ValidationError(
                    "'Iops' is ignored when 'VolumeType' is 'st1'",
                    path=deque(["Iops"]),
                )
            ],
        ),
    ],
)
def test_ebs_iops_ignored(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
