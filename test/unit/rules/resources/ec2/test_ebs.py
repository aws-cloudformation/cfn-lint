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
                    (
                        "'Iops' is a required property when 'VolumeType' "
                        "has a value of 'io1'"
                    ),
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
            [
                ValidationError(
                    (
                        "Additional properties are not allowed (Iops) was "
                        "unexpected when 'VolumeType' has a value of 'standard'"
                    ),
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator=None,
                    validator_value=False,
                    instance=3000,
                    schema=False,
                    schema_path=deque(["allOf", 1, "then", "properties", "Iops"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
