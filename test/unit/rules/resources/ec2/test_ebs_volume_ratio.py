"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.api import lint


@pytest.mark.parametrize(
    "size,iops,expected_error",
    [
        (1, 2999, False),  # EC2 accepts a value below the gp3 baseline
        (1, 3000, False),
        (1, 16000, True),
        (6, 3000, False),
        (6, 3001, True),
        (100, 50000, False),
        (100, 50001, True),
        (160, 80000, False),
        (200, 80000, False),
    ],
)
def test_ec2_gp3_volume_size_based_iops(size, iops, expected_error):
    template = (
        'AWSTemplateFormatVersion: "2010-09-09"\n'
        "Resources:\n"
        "  TestVolume:\n"
        "    Type: AWS::EC2::Volume\n"
        "    Properties:\n"
        "      AvailabilityZone: us-east-1a\n"
        "      VolumeType: gp3\n"
        f"      Size: {size}\n"
        f"      Iops: {iops}\n"
    )

    ratio_errors = [
        match
        for match in lint(template, regions=["us-east-1"])
        if match.rule.id == "E3671" and "size-based limit" in match.message
    ]

    assert bool(ratio_errors) == expected_error, ratio_errors
