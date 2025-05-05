"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Cidr import Cidr
from cfnlint.rules.functions.ImportValue import ImportValue
from cfnlint.rules.functions.Join import Join
from cfnlint.rules.functions.Ref import Ref
from cfnlint.rules.functions.RefResolved import RefResolved
from cfnlint.rules.outputs.ImportValue import ImportValue as OutputsImportValue
from cfnlint.rules.outputs.Value import Value  # pylint: disable=E0401


@pytest.fixture
def template():
    return {
        "Parameters": {
            "additionalVpcCidr": {
                "Type": "String",
                "Default": "",
            },
            "badAdditionalVpcCidr": {
                "Type": "String",
                "Default": "1",
            },
        },
        "Conditions": {
            "isAdditionalVpc": {
                "Fn::Not": [
                    {
                        "Fn::Equals": [
                            {"Ref": "additionalVpcCidr"},
                            "",
                        ]
                    }
                ]
            },
            "isBadAdditionalVpc": {
                "Fn::Not": [
                    {
                        "Fn::Equals": [
                            {"Ref": "badAdditionalVpcCidr"},
                            "",
                        ]
                    }
                ]
            },
        },
    }


@pytest.fixture
def path():
    return Path(
        path=deque(["Outputs", "Test"]),
        value_path=deque(),
        cfn_path=deque(["Outputs", "*"]),
    )


@pytest.fixture
def validator(cfn, context):

    ref = Ref()
    ref.child_rules["W1030"] = RefResolved()

    importvalue = ImportValue()
    importvalue.child_rules["W6001"] = OutputsImportValue()

    yield CfnTemplateValidator(schema={}).extend(
        validators={
            "fn_join": Join().fn_join,
            "ref": ref.ref,
            "fn_cidr": Cidr().fn_cidr,
            "fn_importvalue": importvalue.fn_importvalue,
        }
    )(
        schema={},
        cfn=cfn,
        context=context,
    )


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            {
                "Value": "foo",
            },
            [],
        ),
        (
            {
                "Value": 1.0,
            },
            [],
        ),
        (
            {
                "Value": 1,
            },
            [],
        ),
        (
            {"Value": True},
            [],
        ),
        (
            {"Value": [{}]},
            [
                ValidationError(
                    "[{}] is not of type 'string'",
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque(["Value"]),
                    rule=Value(),
                )
            ],
        ),
        (
            {"Value": {"foo": "bar"}},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque(["Value"]),
                    rule=Value(),
                )
            ],
        ),
        (
            {
                "Value": {"Fn::ImportValue": "test-stack-value"},
            },
            [
                ValidationError(
                    (
                        "The output value {'Fn::ImportValue': 'test-stack-value'} "
                        "is an import from another output"
                    ),
                    validator="fn_importvalue",
                    schema_path=deque(["fn_importvalue"]),
                    path=deque(["Value", "Fn::ImportValue"]),
                    rule=OutputsImportValue(),
                )
            ],
        ),
        (
            {
                "Condition": "isAdditionalVpc",
                "Value": {
                    "Fn::Join": [
                        ",",
                        {"Fn::Cidr": [{"Ref": "additionalVpcCidr"}, 3, 8]},
                    ]
                },
            },
            [],
        ),
        (
            {
                "Condition": "isBadAdditionalVpc",
                "Value": {
                    "Fn::Join": [
                        ",",
                        {"Fn::Cidr": [{"Ref": "badAdditionalVpcCidr"}, 3, 8]},
                    ]
                },
            },
            [
                ValidationError(
                    (
                        "{'Ref': 'badAdditionalVpcCidr'} does not match "
                        "'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\\\\/([0-9]|[1-2][0-9]|3[0-2]))$'"
                        " when 'Ref' is resolved"
                    ),
                    validator="ref",
                    schema_path=deque(
                        [
                            "fn_join",
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "cfnContext",
                            "schema",
                            "fn_cidr",
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            0,
                            "cfnContext",
                            "schema",
                            "ref",
                            "pattern",
                        ]
                    ),
                    path=deque(["Value", "Fn::Join", 1, "Fn::Cidr", 0, "Ref"]),
                    rule=RefResolved(),
                )
            ],
        ),
    ],
)
def test_output_value(input, expected, validator):
    rule = Value()
    results = list(rule.validate(validator, {}, input, {}))
    assert results == expected, f"Expected {expected} results, got {results}"
