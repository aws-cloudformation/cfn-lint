"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.context import Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import CfnLintKeyword
from cfnlint.rules.functions.GetAtt import GetAtt
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = GetAtt()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Resources": {
                "MyBucket": {"Type": "AWS::S3::Bucket"},
                "MyCodePipeline": {"Type": "AWS::CodePipeline::Pipeline"},
            },
            "Parameters": {
                "MyResourceParameter": {"Type": "String", "Default": "MyBucket"},
                "MyAttributeParameter": {"Type": "String", "AllowedValues": ["Arn"]},
            },
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


class _Pass(CfnLintKeyword):
    id = "AAAAA"

    def __init__(self) -> None:
        super().__init__(keywords=["*"])

    def validate(self, validator, s, instance, schema):
        return
        yield


class _Fail(CfnLintKeyword):
    id = "BBBBB"

    def __init__(self) -> None:
        super().__init__(keywords=["*"])

    def validate(self, validator, s, instance, schema):
        yield ValidationError("Fail")


@pytest.mark.parametrize(
    "name,instance,schema,context_evolve,child_rules,expected",
    [
        (
            "Valid GetAtt with a good attribute",
            {"Fn::GetAtt": ["MyBucket", "Arn"]},
            {"type": "string"},
            {},
            {},
            [],
        ),
        (
            "Invalid GetAtt with bad attribute",
            {"Fn::GetAtt": ["MyBucket", "foo"]},
            {"type": "string"},
            {},
            {},
            [
                ValidationError(
                    (
                        "'foo' is not one of ['Arn', 'DomainName', "
                        "'DualStackDomainName', 'RegionalDomainName', 'WebsiteURL'] "
                        "in ['us-east-1']"
                    ),
                    path=deque(["Fn::GetAtt", 1]),
                    schema_path=deque([]),
                    validator="fn_getatt",
                ),
            ],
        ),
        (
            "Invalid GetAtt with bad resource name",
            {"Fn::GetAtt": ["Foo", "bar"]},
            {"type": "string"},
            {},
            {},
            [
                ValidationError(
                    "'Foo' is not one of ['MyBucket', 'MyCodePipeline']",
                    path=deque(["Fn::GetAtt", 0]),
                    schema_path=deque(["enum"]),
                    validator="fn_getatt",
                ),
            ],
        ),
        (
            "Invalid GetAtt with a bad type",
            {"Fn::GetAtt": {"foo": "bar"}},
            {"type": "string"},
            {},
            {},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string', 'array'",
                    path=deque(["Fn::GetAtt"]),
                    schema_path=deque(["type"]),
                    validator="fn_getatt",
                ),
            ],
        ),
        (
            "Invalid GetAtt with a bad response type",
            {"Fn::GetAtt": "MyBucket.Arn"},
            {"type": "array"},
            {},
            {},
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyBucket.Arn'} is not of type 'array'",
                    path=deque(["Fn::GetAtt"]),
                    schema_path=deque(["type"]),
                    validator="fn_getatt",
                ),
            ],
        ),
        (
            "Invalid GetAtt with a bad response type and multiple types",
            {"Fn::GetAtt": "MyBucket.Arn"},
            {"type": ["array", "object"]},
            {},
            {},
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyBucket.Arn'} is not of type 'array', 'object'",
                    path=deque(["Fn::GetAtt"]),
                    schema_path=deque(["type"]),
                    validator="fn_getatt",
                ),
            ],
        ),
        (
            "Valid GetAtt with integer to string",
            {"Fn::GetAtt": "MyCodePipeline.Version"},
            {"type": ["integer"]},
            {
                "strict_types": False,
            },
            {},
            [],
        ),
        (
            "Invalid GetAtt with integer to string",
            {"Fn::GetAtt": "MyCodePipeline.Version"},
            {"type": ["integer"]},
            {
                "strict_types": True,
            },
            {},
            [
                ValidationError(
                    (
                        "{'Fn::GetAtt': 'MyCodePipeline.Version'} "
                        "is not of type 'integer'"
                    ),
                    path=deque(["Fn::GetAtt"]),
                    schema_path=deque(["type"]),
                    validator="fn_getatt",
                )
            ],
        ),
        (
            "Valid GetAtt with one good response type",
            {"Fn::GetAtt": "MyBucket.Arn"},
            {"type": ["array", "string"]},
            {},
            {},
            [],
        ),
        (
            "Valid Ref in GetAtt for resource",
            {"Fn::GetAtt": [{"Ref": "MyResourceParameter"}, "Arn"]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            {},
            [],
        ),
        (
            "Valid Ref in GetAtt for attribute",
            {"Fn::GetAtt": ["MyBucket", {"Ref": "MyAttributeParameter"}]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            {},
            [],
        ),
        (
            "Invalid Ref in GetAtt for attribute",
            {"Fn::GetAtt": ["MyBucket", {"Ref": "MyResourceParameter"}]},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            {},
            [
                ValidationError(
                    (
                        "'MyBucket' is not one of ['Arn', 'DomainName', "
                        "'DualStackDomainName', 'RegionalDomainName', "
                        "'WebsiteURL'] in ['us-east-1'] when "
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
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            {},
            [
                ValidationError(
                    (
                        "'Arn' is not one of ['MyBucket', 'MyCodePipeline'] when "
                        "{'Ref': 'MyAttributeParameter'} is resolved"
                    ),
                    path=deque(["Fn::GetAtt", 0]),
                    schema_path=deque(["enum"]),
                    validator="fn_getatt",
                )
            ],
        ),
        (
            "Valid GetAtt with child rules",
            {"Fn::GetAtt": ["MyBucket", "Arn"]},
            {"type": "string"},
            {},
            {
                "AAAAA": _Pass(),
                "BBBBB": _Fail(),
                "CCCCC": None,
            },
            [ValidationError("Fail")],
        ),
    ],
)
def test_validate(
    name, instance, schema, context_evolve, child_rules, expected, rule, context, cfn
):
    context = context.evolve(**context_evolve)
    rule.child_rules = child_rules
    validator = CfnTemplateValidator({}, context=context, cfn=cfn)
    errs = list(rule.fn_getatt(validator, schema, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
