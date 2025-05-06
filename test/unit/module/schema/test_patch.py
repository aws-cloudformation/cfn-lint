import json
import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import mock_open, patch

from cfnlint.schema._patch import SchemaPatch
from cfnlint.schema._patch import patch as schema_patch
from cfnlint.schema._patch import reset
from cfnlint.schema.manager import ProviderSchemaManager

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


class TestSchemaPatch(BaseTestCase):
    """Test the SchemaPatch class"""

    def test_from_dict(self):
        """Test creating a SchemaPatch from a dictionary"""
        test_dict = {
            "IncludeResourceTypes": ["AWS::EC2::*"],
            "ExcludeResourceTypes": ["AWS::EC2::VPC"],
            "Patches": {
                "AWS::EC2::Instance": [
                    {"op": "add", "path": "/properties/test", "value": "value"}
                ]
            },
        }

        patch = SchemaPatch.from_dict(test_dict)

        self.assertEqual(patch.included_resource_types, ["AWS::EC2::*"])
        self.assertEqual(patch.excluded_resource_types, ["AWS::EC2::VPC"])
        self.assertEqual(
            patch.patches,
            {
                "AWS::EC2::Instance": [
                    {"op": "add", "path": "/properties/test", "value": "value"}
                ]
            },
        )

    def test_from_dict_empty(self):
        """Test creating a SchemaPatch from an empty dictionary"""
        test_dict = {}

        patch = SchemaPatch.from_dict(test_dict)

        self.assertEqual(patch.included_resource_types, [])
        self.assertEqual(patch.excluded_resource_types, [])
        self.assertEqual(patch.patches, {})


class TestReset(BaseTestCase):
    """Test the reset function"""

    @patch("cfnlint.schema._patch.PROVIDER_SCHEMA_MANAGER")
    @patch("cfnlint.schema._patch.OTHER_SCHEMA_MANAGER")
    def test_reset(self, mock_other_manager, mock_provider_manager):
        """Test that reset calls reset on both managers"""
        reset()

        mock_provider_manager.reset.assert_called_once()
        mock_other_manager.reset.assert_called_once()


class TestManagerPatch(BaseTestCase):
    """Used for Testing Resource Schemas"""

    def setUp(self) -> None:
        super().setUp()

        self.manager = ProviderSchemaManager()
        self.schemas = dict.fromkeys(["aws-lambda-codesigningconfig"])
        for resource in self.schemas:
            with open(f"test/fixtures/registry/schemas/{resource}.json") as fh:
                self.schemas[resource] = fh.read()

    def test_patch_file_not_found_error(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = FileNotFoundError()
            err.errno = 2
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                schema_patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    def test_patch_file_is_dir(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = IOError()
            err.errno = 21
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                schema_patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    def test_patch_permission_error(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = PermissionError()
            err.errno = 13
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                schema_patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    def test_patch_value_error(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = ValueError()
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                schema_patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    @patch("cfnlint.schema._patch.PROVIDER_SCHEMA_MANAGER")
    @patch("cfnlint.schema._patch.OTHER_SCHEMA_MANAGER")
    def test_patch_success(self, mock_other_manager, mock_provider_manager):
        """Test successful patching"""
        test_patch_data = {
            "IncludeResourceTypes": ["AWS::EC2::*"],
            "ExcludeResourceTypes": ["AWS::EC2::VPC"],
            "Patches": {
                "AWS::EC2::Instance": [
                    {"op": "add", "path": "/properties/test", "value": "value"}
                ]
            },
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(test_patch_data))):
            schema_patch("test_file.json", regions=["us-east-1", "us-west-2"])

            # Check that provider manager patch was called for each region
            self.assertEqual(mock_provider_manager.patch.call_count, 2)

            # Check that other manager patch was called once (with the last region)
            mock_other_manager.patch.assert_called_once()
