"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging

import pytest

from cfnlint.schema._schema import Schema
from cfnlint.schema.resolver._exceptions import RefResolutionError

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
            "AList": {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"},
                ],
                "type": "array",
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

    assert schema.resolver.resolve_from_url("#/") == resource_schema

    assert schema.resolver.resolve_from_url("#/properties/Name") == {
        "maxLength": 128,
        "minLength": 1,
        "pattern": "^[a-zA-Z0-9-]+$",
        "type": "string",
    }

    assert schema.resolver.resolve_from_url("#/definitions/ListItem") == {
        "description": "A a list Id.",
        "type": "string",
    }
    assert schema.resolver.resolve_from_url("#/definitions/AList/items/0") == {
        "type": "string"
    }
    assert schema.resolver.resolve_from_url("#/definitions/AList/items/1") == {
        "type": "boolean"
    }

    with pytest.raises(RefResolutionError):
        schema.resolver.resolve_from_url("#/definitions/AList/items/2")

    with pytest.raises(RefResolutionError):
        schema.resolver.resolve_from_url("#/properties/bar/key")

    with pytest.raises(RefResolutionError):
        schema.resolver.resolve_from_url("test#/properties/bar/key")

    with pytest.raises(RefResolutionError):
        schema.resolver.pop_scope()
        schema.resolver.pop_scope()
