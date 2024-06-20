"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging

import pytest

from cfnlint.schema._schema import Schema

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


@pytest.fixture
def resource_schema():
    return {
        "additionalProperties": False,
        "definitions": {
            "ListItem": {"description": "A a list Id.", "type": "string"},
            "ResourceArn": {
                "description": "A resource ARN.",
                "maxLength": 256,
                "minLength": 1,
                "pattern": "^arn:aws.*$",
                "type": "string",
            },
        },
        "properties": {
            "Name": {
                "maxLength": 128,
                "minLength": 1,
                "pattern": "^[a-zA-Z0-9-]+$",
                "type": "string",
            },
            "List": {
                "insertionOrder": False,
                "items": {"$ref": "#/definitions/ListItem"},
                "type": "array",
            },
            "Arn": {"$ref": "#/definitions/ResourceArn"},
            "Id": {
                "maxLength": 36,
                "minLength": 36,
                "pattern": "^([0-9a-f]{8})-([0-9a-f]{4}-){3}([0-9a-f]{12})$",
                "type": "string",
            },
        },
        "readOnlyProperties": [
            "/properties/Arn",
            "/properties/Id",
            "/properties/List",
        ],
        "typeName": "AWS::NetworkFirewall::Firewall",
    }


def test_schema(resource_schema):

    schema = Schema(schema=resource_schema)
    assert list(schema.get_atts.keys()) == ["Arn", "Id", "List"]
    assert schema.get_atts["Arn"] == "/properties/Arn"
    assert schema.get_atts["Id"] == "/properties/Id"
    assert schema.get_atts["List"] == "/properties/List"


@pytest.fixture
def resource_vpc_schema():
    return {
        "additionalProperties": False,
        "conditionalCreateOnlyProperties": ["/properties/InstanceTenancy"],
        "createOnlyProperties": [
            "/properties/CidrBlock",
            "/properties/Ipv4IpamPoolId",
            "/properties/Ipv4NetmaskLength",
        ],
        "definitions": {
            "Tag": {
                "additionalProperties": False,
                "properties": {"Key": {"type": "string"}, "Value": {"type": "string"}},
                "required": ["Value", "Key"],
                "type": "object",
            }
        },
        "dependentRequired": {"Ipv4IpamPoolId": ["Ipv4NetmaskLength"]},
        "primaryIdentifier": ["/properties/VpcId"],
        "properties": {
            "CidrBlock": {"type": "string"},
            "CidrBlockAssociations": {
                "insertionOrder": False,
                "items": {"type": "string"},
                "type": "array",
                "uniqueItems": False,
            },
            "DefaultNetworkAcl": {"insertionOrder": False, "type": "string"},
            "DefaultSecurityGroup": {
                "format": "AWS::EC2::SecurityGroup.GroupId",
                "insertionOrder": False,
                "type": "string",
            },
            "EnableDnsHostnames": {"type": "boolean"},
            "EnableDnsSupport": {"type": "boolean"},
            "InstanceTenancy": {"type": "string"},
            "Ipv4IpamPoolId": {"type": "string"},
            "Ipv4NetmaskLength": {"type": "integer"},
            "Ipv6CidrBlocks": {
                "insertionOrder": False,
                "items": {"type": "string"},
                "type": "array",
                "uniqueItems": False,
            },
            "Tags": {
                "insertionOrder": False,
                "items": {"$ref": "#/definitions/Tag"},
                "type": "array",
                "uniqueItems": False,
            },
            "VpcId": {"format": "AWS::EC2::VPC.Id", "type": "string"},
        },
        "readOnlyProperties": [
            "/properties/CidrBlockAssociations",
            "/properties/DefaultNetworkAcl",
            "/properties/DefaultSecurityGroup",
            "/properties/Ipv6CidrBlocks",
            "/properties/VpcId",
        ],
        "requiredXor": ["CidrBlock", "Ipv4IpamPoolId"],
        "tagging": {
            "cloudFormationSystemTags": True,
            "tagOnCreate": True,
            "tagProperty": "/properties/Tags",
            "tagUpdatable": True,
            "taggable": True,
        },
        "typeName": "AWS::EC2::VPC",
        "writeOnlyProperties": [
            "/properties/Ipv4IpamPoolId",
            "/properties/Ipv4NetmaskLength",
        ],
    }


def test_vpc_schema(resource_vpc_schema):

    schema = Schema(schema=resource_vpc_schema)
    assert list(schema.get_atts.keys()) == [
        "CidrBlock",
        "CidrBlockAssociations",
        "DefaultNetworkAcl",
        "DefaultSecurityGroup",
        "EnableDnsHostnames",
        "EnableDnsSupport",
        "InstanceTenancy",
        "Ipv4IpamPoolId",
        "Ipv4NetmaskLength",
        "Ipv6CidrBlocks",
        "Tags",
        "VpcId",
    ]
    assert schema.get_atts["VpcId"] == "/properties/VpcId"
    assert schema.get_atts["CidrBlock"] == "/properties/CidrBlock"
    assert schema.get_atts["Ipv6CidrBlocks"] == "/properties/Ipv6CidrBlocks"
