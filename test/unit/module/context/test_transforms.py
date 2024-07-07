"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.context import Transforms


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        ("Valid transforms", "AWS::LanguageExtensions", True),
        (
            "Valid transforms lists",
            ["AWS::LanguageExtensions", {"Name": "Include"}],
            True,
        ),
        ("Valid transforms lists", None, False),
        ("Valid transforms lists", "", False),
    ],
)
def test_transforms(name, instance, expected):
    transforms = Transforms(instance)

    assert (
        expected == transforms.has_language_extensions_transform()
    ), f"{name!r} test got {transforms.has_language_extensions_transform()}"
