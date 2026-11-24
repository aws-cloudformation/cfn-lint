"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest
import regex as re

from cfnlint.rules.formats.IamRoleName import IamRoleName


@pytest.fixture(scope="module")
def rule():
    rule = IamRoleName()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid role name",
            "AWSBatchServiceRole",
            True,
        ),
        (
            "Valid path prefixed name",
            "/foo/bar",
            True,
        ),
        (
            "Valid service-role path prefixed name",
            "/service-role/AWSBatchServiceRole",
            True,
        ),
        (
            "Valid service linked role nested path and name",
            "/aws-service-role/spotfleet.amazonaws.com/AWSServiceRoleForEC2SpotFleet",
            True,
        ),
        (
            "Valid full character set",
            "role-with-plus+equals=comma,dot.at@dash-",
            True,
        ),
        (
            "Valid maximum length name",
            "a" * 64,
            True,
        ),
        (
            "Valid maximum length name with a path",
            "/service-role/" + "a" * 64,
            True,
        ),
        (
            "Invalid name one over the maximum length",
            "a" * 65,
            False,
        ),
        (
            "Invalid empty string",
            "",
            False,
        ),
        (
            "Invalid path with no name",
            "/",
            False,
        ),
        (
            "Invalid trailing path separator with no name",
            "/foo/",
            False,
        ),
        (
            "Invalid ARN",
            "arn:aws:iam::123456789012:role/MyRole",
            False,
        ),
        (
            "Invalid name with spaces",
            "bad name with spaces",
            False,
        ),
        # unresolvable values are not strings and must stay silent
        (
            "Valid when a Ref cannot be resolved",
            {"Ref": "RoleName"},
            True,
        ),
        (
            "Valid when a GetAtt cannot be resolved",
            {"Fn::GetAtt": ["MyRole", "Arn"]},
            True,
        ),
        (
            "Valid when an Fn::If cannot be resolved",
            {"Fn::If": ["IsUsEast1", "RoleOne", "RoleTwo"]},
            True,
        ),
        (
            "Valid for a non scalar list",
            [],
            True,
        ),
        (
            "Valid for a non string scalar",
            1,
            True,
        ),
        (
            "Valid for None",
            None,
            True,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"


def test_pattern_matches_the_aws_path_spec(rule):
    """The readable path spelling must not drift from IAM's published spec.

    IAM documents ``Path`` as ``(\\u002F)|(\\u002F[\\u0021-\\u007E]+\\u002F)``.
    The rule spells the second alternative literally, so assert the two forms
    are the same string once the escapes are resolved.
    """
    assert "(/[!-~]+/)" == "(\u002f[\u0021-\u007e]+\u002f)"
    assert "(/[!-~]+/)" in rule.pattern


def test_pattern_matches_the_aws_role_name_spec(rule):
    """The readable name spelling must not drift from IAM's published spec.

    IAM documents ``RoleName`` as ``[\\w+=,.@-]{1,64}``. ``\\w`` is spelled out
    in ASCII in the rule because it is Unicode-aware in Python but ASCII-only in
    ECMA-262, and these patterns are consumed by both. Assert the literal class
    agrees with the spec class over every ASCII code point when ``\\w`` is read
    with ECMA-262 semantics.
    """
    literal = re.compile(r"^[a-zA-Z0-9_+=,.@-]$")
    aws_spec = re.compile(r"^[\w+=,.@-]$", re.ASCII)

    disagreements = [
        chr(point)
        for point in range(128)
        if bool(literal.match(chr(point))) != bool(aws_spec.match(chr(point)))
    ]
    assert disagreements == []
    assert r"[a-zA-Z0-9_+=,.@-]{1,64}" in rule.pattern


@pytest.mark.parametrize(
    "instance",
    [
        "\u00e9",  # latin small letter e with acute
        "\u4e2d",  # cjk ideograph
        "\u0661",  # arabic-indic digit one
    ],
)
def test_non_ascii_word_characters_are_rejected(instance, rule, validator):
    """Guard the reason ``\\w`` is spelled out rather than used directly.

    Python's ``\\w`` accepts these, ECMA-262's does not, and IAM does not either.
    """
    assert rule.format(validator, instance) is False
