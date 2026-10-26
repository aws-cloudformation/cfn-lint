"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.rules.resources.lmbd.FunctionZipfileHandler import FunctionZipfileHandler


@pytest.fixture(scope="module")
def rule():
    return FunctionZipfileHandler()


@pytest.mark.parametrize(
    "code",
    [
        {"Code": {"ZipFile": "def handler(e, c): pass"}},
        {"InlineCode": "exports.handler = async () => {};"},
    ],
)
@pytest.mark.parametrize(
    "handler,expected",
    [
        ("index.handler", 0),
        ("index.lambda_handler", 0),
        ("index.api.handler", 0),
        ("app.handler", 1),
        ("index_handler", 1),
        ("indexXhandler", 1),
        ("Index.handler", 1),
        ("index.", 1),
        ("", 1),
        ({"Ref": "Handler"}, 0),
        ({"Fn::GetAtt": ["OtherResource", "Handler"]}, 0),
    ],
)
def test_inline_handler(code, handler, expected, rule, validator):
    errors = list(rule.validate(validator, "", {**code, "Handler": handler}, {}))
    assert len(errors) == expected
    if errors:
        assert errors[0].rule == rule
        assert errors[0].path == deque(["Handler"])
        assert errors[0].message == (
            "Inline Lambda code requires Handler to start with 'index.'"
        )


@pytest.mark.parametrize(
    "instance",
    [
        {},
        [],
        {
            "Code": {"S3Bucket": "bucket", "S3Key": "function.zip"},
            "Handler": "app.handler",
        },
        {"Code": {"ImageUri": "image"}, "PackageType": "Image"},
        {"CodeUri": "src/", "Handler": "app.handler"},
        {"Code": {"ZipFile": "code"}},
        {"InlineCode": "code"},
        {"Code": {"Ref": "Code"}, "Handler": "app.handler"},
        {"Code": "invalid", "Handler": "app.handler"},
        {"Handler": "app.handler"},
    ],
)
def test_other_code_sources_and_missing_properties(instance, rule, validator):
    assert list(rule.validate(validator, "", instance, {})) == []
