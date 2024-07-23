"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.conditions._equals import _equals_cmp_key


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid",
            [
                "A",
                "B",
                {"Ref": "A"},
                {"Ref": "B"},
                {"Key": "Value"},
                {"Fn::FindInMap": ["A", "B", "C"]},
                {"Fn::FindInMap": ["X", "Y", "Z"]},
            ],
            [
                "A",
                "B",
                {"Fn::FindInMap": ["X", "Y", "Z"]},
                {"Fn::FindInMap": ["A", "B", "C"]},
                {"Ref": "A"},
                {"Ref": "B"},
                {"Key": "Value"},
            ],
        ),
        (
            "Different order same results",
            [
                {"Fn::FindInMap": ["A", "B", "C"]},
                {"Fn::FindInMap": ["X", "Y", "Z"]},
                {"Ref": "B"},
                {"Ref": "A"},
                {"Key": "Value"},
                "B",
                "A",
            ],
            [
                "A",
                "B",
                {"Fn::FindInMap": ["X", "Y", "Z"]},
                {"Fn::FindInMap": ["A", "B", "C"]},
                {"Ref": "A"},
                {"Ref": "B"},
                {"Key": "Value"},
            ],
        ),
        (
            "Two Refs",
            [
                {"Ref": "B"},
                {"Ref": "A"},
            ],
            [
                {"Ref": "A"},
                {"Ref": "B"},
            ],
        ),
        (
            "Ref with non mapping",
            [
                {"Ref": "A"},
                {"Key": "Value"},
            ],
            [
                {"Ref": "A"},
                {"Key": "Value"},
            ],
        ),
        (
            "Ref with non mapping backwards",
            [
                {"Key": "Value"},
                {"Ref": "A"},
            ],
            [
                {"Ref": "A"},
                {"Key": "Value"},
            ],
        ),
        (
            "None functions",
            [
                {"Key": "Foo"},
                {"Key": "Bar"},
            ],
            [
                {"Key": "Foo"},
                {"Key": "Bar"},
            ],
        ),
    ],
)
def test_sorted(name, instance, expected):
    assert expected == sorted(
        instance, key=_equals_cmp_key
    ), f"{name} got {sorted(instance, key=_equals_cmp_key)}"
