"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from test.testlib.testcase import BaseTestCase

from cfnlint.schema._pointer import resolve_pointer

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
                }
            },
            "properties": {
                "foo": {"type": "string"},
                "bar": {"$ref": "#/definitions/bar"},
                "fooBars": {"type": "array", "items": {"$ref": "#/definitions/fooBar"}},
            },
        }

    def test_pointer(self):
        self.assertEqual(
            resolve_pointer(self.schema, "/properties/foo"), {"type": "string"}
        )
        self.assertEqual(
            resolve_pointer(self.schema, "/properties/fooBars/*/a"),
            {"items": {"type": "string"}, "type": "array"},
        )

        with self.assertRaises(KeyError):
            resolve_pointer(self.schema, "/properties/bar/key")
