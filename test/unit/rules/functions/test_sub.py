"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Resource
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Sub import Sub


@pytest.fixture(scope="module")
def rule():
    rule = Sub()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={
            "MyResource": Resource({"Type": "AWS::S3::Bucket"}),
        },
        parameters={},
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Sub",
            {"Fn::Sub": "foo"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Sub with an incorrect type",
            {"Fn::Sub": {"foo": "bar"}},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'array', 'string'",
                    path=deque(["Fn::Sub"]),
                    schema_path=deque(["type"]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Invalid Fn::Sub with an invalid output type",
            {"Fn::Sub": "foo"},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Sub': 'foo'} is not of type 'array'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Valid Fn::Sub with a valid Ref",
            {"Fn::Sub": "${AWS::Region}"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Sub with a invalid Ref",
            {"Fn::Sub": "${foo}"},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'foo' is not one of ["
                        "'MyResource', 'AWS::NoValue', 'AWS::AccountId', "
                        "'AWS::Partition', 'AWS::Region', 'AWS::StackId', "
                        "'AWS::StackName', 'AWS::URLSuffix', "
                        "'AWS::NotificationARNs']"
                    ),
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Valid Fn::Sub with a Ref to parameter",
            {"Fn::Sub": ["${foo}", {"foo": "bar"}]},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Sub with an escape character",
            {"Fn::Sub": "${!foo}"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Sub with a bad object",
            {"Fn::Sub": ["${foo}", []]},
            {"type": "string"},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    path=deque(["Fn::Sub", 1]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Invalid Fn::Sub with a bad object type",
            {
                "Fn::Sub": [
                    "${foo}",
                    {
                        "foo": [],
                    },
                ]
            },
            {"type": "string"},
            [
                ValidationError(
                    "[] is not of type 'string'",
                    path=deque(["Fn::Sub", 1, "foo"]),
                    schema_path=deque(
                        ["fn_items", "patternProperties", "[a-zA-Z0-9]+", "type"]
                    ),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Valid Fn::Sub with a GetAtt",
            {"Fn::Sub": "${MyResource.Arn}"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Sub with a GetAtt and a bad attribute",
            {"Fn::Sub": "${MyResource.Foo}"},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'MyResource.Foo' is not one of ['MyResource.Arn', "
                        "'MyResource.DomainName', "
                        "'MyResource.DualStackDomainName', "
                        "'MyResource.RegionalDomainName', "
                        "'MyResource.WebsiteURL']"
                    ),
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Invalid Fn::Sub with a GetAtt and a bad resource name",
            {"Fn::Sub": "${Foo.Bar}"},
            {"type": "string"},
            [
                ValidationError(
                    "'Foo.Bar' is not one of ['MyResource']",
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_sub(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
