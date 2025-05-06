"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
import os
from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, mock_open, patch

from cfnlint.schema._patch import SchemaPatch
from cfnlint.schema.other_schema_manager import OtherSchemaManager, SchemaNotFoundError

LOGGER = logging.getLogger("cfnlint.schema.other_schema_manager")
LOGGER.disabled = True


class TestOtherSchemaManager(BaseTestCase):
    """Used for Testing Other Schema Manager"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = OtherSchemaManager()
        self.test_schema = {
            "type": "object",
            "properties": {"test": {"type": "string"}},
        }
        self.schema_patch = [
            {"op": "add", "path": "/additionalProperties", "value": False}
        ]

    @patch("cfnlint.schema.other_schema_manager.load_resource")
    def test_get_schema(self, mock_load_resource):
        """Test getting a schema"""
        mock_load_resource.return_value = self.test_schema

        # First call should load from resource
        schema = self.manager.get_schema("other.functions.join")
        self.assertEqual(schema, self.test_schema)
        mock_load_resource.assert_called_once()

        # Second call should use cached value
        schema = self.manager.get_schema("other.functions.join")
        self.assertEqual(schema, self.test_schema)
        mock_load_resource.assert_called_once()  # Still only called once

    @patch("cfnlint.schema.other_schema_manager.load_resource")
    def test_get_schema_not_found(self, mock_load_resource):
        """Test getting a schema that doesn't exist"""
        mock_load_resource.side_effect = Exception("Schema not found")

        with self.assertRaises(SchemaNotFoundError):
            self.manager.get_schema("nonexistent.schema")

    @patch("cfnlint.schema.other_schema_manager.load_resource")
    def test_reset(self, mock_load_resource):
        """Test resetting the cache"""
        mock_load_resource.return_value = self.test_schema

        # Load schema into cache
        self.manager.get_schema("other.functions.join")
        mock_load_resource.assert_called_once()

        # Reset cache
        self.manager.reset()

        # Should load from resource again
        self.manager.get_schema("other.functions.join")
        self.assertEqual(mock_load_resource.call_count, 2)

    @patch("cfnlint.schema.other_schema_manager.load_resource")
    @patch("cfnlint.schema.other_schema_manager.jsonpatch.JsonPatch")
    def test_patch(self, mock_json_patch, mock_load_resource):
        """Test patching a schema"""
        mock_load_resource.return_value = self.test_schema
        mock_patch = MagicMock()
        mock_json_patch.return_value = mock_patch

        # Load schema
        self.manager.get_schema("other.functions.join")

        # Create patch
        patch = SchemaPatch([], [], {"other.functions.join": self.schema_patch})

        # Apply patch
        self.manager.patch(patch, "us-east-1")

        # Verify patch was applied
        mock_json_patch.assert_called_with(self.schema_patch)
        mock_patch.apply.assert_called_once()

    @patch("cfnlint.schema.other_schema_manager.load_resource")
    @patch("cfnlint.schema.other_schema_manager.jsonpatch.JsonPatch")
    def test_patch_schema_not_found(self, mock_json_patch, mock_load_resource):
        """Test patching a schema that doesn't exist"""
        mock_load_resource.side_effect = Exception("Schema not found")
        mock_patch = MagicMock()
        mock_json_patch.return_value = mock_patch

        # Create patch for non-existent schema
        patch = SchemaPatch([], [], {"nonexistent.schema": self.schema_patch})

        # Apply patch - should not raise an exception
        self.manager.patch(patch, "us-east-1")

        # Verify patch was not applied
        mock_patch.apply.assert_not_called()

    @patch("cfnlint.schema.other_schema_manager.open", new_callable=mock_open)
    @patch("cfnlint.schema.other_schema_manager.os.walk")
    @patch("cfnlint.schema.other_schema_manager.os.path.join")
    def test_load_registry_schemas(self, mock_path_join, mock_walk, mock_open_file):
        """Test loading registry schemas"""
        # Setup mock for os.walk to return one file
        mock_walk.return_value = [
            (os.path.normpath("/path/to/schemas"), [], ["test.json"])
        ]

        # Setup mock for os.path.join to return platform-appropriate paths
        mock_path_join.return_value = os.path.normpath("/path/to/schemas/test.json")

        # Setup mock for open to return a file with test schema
        mock_open_file.return_value.__enter__.return_value.read.return_value = (
            json.dumps(self.test_schema)
        )

        # Mock json.load to return our test schema
        with patch(
            "cfnlint.schema.other_schema_manager.json.load",
            return_value=self.test_schema,
        ):
            self.manager.load_registry_schemas(os.path.normpath("/path/to/schemas"))

        # Verify schema was loaded
        self.assertEqual(
            self.manager._schemas[os.path.normpath("/path/to/schemas")],
            self.test_schema,
        )

        # Verify open was called with correct path
        mock_open_file.assert_called_with(
            os.path.normpath("/path/to/schemas/test.json"), "r", encoding="utf-8"
        )
