"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.Ebs import Ebs


@pytest.fixture(scope="module")
def rule():
    rule = Ebs()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "VolumeType": "gp3",
                "Iops": 3000,
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "VolumeType": "io1",
                "Iops": 3000,
            },
            [],
        ),
        (
            {
                "VolumeType": "standard",
            },
            [],
        ),
        (
            {
                "VolumeType": "io1",
            },
            [
                ValidationError(
                    "'Iops' is a required property when 'VolumeType' "
                    "has a value of 'io1'",
                    rule=Ebs(),
                    path=deque([]),
                    validator="required",
                    validator_value=["Iops"],
                    instance={"VolumeType": "io1"},
                    schema={"required": ["Iops"]},
                    schema_path=deque(["allOf", 0, "then", "required"]),
                )
            ],
        ),
        (
            {
                "VolumeType": "standard",
                "Iops": 3000,
            },
            [],
        ),
        (
            {
                "VolumeType": "gp3",
                "Iops": 64000,
            },
            [
                ValidationError(
                    "64000 is greater than the maximum of 16000",
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator="maximum",
                    validator_value=16000,
                    instance=64000,
                    schema={"minimum": 3000, "maximum": 16000},
                    schema_path=deque(
                        ["allOf", 2, "then", "properties", "Iops", "maximum"]
                    ),
                )
            ],
        ),
        (
            {
                "VolumeType": "io1",
                "Iops": 50,
            },
            [
                ValidationError(
                    "50 is less than the minimum of 100",
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator="minimum",
                    validator_value=100,
                    instance=50,
                    schema={"minimum": 100, "maximum": 64000},
                    schema_path=deque(
                        ["allOf", 0, "then", "properties", "Iops", "minimum"]
                    ),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
