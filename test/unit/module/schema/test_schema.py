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
