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


@pytest.fixture
def resource_servicecatalog_schema():
    return {
        "additionalProperties": False,
        "createOnlyProperties": [
            "/properties/NotificationArns",
            "/properties/ProvisionedProductName",
        ],
        "definitions": {
            "OutputType": {"type": "string"},
            "ProvisioningParameter": {
                "additionalProperties": False,
                "properties": {
                    "Key": {"maxLength": 1000, "minLength": 1, "type": "string"},
                    "Value": {"maxLength": 4096, "type": "string"},
                },
                "required": ["Key", "Value"],
                "type": "object",
            },
            "ProvisioningPreferences": {
                "additionalProperties": False,
                "properties": {
                    "StackSetAccounts": {
                        "items": {"pattern": "^[0-9]{12}$", "type": "string"},
                        "type": "array",
                        "uniqueItems": True,
                    },
                    "StackSetFailureToleranceCount": {"minimum": 0, "type": "integer"},
                    "StackSetFailureTolerancePercentage": {
                        "maximum": 100,
                        "minimum": 0,
                        "type": "integer",
                    },
                    "StackSetMaxConcurrencyCount": {"minimum": 1, "type": "integer"},
                    "StackSetMaxConcurrencyPercentage": {
                        "maximum": 100,
                        "minimum": 1,
                        "type": "integer",
                    },
                    "StackSetOperationType": {
                        "enum": ["CREATE", "UPDATE", "DELETE"],
                        "type": "string",
                    },
                    "StackSetRegions": {
                        "items": {
                            "pattern": "^[a-z]{2}-([a-z]+-)+[1-9]",
                            "type": "string",
                        },
                        "type": "array",
                        "uniqueItems": True,
                    },
                },
                "type": "object",
            },
            "Tag": {
                "additionalProperties": False,
                "properties": {
                    "Key": {
                        "maxLength": 128,
                        "minLength": 1,
                        "pattern": "^([\\p{L}\\p{Z}\\p{N}_.:/=+\\-@]*)$",
                        "type": "string",
                    },
                    "Value": {
                        "maxLength": 256,
                        "minLength": 1,
                        "pattern": "^([\\p{L}\\p{Z}\\p{N}_.:/=+\\-@]*)$",
                        "type": "string",
                    },
                },
                "required": ["Key", "Value"],
                "type": "object",
            },
        },
        "documentationUrl": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-servicecatalog-cloudformationprovisionedproduct.html",
        "handlers": {
            "create": {"permissions": ["*"], "timeoutInMinutes": 720},
            "delete": {"permissions": ["*"]},
            "read": {"permissions": ["*"]},
            "update": {"permissions": ["*"], "timeoutInMinutes": 720},
        },
        "primaryIdentifier": ["/properties/ProvisionedProductId"],
        "properties": {
            "AcceptLanguage": {"enum": ["en", "jp", "zh"], "type": "string"},
            "CloudformationStackArn": {
                "maxLength": 256,
                "minLength": 1,
                "type": "string",
            },
            "NotificationArns": {
                "items": {"type": "string"},
                "maxItems": 5,
                "type": "array",
                "uniqueItems": True,
            },
            "Outputs": {
                "additionalProperties": False,
                "maxProperties": 100,
                "patternProperties": {
                    "^[A-Za-z0-9]{1,64}$": {"$ref": "#/definitions/OutputType"}
                },
                "type": "object",
            },
            "PathId": {"maxLength": 100, "minLength": 1, "type": "string"},
            "PathName": {"maxLength": 100, "minLength": 1, "type": "string"},
            "ProductId": {"maxLength": 100, "minLength": 1, "type": "string"},
            "ProductName": {"maxLength": 128, "minLength": 1, "type": "string"},
            "ProvisionedProductId": {"maxLength": 50, "minLength": 1, "type": "string"},
            "ProvisionedProductName": {
                "maxLength": 128,
                "minLength": 1,
                "type": "string",
            },
            "ProvisioningArtifactId": {
                "maxLength": 100,
                "minLength": 1,
                "type": "string",
            },
            "ProvisioningArtifactName": {"type": "string"},
            "ProvisioningParameters": {
                "items": {"$ref": "#/definitions/ProvisioningParameter"},
                "type": "array",
            },
            "ProvisioningPreferences": {
                "$ref": "#/definitions/ProvisioningPreferences"
            },
            "RecordId": {"maxLength": 50, "minLength": 1, "type": "string"},
            "Tags": {"items": {"$ref": "#/definitions/Tag"}, "type": "array"},
        },
        "readOnlyProperties": [
            "/properties/RecordId",
            "/properties/CloudformationStackArn",
            "/properties/Outputs",
            "/properties/ProvisionedProductId",
        ],
        "sourceUrl": "https://github.com/aws-cloudformation/aws-cloudformation-rpdk.git",
        "typeName": "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
    }


def test_servicecatalog_cloudformation_schema(resource_servicecatalog_schema):

    schema = Schema(schema=resource_servicecatalog_schema)
    assert list(schema.get_atts.keys()) == [
        "RecordId",
        "CloudformationStackArn",
        "Outputs\\..*",
        "ProvisionedProductId",
    ]
    assert schema.get_atts["Outputs.Example"] == "/properties/CfnLintStringType"
