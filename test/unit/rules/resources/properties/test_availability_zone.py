"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.AvailabilityZone import (
    AvailabilityZone,  # pylint: disable=E0401
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = AvailabilityZone()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MySqs": {
                "Type": "AWS::SQS::Queue",
            }
        }
    }


@pytest.fixture(scope="module")
def validator_cdk():
    cfn = Template(
        "",
        {
            "Resources": {
                "MySqs": {
                    "Type": "AWS::SQS::Queue",
                },
                "CDK": {
                    "Type": "AWS::CDK::Metadata",
                },
            }
        },
    )
    context = (
        create_context_for_template(cfn)
        .evolve(
            functions=FUNCTIONS,
            path="Resources",
        )
        .evolve(path="MySqs")
        .evolve(path="Properties")
    )
    yield CfnTemplateValidator(schema={}, context=context, cfn=cfn)


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid ref",
            {"Ref": "AZ"},
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [],
        ),
        (
            "Valid list ref",
            [{"Ref": "AZ"}],
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [],
        ),
        (
            "Valid inside Ref",
            "us-east-1a",
            {"path": deque(["Ref"])},
            [],
        ),
        (
            "Valid GetAZs",
            ["us-east-1a", "us-east-1b"],
            {"path": deque(["Fn::GetAZs"])},
            [],
        ),
        (
            "Invalid type",
            True,
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [],
        ),
        (
            "Valid hardcoded all string",
            "all",
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [],
        ),
        (
            "Invalid hardcoded string",
            "us-east-1a",
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [
                ValidationError(
                    ("Avoid hardcoding availability zones 'us-east-1a'"),
                    rule=AvailabilityZone(),
                )
            ],
        ),
        (
            "Invalid hardcoded array",
            ["us-east-1a", "us-east-1b"],
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [
                ValidationError(
                    ("Avoid hardcoding availability zones 'us-east-1a'"),
                    rule=AvailabilityZone(),
                ),
                ValidationError(
                    ("Avoid hardcoding availability zones 'us-east-1b'"),
                    rule=AvailabilityZone(),
                ),
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, path, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert errors == expected, f"Test {name!r} got {errors!r}"


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid hardcoded string because CDK",
            "us-east-1a",
            deque(["Resources", "MySqs", "Properties"]),
            [],
        ),
    ],
)
def test_validate_for_cdk(name, instance, path, expected, rule, validator_cdk):
    validator = validator_cdk.evolve(
        context=validator_cdk.context.evolve(
            path=Path(path=path),
        )
    )
    errors = list(rule.validate(validator, False, instance, {}))
    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert errors == expected, f"Test {name!r} got {errors!r}"
