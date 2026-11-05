"""Regression tests for E3671 on standalone EC2 EBS volumes."""

import pytest

from cfnlint.api import lint


@pytest.mark.parametrize(
    "volume_type,iops,should_report",
    [
        ("gp3", 80000, False),
        ("gp3", 80001, True),
        ("gp3", 999999, True),
        ("gp3", 2999, False),
        ("gp3", None, False),
        ("io1", 64000, False),
        ("io1", 64001, True),
        ("io1", None, True),
        ("io2", 256000, False),
        ("io2", 256001, True),
        ("io2", None, True),
    ],
)
def test_ec2_volume_iops(volume_type, iops, should_report):
    iops_line = f"      Iops: {iops}\n" if iops is not None else ""

    template = (
        'AWSTemplateFormatVersion: "2010-09-09"\n'
        "Resources:\n"
        "  TestVolume:\n"
        "    Type: AWS::EC2::Volume\n"
        "    Properties:\n"
        "      AvailabilityZone: us-east-1a\n"
        f"      VolumeType: {volume_type}\n"
        "      Size: 2000\n"
        f"{iops_line}"
    )

    errors = [
        match
        for match in lint(template, regions=["us-east-1"])
        if match.rule.id == "E3671"
    ]

    assert bool(errors) == should_report, errors
