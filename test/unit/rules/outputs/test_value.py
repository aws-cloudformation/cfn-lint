"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.outputs.Value import Value  # pylint: disable=E0401


@pytest.mark.parametrize(
    "input,expected",
    [
        ("foo", 0),
        (1.0, 1),
        (1, 1),
        (True, 1),
        ([{}], 1),
        ({"foo": "bar"}, 1),
    ],
)
def test_output_value(input, expected):
    rule = Value()
    validator = CfnTemplateValidator()

    results = list(rule.validate(validator, {}, input, {}))

    assert len(results) == expected, f"Expected {expected} results, got {results}"
