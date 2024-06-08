"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.outputs.ImportValue import ImportValue


@pytest.fixture(scope="module")
def rule():
    rule = ImportValue()
    yield rule


@pytest.mark.parametrize(
    "name,instance,path,schema,expected",
    [
        (
            "Valid Fn::ImportValue",
            {"Fn::ImportValue": "Export"},
            {
                "path": ["Resources", "MyResource", "Properties", "BucketName"],
            },
            {"type": "string"},
            [],
        ),
        (
            "Short path",
            {"Fn::ImportValue": "Export"},
            {
                "path": ["Outputs"],
            },
            {"type": "object"},
            [],
        ),
        (
            "Invalid Fn::ImportValue in Output",
            {"Fn::ImportValue": "Export"},
            {
                "path": ["Outputs", "MyOutput", "Value"],
            },
            {"type": "string"},
            [
                ValidationError(
                    (
                        "The output value {'Fn::ImportValue': 'Export'} "
                        "is an import from another output"
                    ),
                    path=deque(["Fn::ImportValue"]),
                    rule=ImportValue(),
                )
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, path, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
