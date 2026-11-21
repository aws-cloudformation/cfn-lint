"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

import pytest

from cfnlint.api import lint


@pytest.mark.parametrize(
    "resource_type,code",
    [
        ("AWS::Lambda::Function", {"Code": {"ZipFile": "def handler(e, c): pass"}}),
        ("AWS::Serverless::Function", {"InlineCode": "def handler(e, c): pass"}),
    ],
)
@pytest.mark.parametrize("handler,expected", [("app.handler", 1), ("index.handler", 0)])
@pytest.mark.parametrize("runtime", ["python3.12", "nodejs22.x"])
def test_inline_handler(resource_type, code, handler, expected, runtime):
    template = {
        "Resources": {
            "Function": {
                "Type": resource_type,
                "Properties": {
                    **code,
                    "Handler": handler,
                    "Runtime": runtime,
                    "Role": "arn:aws:iam::123456789012:role/lambda-role",
                },
            }
        }
    }
    if resource_type == "AWS::Serverless::Function":
        template["Transform"] = "AWS::Serverless-2016-10-31"

    matches = [m for m in lint(json.dumps(template)) if m.rule.id == "E3726"]
    assert len(matches) == expected
    if matches:
        assert list(matches[0].path) == [
            "Resources",
            "Function",
            "Properties",
            "Handler",
        ]


@pytest.mark.parametrize(
    "inline_handler,expected", [("index.handler", 0), ("app.handler", 1)]
)
def test_conditional_code_and_handler(inline_handler, expected):
    template = {
        "Parameters": {"Inline": {"Type": "String", "AllowedValues": ["yes", "no"]}},
        "Conditions": {"UseInline": {"Fn::Equals": [{"Ref": "Inline"}, "yes"]}},
        "Resources": {
            "Function": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {
                        "Fn::If": [
                            "UseInline",
                            {"ZipFile": "def handler(e, c): pass"},
                            {"S3Bucket": "code-bucket", "S3Key": "function.zip"},
                        ]
                    },
                    "Handler": {"Fn::If": ["UseInline", inline_handler, "app.handler"]},
                    "Runtime": "python3.12",
                    "Role": "arn:aws:iam::123456789012:role/lambda-role",
                },
            }
        },
    }
    matches = [m for m in lint(json.dumps(template)) if m.rule.id == "E3726"]
    assert len(matches) == expected


@pytest.mark.parametrize("default", ["index.handler", "app.handler"])
def test_handler_parameter_is_not_treated_as_a_literal(default):
    template = {
        "Parameters": {"Handler": {"Type": "String", "Default": default}},
        "Resources": {
            "Function": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {"ZipFile": "def handler(e, c): pass"},
                    "Handler": {"Ref": "Handler"},
                    "Runtime": "python3.12",
                    "Role": "arn:aws:iam::123456789012:role/lambda-role",
                },
            }
        },
    }
    matches = [m for m in lint(json.dumps(template)) if m.rule.id == "E3726"]
    assert matches == []
