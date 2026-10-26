"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
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
                "'test' does not match '^arn:(aws[a-zA-Z-]*)?:"
                "iam::\\\\d{12}:role/[a-zA-Z_0-9+=,.@\\\\-_/]+$'"
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


_ARN_ERROR = (
    "{!r} does not match '^arn:(aws[a-zA-Z-]*)?:"
    "iam::\\\\d{{12}}:role/[a-zA-Z_0-9+=,.@\\\\-_/]+$'"
)


@pytest.mark.parametrize(
    "name,role,path,errors",
    [
        (
            "Batch ServiceRole accepts a role name",
            "my-batch-service-role",
            ["Resources", "ComputeEnvironment", "Properties", "ServiceRole"],
            [],
        ),
        (
            "Batch ServiceRole still accepts an ARN",
            "arn:aws:iam::123456789012:role/service-role/my-role",
            ["Resources", "ComputeEnvironment", "Properties", "ServiceRole"],
            [],
        ),
        (
            "Batch ServiceRole accepts a path-prefixed name",
            "service-role/my-role",
            ["Resources", "ComputeEnvironment", "Properties", "ServiceRole"],
            [],
        ),
        (
            "Batch ServiceRole accepts a name with a custom path",
            "/foo/bar",
            ["Resources", "ComputeEnvironment", "Properties", "ServiceRole"],
            [],
        ),
        (
            "Batch ServiceRole still validates a malformed ARN",
            "arn:aws:iam::123:role/x",
            ["Resources", "ComputeEnvironment", "Properties", "ServiceRole"],
            [_ARN_ERROR.format("arn:aws:iam::123:role/x")],
        ),
        (
            "Other properties still need a full ARN",
            "my-role",
            [
                "Resources",
                "TaskDefinition",
                "Properties",
                "ExecutionRoleArn",
            ],
            [_ARN_ERROR.format("my-role")],
        ),
    ],
)
def test_iam_role_name_only_for_service_role(name, role, path, errors):
    validator = CfnTemplateValidator()
    validator = validator.evolve(
        context=validator.context.evolve(path=Path(path=deque(path)))
    )
    _message_errors(name, role, errors, context=validator.context)
