"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.EbsIopsAdjusted import EbsIopsAdjusted

_not = {"exclusiveMaximum": 3000, "minimum": 100, "type": "number"}


def _expected(iops):
    return [
        ValidationError(
            f"'Iops' of {iops} is raised to 3000 for 'VolumeType' 'gp3'",
            rule=EbsIopsAdjusted(),
            path=deque(["Iops"]),
            validator="not",
            validator_value=_not,
            instance=iops,
            schema={"not": _not},
            schema_path=deque(["then", "properties", "Iops", "not"]),
        )
    ]


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
        # below the gp3 minimum the volume is rejected rather than
        # adjusted, and E3671 reports that
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
        # 'VolumeType' is a case sensitive enum, so a mismatched case is
        # already an E3030 and must not also draw this warning
        (
            {"VolumeType": "GP3", "Iops": 2999},
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
            {"VolumeType": "gp3", "Iops": {}},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": "three thousand"},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": None},
            [],
        ),
        (
            {"VolumeType": "gp3", "Iops": True},
            [],
        ),
        # the value is adjusted
        (
            {"VolumeType": "gp3", "Iops": 2999},
            _expected(2999),
        ),
        (
            {"VolumeType": "gp3", "Iops": 100},
            _expected(100),
        ),
        (
            {"VolumeType": "gp3", "Iops": 2999, "VolumeSize": 100},
            _expected(2999),
        ),
    ],
)
def test_ebs_iops_adjusted(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
