"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.EbsIopsAdjusted import EbsIopsAdjusted


@pytest.fixture(scope="module")
def rule():
    rule = EbsIopsAdjusted()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        # the property is absent
        (
            {"VolumeType": "gp3", "VolumeSize": 100},
            [],
        ),
        # at the baseline and above it nothing is adjusted
        (
            {"VolumeType": "gp3", "Iops": 3000},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": 80000},
            [],
        ),
        # below the gp3 minimum the volume is rejected, not adjusted,
        # and E3671 reports that
        (
            {"VolumeType": "gp3", "Iops": 99},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": 50},
            [],
        ),
        # a sibling 'VolumeType' that is not gp3 has no gp3 baseline
        (
            {"VolumeType": "io1", "Iops": 2999},
            [],
        ),
        (
            {"VolumeType": "io2", "Iops": 2999},
            [],
        ),
        (
            {"VolumeType": "gp2", "Iops": 2999},
            [],
        ),
        (
            {"Iops": 2999},
            [],
        ),
        # unresolved functions on the value
        (
            {"VolumeType": "gp3", "Iops": {"Ref": "MyParameter"}},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": {"Fn::GetAtt": "MyResource.Iops"}},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": {"Fn::If": ["IsUsEast1", 2999, 3000]}},
            [],
        ),
        # an unresolved function on the sibling 'VolumeType'
        (
            {"VolumeType": {"Ref": "MyParameter"}, "Iops": 2999},
            [],
        ),
        # an unresolved function on the enclosing 'Ebs' object
        (
            {
                "Fn::If": [
                    "IsUsEast1",
                    {"VolumeType": "gp3", "Iops": 2999},
                    {"VolumeType": "gp3", "Iops": 3000},
                ]
            },
            [],
        ),
        # non scalars
        (
            [],
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": []},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": "three thousand"},
            [],
        ),
        # the value is adjusted
        (
            {"VolumeType": "gp3", "Iops": 2999},
            [
                ValidationError(
                    "'Iops' of 2999 is raised to 3000 for 'VolumeType' 'gp3'",
                    path=deque(["Iops"]),
                )
            ],
        ),
        (
            {"VolumeType": "gp3", "Iops": 100},
            [
                ValidationError(
                    "'Iops' of 100 is raised to 3000 for 'VolumeType' 'gp3'",
                    path=deque(["Iops"]),
                )
            ],
        ),
        # CloudFormation converts a string to the number it represents
        (
            {"VolumeType": "gp3", "Iops": "2999"},
            [
                ValidationError(
                    "'Iops' of 2999 is raised to 3000 for 'VolumeType' 'gp3'",
                    path=deque(["Iops"]),
                )
            ],
        ),
        (
            {"VolumeType": "GP3", "Iops": 2999},
            [
                ValidationError(
                    "'Iops' of 2999 is raised to 3000 for 'VolumeType' 'GP3'",
                    path=deque(["Iops"]),
                )
            ],
        ),
    ],
)
def test_ebs_iops_adjusted(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
