"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint import lint


@pytest.mark.parametrize(
    "volume_properties,expected",
    [
        ("Size: 1\n      Iops: 16000", ["E3662"]),
        ("Size: 1\n      Iops: 3000", []),
    ],
)
def test_ebs_volume_iops_ratio(volume_properties, expected):
    template = f"""
Resources:
  Volume:
    Type: AWS::EC2::Volume
    Properties:
      AvailabilityZone: us-east-1a
      VolumeType: gp3
      {volume_properties}
"""
    matches = [
        match
        for match in lint(template, regions=["us-east-1"])
        if match.rule.id in {"E3662", "W3662"}
    ]

    assert [match.rule.id for match in matches] == expected
    if matches:
        assert matches[0].path == ["Resources", "Volume", "Properties", "Iops"]


def test_launch_template_iops_ratio_is_warning():
    template = """
Resources:
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        BlockDeviceMappings:
          - DeviceName: /dev/sdf
            Ebs:
              VolumeType: gp3
              VolumeSize: 1
              Iops: 16000
"""
    matches = [
        match
        for match in lint(template, regions=["us-east-1"])
        if match.rule.id in {"E3662", "W3662"}
    ]

    assert [match.rule.id for match in matches] == ["W3662"]
    assert matches[0].path == [
        "Resources",
        "LaunchTemplate",
        "Properties",
        "LaunchTemplateData",
        "BlockDeviceMappings",
        0,
        "Ebs",
        "Iops",
    ]
