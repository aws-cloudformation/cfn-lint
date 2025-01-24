"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.context import Resource, _init_resources


@pytest.mark.parametrize(
    "name,instance,expected_ref",
    [
        (
            "Valid resource",
            {"Type": "AWS::EC2::VPC"},
            {"format": "AWS::EC2::VPC.Id", "type": "string"},
        ),
    ],
)
def test_resource(name, instance, expected_ref):
    region = "us-east-1"
    resource = Resource(instance)

    assert expected_ref == resource.ref(
        region
    ), f"{name!r} test got {resource.ref(region)}"


@pytest.mark.parametrize(
    "name,instance",
    [
        ("Invalid Type", {"Type": {}}),
    ],
)
def test_errors(name, instance):
    with pytest.raises(ValueError):
        Resource(instance)


def test_resources():
    with pytest.raises(ValueError):
        _init_resources([])
