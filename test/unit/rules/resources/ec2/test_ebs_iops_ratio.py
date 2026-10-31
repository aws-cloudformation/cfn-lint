"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.EbsIopsRatio import (
    EbsIopsRatio,
    EbsIopsRatioWarning,
)

_VOLUME = "Resources/AWS::EC2::Volume/Properties"
_INSTANCE = "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs"
_LAUNCH_CONFIG = (
    "Resources/AWS::AutoScaling::LaunchConfiguration"
    "/Properties/BlockDeviceMappings/*/Ebs"
)
_LAUNCH_TEMPLATE = (
    "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData"
    "/BlockDeviceMappings/*/Ebs"
)
_SPOT_FLEET = (
    "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData"
    "/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs"
)


@pytest.mark.parametrize(
    "keyword,instance,expected_message",
    [
        (
            _VOLUME,
            {"VolumeType": "gp3", "Size": 1, "Iops": 16000},
            "16000 IOPS exceeds the gp3 maximum of 3000 for a 1 GiB "
            "volume (ratio 500:1)",
        ),
        (
            _VOLUME,
            {"VolumeType": "io1", "Size": 10, "Iops": 501},
            "501 IOPS exceeds the io1 maximum of 500 for a 10 GiB volume (ratio 50:1)",
        ),
        (
            _VOLUME,
            {"VolumeType": "io2", "Size": 10, "Iops": 10001},
            "10001 IOPS exceeds the io2 maximum of 10000 for a 10 GiB "
            "volume (ratio 1000:1)",
        ),
        (
            _INSTANCE,
            {"VolumeType": "gp3", "VolumeSize": 1, "Iops": 16000},
            "16000 IOPS exceeds the gp3 maximum of 3000 for a 1 GiB "
            "volume (ratio 500:1)",
        ),
        (
            _LAUNCH_CONFIG,
            {"VolumeType": "io1", "VolumeSize": 10, "Iops": 501},
            "501 IOPS exceeds the io1 maximum of 500 for a 10 GiB volume (ratio 50:1)",
        ),
    ],
)
def test_ebs_iops_ratio_errors(keyword, instance, expected_message, validator):
    errors = list(EbsIopsRatio().validate(validator, keyword, instance, {}))

    assert errors == [ValidationError(expected_message, path=deque(["Iops"]))]


@pytest.mark.parametrize(
    "keyword,instance",
    [
        # gp3 has a 3000-IOPS baseline even for volumes below 6 GiB.
        (_VOLUME, {"VolumeType": "gp3", "Size": 1, "Iops": 3000}),
        (_VOLUME, {"VolumeType": "gp3", "Size": 6, "Iops": 3000}),
        (_VOLUME, {"VolumeType": "gp3", "Size": 160, "Iops": 80000}),
        (_VOLUME, {"VolumeType": "io1", "Size": 10, "Iops": 500}),
        (_VOLUME, {"VolumeType": "io2", "Size": 10, "Iops": 10000}),
        (_VOLUME, {"VolumeType": "gp2", "Size": 1, "Iops": 16000}),
        (_VOLUME, {"Size": 1, "Iops": 16000}),
        (_VOLUME, {"VolumeType": "gp3", "Size": 1}),
        (_VOLUME, {"VolumeType": "gp3", "Size": {"Ref": "Size"}, "Iops": 16000}),
        (_VOLUME, {"VolumeType": "gp3", "Size": 1, "Iops": {"Ref": "Iops"}}),
        (_VOLUME, {"VolumeType": {"Ref": "Type"}, "Size": 1, "Iops": 16000}),
        (_VOLUME, {"VolumeType": "gp3", "Size": True, "Iops": 16000}),
        (_VOLUME, {"VolumeType": "gp3", "Size": 1, "Iops": True}),
        (_VOLUME, {"VolumeType": "gp3", "Size": 0, "Iops": 16000}),
        (_VOLUME, []),
        # A missing block device size can be inherited from the image/snapshot.
        (_INSTANCE, {"VolumeType": "gp3", "Iops": 16000}),
    ],
)
def test_ebs_iops_ratio_valid_or_unresolved(keyword, instance, validator):
    assert list(EbsIopsRatio().validate(validator, keyword, instance, {})) == []


@pytest.mark.parametrize("keyword", [_LAUNCH_TEMPLATE, _SPOT_FLEET])
def test_ebs_iops_ratio_warning(keyword, validator):
    rule = EbsIopsRatioWarning()
    instance = {"VolumeType": "io2", "VolumeSize": 10, "Iops": 10001}

    assert rule.id == "W3662"
    assert list(rule.validate(validator, keyword, instance, {})) == [
        ValidationError(
            "10001 IOPS exceeds the io2 maximum of 10000 for a 10 GiB "
            "volume (ratio 1000:1)",
            path=deque(["Iops"]),
        )
    ]


@pytest.mark.parametrize("keyword", [_LAUNCH_TEMPLATE, _SPOT_FLEET])
def test_ebs_iops_ratio_warning_boundary(keyword, validator):
    assert (
        list(
            EbsIopsRatioWarning().validate(
                validator,
                keyword,
                {"VolumeType": "io2", "VolumeSize": 10, "Iops": 10000},
                {},
            )
        )
        == []
    )
