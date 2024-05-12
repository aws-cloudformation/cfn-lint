"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.s3.AccessControlObsolete import AccessControlObsolete
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = AccessControlObsolete()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={}).evolve(cfn=Template("", {}))


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "AccessControl": "AuthenticatedRead",
            },
            [
                ValidationError(
                    (
                        "'AccessControl' is a legacy property. "
                        "Consider using 'AWS::S3::BucketPolicy' instead"
                    ),
                    path=deque(["AccessControl"]),
                )
            ],
        ),
        (
            {
                "AccessControl": {"Ref": "AWS::NoValue"},
            },
            [],
        ),
        (
            {},
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
