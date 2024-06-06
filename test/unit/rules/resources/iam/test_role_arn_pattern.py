"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema.validators import CfnTemplateValidator
from cfnlint.rules.resources.iam.RoleArnPattern import RoleArnPattern


def _message_errors(name, arn, errors, **kwargs):
    validator = CfnTemplateValidator().evolve(**kwargs)

    i_errors = list(RoleArnPattern().validate(validator, {}, arn, {}))

    assert len(errors) == len(i_errors), (
        f"{name}: Expected exactly {len(errors)} error, "
        f"found {i_errors!r}, need {errors!r}"
    )

    err_messages = [err.message for err in i_errors]
    for err in errors:
        assert err in err_messages, f"{name}: expected {err} to be in {i_errors!r}"


@pytest.mark.parametrize(
    "name,arn,errors",
    [
        (
            "Invalid Arn",
            "test",
            [
                (
                    "'test' does not match '^arn:(aws[a-zA-Z-]*)?:"
                    "iam::\\\\d{12}:role/[a-zA-Z_0-9+=,.@\\\\-_/]+$'"
                )
            ],
        ),
        (
            "Valid but wrong type",
            {},
            [],
        ),
        (
            "Valid Arn",
            "arn:aws:iam::123456789012:role/test",
            [],
        ),
        (
            "Valid Arn for aws-us-gov",
            "arn:aws-us-gov:iam::123456789012:role/test",
            [],
        ),
    ],
)
def test_iam_role_arn(name, arn, errors):
    _message_errors(name, arn, errors)
