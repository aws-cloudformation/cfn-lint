"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.EbsWarning import EbsWarning


@pytest.fixture(scope="module")
def rule():
    rule = EbsWarning()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "VolumeType": "gp3",
                "Iops": 20000,
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
                    rule=EbsWarning(),
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
                "VolumeType": "gp3",
                "Iops": 80001,
            },
            [
                ValidationError(
                    "80001 is greater than the maximum of 80000",
                    rule=EbsWarning(),
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
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
