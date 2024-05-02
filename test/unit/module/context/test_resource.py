"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Resource, _init_resources


@pytest.mark.parametrize(
    "name,instance,expected_ref",
    [
        ("Valid resource", {"Type": "AWS::S3::Bucket"}, []),
    ],
)
def test_resource(name, instance, expected_ref):
    context = Context(["us-east-1"])
    parameter = Resource(instance)

    assert expected_ref == list(
        parameter.ref(context)
    ), f"{name!r} test got {list(parameter.ref(context))}"


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
