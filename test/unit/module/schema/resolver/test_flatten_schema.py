"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging

import pytest

from cfnlint.schema.resolver import RefResolver

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


@pytest.fixture
def resource_schema():
    return {
        "definitions": {
            "ResourceArn": {
                "description": "A resource ARN.",
                "maxLength": 256,
                "minLength": 1,
                "pattern": "^arn:aws.*$",
                "type": "string",
            },
            "Tag": {
                "oneOf": [
                    {
                        "properties": {
                            "Key": {"type": "string"},
                            "Value": {"type": "string"},
                        }
                    },
                    {
                        "properties": {
                            "TagKey": {"type": "string"},
                            "TagValue": {"type": "string"},
                        }
                    },
                ],
                "type": "object",
            },
            "Tags": {"type": "array", "items": {"$ref": "#/definitions/Tag"}},
        },
        "properties": {
            "Name": {
                "maxLength": 128,
                "minLength": 1,
                "pattern": "^[a-zA-Z0-9-]+$",
                "type": "string",
            },
            "Arn": {"$ref": "#/definitions/ResourceArn"},
            "Tags": {"$ref": "#/definitions/Tags"},
        },
        "readOnlyProperties": ["/properties/Arn"],
        "typeName": "AWS::NetworkFirewall::Firewall",
    }


@pytest.mark.parametrize(
    "name,pointer,expected",
    [
        (
            "Simple uses case",
            "/properties/Name",
            {
                "maxLength": 128,
                "minLength": 1,
                "pattern": "^[a-zA-Z0-9-]+$",
                "type": "string",
            },
        ),
        (
            "Simple ref use case",
            "/properties/Arn",
            {
                "description": "A resource ARN.",
                "maxLength": 256,
                "minLength": 1,
                "pattern": "^arn:aws.*$",
                "type": "string",
            },
        ),
    ],
)
def test_schema(name, pointer, expected, resource_schema):
    resolver = RefResolver(resource_schema)

    _, value = resolver.resolve_cfn_pointer(pointer)
    results = resolver.flatten_schema(value)
    assert results == expected, f"{name} got results {results!r}"
