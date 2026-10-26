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
            {
                "VolumeType": "gp3",
                "Iops": 20000,
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
                "Iops": 80001,
            },
            [
                ValidationError(
                    "80001 is greater than the maximum of 80000",
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator="maximum",
                    validator_value=80000,
                    instance=80001,
                    schema={"minimum": 3000, "maximum": 80000},
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
        # gp3 below 3000 is clamped up by EC2, not rejected, so the floor
        # on this path is 100 (the value the service itself reports)
        (
            {
                "VolumeType": "gp3",
                "Iops": 2999,
            },
            [],
        ),
        (
            {
                "VolumeType": "gp3",
                "Iops": 100,
            },
            [],
        ),
        (
            {
                "VolumeType": "gp3",
            },
            [],
        ),
        (
            {
                "VolumeType": "gp3",
                "Iops": {"Ref": "MyParameter"},
            },
            [],
        ),
        (
            {
                "VolumeType": "gp3",
                "Iops": 99,
            },
            [
                ValidationError(
                    "99 is less than the minimum of 100",
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator="minimum",
                    validator_value=100,
                    instance=99,
                    schema={"minimum": 100, "maximum": 80000},
                    schema_path=deque(
                        ["allOf", 2, "then", "properties", "Iops", "minimum"]
                    ),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "VolumeType": "gp3",
                "Iops": 16000,
            },
            [],
        ),
        (
            {
                "VolumeType": "gp3",
                "Iops": 20000,
            },
            [
                ValidationError(
                    "20000 is greater than the maximum of 16000",
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator="maximum",
                    validator_value=16000,
                    instance=20000,
                    schema={"minimum": 3000, "maximum": 16000},
                    schema_path=deque(
                        ["allOf", 2, "then", "properties", "Iops", "maximum"]
                    ),
                )
            ],
        ),
        # Auto Scaling genuinely rejects gp3 below 3000 with
        # "GP3 volumes must have between 3000 and 16000 IOPS.", so this
        # path keeps the 3000 floor the EC2 instance path drops
        (
            {
                "VolumeType": "gp3",
                "Iops": 2999,
            },
            [
                ValidationError(
                    "2999 is less than the minimum of 3000",
                    rule=Ebs(),
                    path=deque(["Iops"]),
                    validator="minimum",
                    validator_value=3000,
                    instance=2999,
                    schema={"minimum": 3000, "maximum": 16000},
                    schema_path=deque(
                        ["allOf", 2, "then", "properties", "Iops", "minimum"]
                    ),
                )
            ],
        ),
    ],
)
def test_launch_configuration(instance, expected, rule, validator):
    keyword = (
        "Resources/AWS::AutoScaling::LaunchConfiguration"
        "/Properties/BlockDeviceMappings/*/Ebs"
    )
    errs = list(rule.validate(validator, keyword, instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
