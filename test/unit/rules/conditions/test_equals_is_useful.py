"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.conditions.EqualsIsUseful import EqualsIsUseful


@pytest.mark.parametrize(
    "name,instance,num_of_errors",
    [
        ("Equal string and integer", [1, "1"], 1),
        ("Equal string and boolean", [True, "true"], 1),
        ("Equal string and number", [1.0, "1.0"], 1),
        ("Not equal string and integer", [1, "1.1"], 1),
        ("Not equal string and boolean", [True, "True"], 1),
        ("No error on bad type", {"true": True}, 0),
        ("No error on bad length", ["a", "a", "a"], 0),
        ("No with string and account id", ["A", {"Ref": "AWS::AccountId"}], 0),
        ("No with string and account id", [{"Ref": "AWS::AccountId"}, "A"], 0),
    ],
)
def test_names(name, instance, num_of_errors):
    rule = EqualsIsUseful()
    validator = CfnTemplateValidator({})
    assert (
        len(list(rule.equals_is_useful(validator, {}, instance, {}))) == num_of_errors
    ), f"Expected {num_of_errors} errors for {name} and {instance}"
