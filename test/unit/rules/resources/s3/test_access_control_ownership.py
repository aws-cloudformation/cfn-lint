"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.s3.AccessControlOwnership import AccessControlOwnership


@pytest.fixture(scope="module")
def rule():
    rule = AccessControlOwnership()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {},
            [],
        ),
        (
            {"AccessControl": "Private"},
            [],
        ),
        (
            {
                "AccessControl": {"Ref": "AWS::NoValue"},
            },
            [],
        ),
        (
            {
                "AccessControl": "AuthenticatedRead",
                "OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwner"}]},
            },
            [],
        ),
        (
            {
                "AccessControl": "AuthenticatedRead",
            },
            [
                ValidationError(
                    (
                        "A bucket with 'AccessControl' set should also "
                        "have at least one 'OwnershipControl' configured"
                    ),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                    rule=AccessControlOwnership(),
                )
            ],
        ),
        (
            {
                "AccessControl": "AuthenticatedRead",
                "OwnershipControls": {},
            },
            [
                ValidationError(
                    (
                        "A bucket with 'AccessControl' set should also "
                        "have at least one 'OwnershipControl' configured"
                    ),
                    path=deque(["OwnershipControls"]),
                    validator="required",
                    schema_path=deque(
                        ["then", "properties", "OwnershipControls", "required"]
                    ),
                    rule=AccessControlOwnership(),
                )
            ],
        ),
        (
            {
                "AccessControl": "AuthenticatedRead",
                "OwnershipControls": {
                    "Rules": [],
                },
            },
            [
                ValidationError(
                    (
                        "A bucket with 'AccessControl' set should also "
                        "have at least one 'OwnershipControl' configured"
                    ),
                    path=deque(["OwnershipControls", "Rules"]),
                    validator="minItems",
                    schema_path=deque(
                        [
                            "then",
                            "properties",
                            "OwnershipControls",
                            "properties",
                            "Rules",
                            "minItems",
                        ]
                    ),
                    rule=AccessControlOwnership(),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
