"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.DynamicReferenceSecureString import (
    DynamicReferenceSecureString,
)


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReferenceSecureString()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyResource": {
                "Type": "AWS::IAM::User",
                "Properties": {"LoginProfile": {"Password": "Foo"}},
            }
        }
    }


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid SSM Secure Parameter",
            "{{resolve:ssm-secure:Parameter}}",
            {
                "cfn_path": [
                    "Resources",
                    "AWS::IAM::User",
                    "Properties",
                    "LoginProfile",
                    "Password",
                ]
            },
            [],
        ),
        (
            "Invalid SSM secure location",
            "{{resolve:ssm-secure:Parameter}}",
            {"cfn_path": ["Outputs", "*", "Value"]},
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm-secure:Parameter}}' "
                        "to SSM secure strings can only be used in resource properties"
                    ),
                    rule=DynamicReferenceSecureString(),
                )
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, path, expected, rule, validator):

    errs = list(rule.validate(validator, {"type": "string"}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
