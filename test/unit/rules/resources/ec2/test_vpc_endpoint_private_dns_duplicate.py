"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.VpcEndpointPrivateDnsDuplicate import (
    VpcEndpointPrivateDnsDuplicate,
)


@pytest.fixture(scope="module")
def rule():
    rule = VpcEndpointPrivateDnsDuplicate()
    yield rule


@pytest.fixture
def template():
    return {
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsUsWest2": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
        },
        "Resources": {},
    }


@pytest.mark.parametrize(
    "name,instance,starting_endpoints,expected",
    [
        (
            "Valid first endpoint in VPC",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {},
            [],
        ),
        (
            "Valid with unresolvable VpcId function",
            {
                "VpcId": {"Fn::Select": [0, ["vpc-123"]]},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {},
            [],
        ),
        (
            "Valid with unresolvable ServiceName function",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Select": [0, ["svc"]]},
                "PrivateDnsEnabled": True,
            },
            {},
            [],
        ),
        (
            "Valid with non-dict non-string VpcId",
            {
                "VpcId": 123,
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {},
            [],
        ),
        (
            "Valid with GetAtt VpcId",
            {
                "VpcId": {"Fn::GetAtt": ["MyResource", "VpcId"]},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {},
            [],
        ),
        (
            "Valid with Fn::Sub list form ServiceName",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {
                    "Fn::Sub": ["com.amazonaws.${Region}.sqs", {"Region": "us-east-1"}]
                },
                "PrivateDnsEnabled": True,
            },
            {},
            [],
        ),
        (
            "Valid same service different VPC",
            {
                "VpcId": {"Ref": "Vpc2"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc1", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (["Resources", "Endpoint1"], {})
                ],
            },
            [],
        ),
        (
            "Valid different service same VPC",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sns"},
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (["Resources", "Endpoint1"], {})
                ],
            },
            [],
        ),
        (
            "Valid PrivateDnsEnabled is false",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": False,
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (["Resources", "Endpoint1"], {})
                ],
            },
            [],
        ),
        (
            "Valid Gateway type duplicate",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Gateway",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.s3"},
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.s3"): [
                    (["Resources", "Endpoint1"], {})
                ],
            },
            [],
        ),
        (
            "Valid with mutually exclusive conditions via Fn::If on PrivateDns",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": {"Fn::If": ["IsUsWest2", True, False]},
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (
                        ["Resources", "Endpoint1"],
                        {"IsUsEast1": True, "IsUsWest2": False},
                    ),
                ],
            },
            [],
        ),
        (
            "Valid with Fn::If on VpcId resolving to different VPCs",
            {
                "VpcId": {"Fn::If": ["IsUsEast1", {"Ref": "Vpc1"}, {"Ref": "Vpc2"}]},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc1", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (
                        ["Resources", "Endpoint1"],
                        {"IsUsEast1": True},
                    ),
                ],
            },
            [
                ValidationError(
                    (
                        "Only one Interface VPC Endpoint per service "
                        "can have 'PrivateDnsEnabled' set to true in "
                        "a VPC. A second endpoint will fail to create "
                        "due to a conflicting private DNS domain."
                    ),
                    rule=VpcEndpointPrivateDnsDuplicate(),
                )
            ],
        ),
        (
            "Valid with PrivateDnsEnabled via Fn::If resolving to false",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": {"Fn::If": ["IsUsEast1", False, True]},
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (
                        ["Resources", "Endpoint1"],
                        {"IsUsEast1": True},
                    ),
                ],
            },
            [],
        ),
        (
            "Invalid with same conditions on both endpoints",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (
                        ["Resources", "Endpoint1"],
                        {"IsUsEast1": True},
                    ),
                ],
            },
            [
                ValidationError(
                    (
                        "Only one Interface VPC Endpoint per service "
                        "can have 'PrivateDnsEnabled' set to true in "
                        "a VPC. A second endpoint will fail to create "
                        "due to a conflicting private DNS domain."
                    ),
                    rule=VpcEndpointPrivateDnsDuplicate(),
                )
            ],
        ),
        (
            "Invalid duplicate same service same VPC",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (["Resources", "Endpoint1"], {})
                ],
            },
            [
                ValidationError(
                    (
                        "Only one Interface VPC Endpoint per service "
                        "can have 'PrivateDnsEnabled' set to true in "
                        "a VPC. A second endpoint will fail to create "
                        "due to a conflicting private DNS domain."
                    ),
                    rule=VpcEndpointPrivateDnsDuplicate(),
                )
            ],
        ),
        (
            "Invalid with Fn::If on ServiceName matching saved in same condition",
            {
                "VpcId": {"Ref": "Vpc"},
                "VpcEndpointType": "Interface",
                "ServiceName": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Fn::Sub": "com.amazonaws.${AWS::Region}.sqs"},
                        {"Fn::Sub": "com.amazonaws.${AWS::Region}.sns"},
                    ]
                },
                "PrivateDnsEnabled": True,
            },
            {
                ("Ref:Vpc", "Sub:com.amazonaws.${AWS::Region}.sqs"): [
                    (
                        ["Resources", "Endpoint1"],
                        {"IsUsEast1": True},
                    ),
                ],
            },
            [
                ValidationError(
                    (
                        "Only one Interface VPC Endpoint per service "
                        "can have 'PrivateDnsEnabled' set to true in "
                        "a VPC. A second endpoint will fail to create "
                        "due to a conflicting private DNS domain."
                    ),
                    rule=VpcEndpointPrivateDnsDuplicate(),
                )
            ],
        ),
        (
            "Invalid duplicate with hardcoded VPC ID",
            {
                "VpcId": "vpc-12345678",
                "VpcEndpointType": "Interface",
                "ServiceName": "com.amazonaws.us-east-1.execute-api",
                "PrivateDnsEnabled": True,
            },
            {
                ("vpc-12345678", "com.amazonaws.us-east-1.execute-api"): [
                    (["Resources", "Endpoint1"], {})
                ],
            },
            [
                ValidationError(
                    (
                        "Only one Interface VPC Endpoint per service "
                        "can have 'PrivateDnsEnabled' set to true in "
                        "a VPC. A second endpoint will fail to create "
                        "due to a conflicting private DNS domain."
                    ),
                    rule=VpcEndpointPrivateDnsDuplicate(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, starting_endpoints, expected, rule, validator):
    rule._endpoints = starting_endpoints
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, (
        f"Expected test {name!r} to have {expected!r} but got {errs!r}"
    )
