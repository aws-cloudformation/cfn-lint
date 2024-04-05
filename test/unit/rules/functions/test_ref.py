"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.context import Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.jsonschema._keywords_cfn import FnItems
from cfnlint.rules.functions.Ref import Ref
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Ref()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Resources": {
                "MyVolume": {"Type": "AWS::EC2::Volume"},
                "MyInstance": {"Type": "AWS::EC2::Instance"},
            },
            "Parameters": {
                "MyParameter": {
                    "Type": "String",
                },
                "MyArrayParameter": {
                    "Type": "CommaDelimitedList",
                },
            },
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,schema,context_evolve,expected",
    [
        (
            "Valid ref",
            {"Ref": "MyVolume"},
            {"type": "string"},
            {},
            [],
        ),
        (
            "Valid array ref",
            {"Ref": "MyArrayParameter"},
            {"type": "array"},
            {},
            [],
        ),
        (
            "Invalid Ref with bad type",
            {"Ref": ["foo"]},
            {"type": "string"},
            {},
            [
                ValidationError(
                    "['foo'] is not of type 'string'",
                    path=deque(["Ref"]),
                    validator="ref",
                    schema_path=deque(["type"]),
                ),
                ValidationError(
                    (
                        "['foo'] is not one of ['MyParameter', 'MyArrayParameter', "
                        "'MyVolume', 'MyInstance', 'AWS::AccountId', "
                        "'AWS::NoValue', 'AWS::NotificationARNs', "
                        "'AWS::Partition', 'AWS::Region', "
                        "'AWS::StackId', 'AWS::StackName', 'AWS::URLSuffix']"
                    ),
                    path=deque(["Ref"]),
                    schema_path=deque(["enum"]),
                    validator="ref",
                ),
            ],
        ),
        (
            "Invalid Ref with a type that doesn't match array schema",
            {"Ref": "MyParameter"},
            {"type": "array"},
            {},
            [ValidationError("{'Ref': 'MyParameter'} is not of type 'array'")],
        ),
        (
            "Invalid Ref with a type that doesn't match singular schema",
            {"Ref": "Foo"},
            {"type": "string"},
            {},
            [
                ValidationError(
                    (
                        "'Foo' is not one of ['MyParameter', 'MyArrayParameter', "
                        "'MyVolume', 'MyInstance', 'AWS::AccountId', "
                        "'AWS::NoValue', 'AWS::NotificationARNs', "
                        "'AWS::Partition', 'AWS::Region', "
                        "'AWS::StackId', 'AWS::StackName', 'AWS::URLSuffix']"
                    ),
                    path=deque(["Ref"]),
                    schema_path=deque(["enum"]),
                    validator="ref",
                ),
            ],
        ),
        (
            "Valid ref",
            {"Ref": {"Ref": "MyParameter"}},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
        ),
        (
            "Invalid second ref with array return",
            {"Ref": {"Ref": "MyArrayParameter"}},
            {"type": "array"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [
                ValidationError(
                    "{'Ref': 'MyArrayParameter'} is not of type 'string'",
                    path=deque(["Ref"]),
                    validator="ref",
                    schema_path=deque(["ref"]),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, context_evolve, expected, rule, context, cfn):
    context = context.evolve(**context_evolve)
    validator = CfnTemplateValidator({}).extend(
        validators={
            "fn_items": FnItems().validate,
            "ref": Ref().ref,
        }
    )(context=context, cfn=cfn)
    errs = list(rule.ref(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
