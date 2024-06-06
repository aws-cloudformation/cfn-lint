"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.testlib.testcase import BaseTestCase

from cfnlint.schema.resolver import RefResolver
from cfnlint.schema.resolver._exceptions import RefResolutionError

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


class TestPointer(BaseTestCase):
    """Used for Pointer"""

    def setUp(self) -> None:
        super().setUp()
        self.schema = {
            "typeName": "Test::Resource::Type",
            "definitions": {
                "fooBar": {
                    "type": "object",
                    "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
                },
                "anyOf": {
                    "anyOf": [
                        {"$ref": "#/definitions/fooBar"},
                        {
                            "type": "object",
                            "properties": {
                                "a": {"type": "boolean"},
                                "c": {"type": "boolean"},
                                "d": {"type": "boolean"},
                            },
                        },
                    ]
                },
            },
            "properties": {
                "foo": {"type": "string"},
                "bar": {"$ref": "#/definitions/bar"},
                "fooBars": {"type": "array", "items": {"$ref": "#/definitions/fooBar"}},
                "refFirst": {
                    "$ref": "#/definitions/fooBar",
                    "type": "object",
                    "properties": {
                        "a": {"type": "boolean"},
                    },
                },
                "anyOf": {"$ref": "#/definitions/anyOf"},
            },
        }

    def test_pointer(self):
        resolver = RefResolver(self.schema)
        self.assertEqual(
            resolver.resolve_cfn_pointer("/properties/foo"),
            {"type": "string"},
        )
        self.assertEqual(
            resolver.resolve_cfn_pointer("/properties/fooBars/*/a"),
            {"type": "string"},
        )

        # first one found is string (not boolean)
        self.assertEqual(
            resolver.resolve_cfn_pointer("/properties/anyOf/a"),
            {"type": "string"},
        )

        # second option in anyOf has the property we are looking for
        self.assertEqual(
            resolver.resolve_cfn_pointer("/properties/anyOf/c"),
            {"type": "boolean"},
        )

        # refs are handled first
        self.assertEqual(
            resolver.resolve_cfn_pointer("/properties/refFirst/a"),
            {"type": "string"},
        )

        with self.assertRaises(RefResolutionError):
            resolver.resolve_cfn_pointer("/properties/bar/key")
