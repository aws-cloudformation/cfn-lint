"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, Resource, Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.GetAtt import GetAtt


@pytest.fixture(scope="module")
def rule():
    rule = GetAtt()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={
            "MyBucket": Resource(
                {
                    "Type": "AWS::S3::Bucket",
                }
            )
        },
        parameters={
            "MyResourceParameter": Parameter({"Type": "String", "Default": "MyBucket"}),
            "MyAttributeParameter": Parameter(
                {"Type": "String", "AllowedValues": ["Arn"]}
            ),
        },
        mappings={},
        transforms=Transforms(["AWS::LanguageExtensions"]),
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Ref in GetAtt for resource",
            {"Fn::GetAtt": [{"Ref": "MyResourceParameter"}, "Arn"]},
            {"type": "string"},
            [],
        ),
        (
            "Valid Ref in GetAtt for attribute",
            {"Fn::GetAtt": ["MyBucket", {"Ref": "MyAttributeParameter"}]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Ref in GetAtt for attribute",
            {"Fn::GetAtt": ["MyBucket", {"Ref": "MyResourceParameter"}]},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'MyBucket' is not one of ['Arn', 'DomainName', "
                        "'DualStackDomainName', 'RegionalDomainName', "
                        "'WebsiteURL'] when "
                        "{'Ref': 'MyResourceParameter'} is resolved"
                    ),
                    path=deque(["Fn::GetAtt", 1]),
                    validator="fn_getatt",
                )
            ],
        ),
        (
            "Invalid Ref in GetAtt for attribute",
            {"Fn::GetAtt": [{"Ref": "MyAttributeParameter"}, "Arn"]},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'Arn' is not one of ['MyBucket'] when "
                        "{'Ref': 'MyAttributeParameter'} is resolved"
                    ),
                    path=deque(["Fn::GetAtt", 0]),
                    schema_path=deque(["enum"]),
                    validator="fn_getatt",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_getatt(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
