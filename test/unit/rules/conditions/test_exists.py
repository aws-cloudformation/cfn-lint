"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.conditions.Exists import Exists


@pytest.fixture(scope="module")
def rule():
    rule = Exists()
    yield rule


@pytest.fixture
def template():
    return {
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
        },
        "Resources": {
            "MyRdsDbInstance": {
                "Type": "AWS::RDS::DBInstance",
            }
        },
    }


@pytest.fixture
def path():
    return Path(path=deque(["Resources", "MyRdsDbInstance", "Properties"]))


@pytest.mark.parametrize(
    "name,instance,errors",
    [
        ("Valid with string", "IsUsEast1", []),
        ("No response when an incorrect  type", {}, []),
        (
            "Invalid with a condition that doesn't exist",
            "IsUsWest2",
            [
                ValidationError(
                    "'IsUsWest2' is not one of ['IsUsEast1']",
                    rule=Exists(),
                    validator="enum",
                    schema_path=deque(["enum"]),
                )
            ],
        ),
    ],
)
def test_condition(name, instance, errors, rule, validator):
    errs = list(rule.cfncondition(validator, {}, instance, {}))
    assert errs == errors, f"Test {name!r} failed with {errs!r}"
