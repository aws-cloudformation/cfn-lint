"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from unittest import TestCase

from cfnlint.schema.schema import Schema

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


class TestSchema(TestCase):
    """Used for Testing Schema"""

    def test_get_atts(self) -> None:
        r_schema = {
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

        schema = Schema(schema=r_schema)
        self.assertListEqual(list(schema.get_atts.keys()), ["Arn", "Id", "List"])
        self.assertEqual(schema.get_atts["Arn"].type, "string")
        self.assertEqual(schema.get_atts["Id"].type, "string")
        self.assertEqual(schema.get_atts["List"].type, "array")
        self.assertEqual(schema.get_atts["List"].item_type, "string")

        self.assertDictEqual(
            schema.json_schema,
            {
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
                },
                "readOnlyProperties": [
                    "/properties/Arn",
                    "/properties/Id",
                    "/properties/List",
                ],
                "typeName": "AWS::NetworkFirewall::Firewall",
            },
        )
