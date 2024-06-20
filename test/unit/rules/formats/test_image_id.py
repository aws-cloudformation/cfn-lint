"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.rules.formats.ImageId import ImageId


@pytest.fixture(scope="module")
def rule():
    rule = ImageId()
    yield rule


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid image id",
            "ami-abcd1234",
            deque([]),
            True,
        ),
        (
            "Valid image id long",
            "ami-abcdefa1234567890",
            deque([]),
            True,
        ),
        (
            "Valid image id using ssm",
            "resolve:ssm:/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id",
            deque(
                [
                    "Resources",
                    "AWS::EC2::LaunchTemplate",
                    "Properties",
                    "LaunchTemplateData",
                    "ImageId",
                ]
            ),
            True,
        ),
        (
            "Invalid image id using ssm",
            "resolve:ssm:/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id",
            deque([]),
            False,
        ),
        (
            "Valid image id in exception",
            "ami-abcd1234",
            deque(
                [
                    "Resources",
                    "AWS::EC2::LaunchTemplate",
                    "Properties",
                    "LaunchTemplateData",
                    "ImageId",
                ]
            ),
            True,
        ),
        (
            "Valid type",
            [],
            deque([]),
            True,
        ),
        ("Invalid image ID", "ami-abc", deque([]), False),
    ],
)
def test_validate(name, instance, path, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque([]),
                cfn_path=path,
            ),
        )
    )

    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
