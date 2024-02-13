"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, Resource
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Ref import Ref


@pytest.fixture(scope="module")
def rule():
    rule = Ref()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={
            "MyVolume": Resource({"Type": "AWS::EC2::Volume"}),
            "MyInstance": Resource({"Type": "AWS::EC2::Instance"}),
        },
        parameters={
            "MyParameter": Parameter({"Type": "String"}),
            "MyArrayParameter": Parameter({"Type": "CommaDelimitedList"}),
        },
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid ref",
            {"Ref": "MyVolume"},
            {"type": "string"},
            [],
        ),
        (
            "Valid array ref",
            {"Ref": "MyArrayParameter"},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Ref with bad type",
            {"Ref": ["foo"]},
            {"type": "string"},
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
                        "'MyVolume', 'MyInstance', 'AWS::NoValue', 'AWS::AccountId', "
                        "'AWS::Partition', 'AWS::Region', 'AWS::StackId', "
                        "'AWS::StackName', 'AWS::URLSuffix', 'AWS::NotificationARNs']"
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
            [ValidationError("{'Ref': 'MyParameter'} is not of type 'array'")],
        ),
        (
            "Invalid Ref with a type that doesn't match singular schema",
            {"Ref": "Foo"},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'Foo' is not one of ['MyParameter', 'MyArrayParameter', "
                        "'MyVolume', 'MyInstance', 'AWS::NoValue', 'AWS::AccountId', "
                        "'AWS::Partition', 'AWS::Region', 'AWS::StackId', "
                        "'AWS::StackName', 'AWS::URLSuffix', 'AWS::NotificationARNs']"
                    ),
                    path=deque(["Ref"]),
                    schema_path=deque(["enum"]),
                    validator="ref",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.ref(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
