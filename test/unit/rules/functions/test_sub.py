"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.GetAtt import GetAtt
from cfnlint.rules.functions.GetAz import GetAz
from cfnlint.rules.functions.Ref import Ref
from cfnlint.rules.functions.Sub import Sub
from cfnlint.rules.functions.SubResolved import SubResolved
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Sub()
    rule.child_rules["W1031"] = SubResolved()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Parameters": {
                "MyParameter": {
                    "Type": "String",
                    "AllowedValues": [
                        "one",
                        "two",
                    ],
                }
            },
            "Resources": {
                "MyResource": {"Type": "AWS::S3::Bucket"},
                "MySimpleAd": {"Type": "AWS::DirectoryService::SimpleAD"},
                "MyPolicy": {"Type": "AWS::IAM::ManagedPolicy"},
            },
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


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
            "Valid Fn::Sub with a valid Ref and a string escape",
            {"Fn::Sub": "${!Foo}=${AWS::Region}"},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Sub with a valid Ref and a string escape with parameter",
            {"Fn::Sub": "${!foo}=${bar}"},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'bar' is not one of ["
                        "'MyParameter', 'MyResource', 'MySimpleAd', 'MyPolicy', "
                        "'AWS::AccountId', 'AWS::NoValue', 'AWS::NotificationARNs', "
                        "'AWS::Partition', 'AWS::Region', "
                        "'AWS::StackId', 'AWS::StackName', 'AWS::URLSuffix']"
                    ),
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Invalid Fn::Sub with a invalid Ref",
            {"Fn::Sub": "${foo}"},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "'foo' is not one of ["
                        "'MyParameter', 'MyResource', 'MySimpleAd', 'MyPolicy', "
                        "'AWS::AccountId', 'AWS::NoValue', 'AWS::NotificationARNs', "
                        "'AWS::Partition', 'AWS::Region', "
                        "'AWS::StackId', 'AWS::StackName', 'AWS::URLSuffix']"
                    ),
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Valid Fn::Sub with a Ref to a sub parameter",
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
            "Valid Fn::Sub with an ref to resource",
            {"Fn::Sub": ["${MyResource}", {"MyResource": {"Ref": "MyResource"}}]},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Sub with an integer parameter",
            {"Fn::Sub": ["${Foo}", {"Foo": 1}]},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Sub with a space and escape char",
            {"Fn::Sub": "${ !Foo }"},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Sub with a space and no escape char",
            {"Fn::Sub": "${ AWS::AccountId }"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Sub with a too to many elements",
            {"Fn::Sub": ["${foo}", {"foo": "bar"}, {}]},
            {"type": "string"},
            [
                ValidationError(
                    "expected maximum item count: 2, found: 3",
                    path=deque(["Fn::Sub"]),
                    schema_path=deque(["maxItems"]),
                    validator="fn_sub",
                ),
            ],
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
            "Invalid Fn::Sub with a bad object type from fn",
            {
                "Fn::Sub": [
                    "${foo}",
                    {
                        "foo": {"Fn::GetAZs": ""},
                    },
                ]
            },
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::GetAZs': ''} is not of type 'string'",
                    path=deque(["Fn::Sub", 1, "foo"]),
                    schema_path=deque(
                        ["fn_items", "patternProperties", "[a-zA-Z0-9]+", "fn_getazs"]
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
                        "'Foo' is not one of ['Arn', "
                        "'DomainName', "
                        "'DualStackDomainName', "
                        "'RegionalDomainName', "
                        "'MetadataTableConfiguration.S3TablesDestination.TableNamespace',"
                        " 'MetadataTableConfiguration.S3TablesDestination.TableArn',"
                        " 'WebsiteURL'] in ['us-east-1']"
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
                    "'Foo' is not one of ['MyResource', 'MySimpleAd', 'MyPolicy']",
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Invalid Fn::Sub with a GetAtt to an array of attributes",
            {"Fn::Sub": "${MySimpleAd.DnsIpAddresses}"},
            {"type": "string"},
            [
                ValidationError(
                    ("'MySimpleAd.DnsIpAddresses' is not of type 'string'"),
                    instance="MySimpleAd.DnsIpAddresses",
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "Invalid Fn::Sub with a GetAtt to an integer",
            {"Fn::Sub": "${MyPolicy.AttachmentCount}"},
            {"type": "string"},
            [
                ValidationError(
                    ("'MyPolicy.AttachmentCount' is not of type 'string'"),
                    instance="MySimpleAd.DnsIpAddresses",
                    path=deque(["Fn::Sub"]),
                    schema_path=deque([]),
                    validator="fn_sub",
                ),
            ],
        ),
        (
            "One valid resolution",
            {"Fn::Sub": "${MyParameter}"},
            {"type": "string", "const": "two"},
            [],
        ),
        (
            "No valid resolution",
            {"Fn::Sub": "${MyParameter}"},
            {"type": "string", "const": "three"},
            [
                ValidationError(
                    ("'three' was expected when 'Fn::Sub' is resolved"),
                    path=deque(["Fn::Sub"]),
                    schema_path=deque(["const"]),
                    validator="fn_sub",
                    rule=SubResolved(),
                ),
                ValidationError(
                    ("'three' was expected when 'Fn::Sub' is resolved"),
                    path=deque(["Fn::Sub"]),
                    schema_path=deque(["const"]),
                    validator="fn_sub",
                    rule=SubResolved(),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, context, cfn):
    validator = CfnTemplateValidator({}).extend(
        validators={
            "ref": Ref().ref,
            "fn_getatt": GetAtt().fn_getatt,
            "fn_getazs": GetAz().fn_getazs,
        }
    )(context=context, cfn=cfn)
    errs = list(rule.fn_sub(validator, schema, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
