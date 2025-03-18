"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.iam.Permissions import Permissions


@pytest.fixture(scope="module")
def rule():
    rule = Permissions()
    yield rule


@pytest.mark.parametrize(
    "name,instance,err_count",
    [
        ("Valid string", "s3:GetObject", 0),
        ("Valid list", ["s3:GetObject"], 0),
        ("Invalid string", "s3:Foo", 1),
        ("Invalid list", ["s3:Foo"], 1),
        ("Valid astrisk for permission", ["s3:*"], 0),
        ("Valid all astrisk", ["*"], 0),
        ("Valid string with ending astrisk", "s3:Get*", 0),
        ("Valid string with starting astrisk", "s3:*Object", 0),
        ("Invalid list", ["s3:Foo"], 1),
        ("Invalid string with ending astrisk", "s3:Foo*", 1),
        ("Invalid string with starting astrisk", "s3:*Foo", 1),
        ("Invalid service", "foo:Bar", 1),
        ("Empty string", "", 1),
        ("A function", {"Ref": "MyParameter"}, 0),
        ("asterisk in the middle", "iam:*Tags", 0),
        ("multiple asterisks good", "iam:*Group*", 0),
        ("multiple asterisks bad", "iam:*ec2*", 1),
        ("question mark is bad", "iam:Tag?", 1),
        ("question mark is good", "iam:TagRol?", 0),
    ],
)
def test_permissions(name, instance, err_count, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))

    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
