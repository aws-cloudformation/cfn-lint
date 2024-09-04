"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, call, mock_open, patch

from cfnlint.schema.manager import ProviderSchemaManager, ResourceNotFoundError
from cfnlint.schema.patch import SchemaPatch

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


class TestUpdateResourceSchemas(BaseTestCase):
    """Used for Testing Resource Schemas"""

    def setUp(self) -> None:
        super().setUp()

        self.schema_zip = "test/fixtures/registry/schema.zip"
        self.manager = ProviderSchemaManager()
        self.schemas = dict.fromkeys(["aws-lambda-codesigningconfig"])
        for resource in self.schemas:
            with open(f"test/fixtures/registry/schemas/{resource}.json") as fh:
                self.schemas[resource] = fh.read()

        self.schema_patch = [{"op": "add", "path": "/cfnSchema", "value": ["test"]}]

    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.json.dump")
    @patch("cfnlint.schema.manager.REGIONS", ["us-east-1"])
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.zipfile.ZipFile")
    @patch("cfnlint.schema.manager.os.listdir")
    @patch("cfnlint.schema.manager.os.path.isfile")
    @patch("cfnlint.schema.manager.os.remove")
    @patch("cfnlint.schema.manager.os.walk")
    @patch("cfnlint.schema.manager.filecmp.cmp")
    @patch("cfnlint.schema.manager.load_resource")
    @patch("cfnlint.schema.manager.shutil.rmtree")
    def test_update_resource_spec(
        self,
        mock_shutil_rmtree,
        mock_load_resource,
        mock_filecmp_cmp,
        mock_os_walk,
        mock_os_remove,
        mock_os_path_isfile,
        mock_os_listdir,
        mock_zipfile,
        mock_get_url_retrieve,
        mock_json_dump,
        mock_url_newer_version,
    ):
        schema = self.schemas["aws-lambda-codesigningconfig"]
        schema_json = json.loads(schema)

        """Success update resource spec"""
        mock_url_newer_version.return_value = True
        mock_get_url_retrieve.return_value = self.schema_zip
        mock_zipfile.return_value = MagicMock()
        mock_os_listdir.return_value = [
            "aws_lambda_codesigningconfig.json",
            "__init__.py",
        ]
        mock_os_path_isfile.side_effect = [True, True, True, True]
        mock_load_resource.return_value = self.schema_patch
        mock_os_walk.return_value = iter(
            [("all", [], ["aws_lambda_codesigningconfig.json"])]
        )
        builtin_module_name = "builtins"

        with patch(
            "{}.open".format(builtin_module_name), mock_open(read_data=schema)
        ) as mock_builtin_open:
            self.manager._update_provider_schema("us-east-1", False)
            schema_patched = {**schema_json, **{"cfnSchema": ["test"]}}
            mock_json_dump.assert_called_with(
                schema_patched,
                mock_builtin_open.return_value.__enter__.return_value,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )
            mock_os_listdir.assert_has_calls(
                [
                    call(f"{self.manager._root.path_relative}/us_east_1/"),
                ]
            )
            mock_zipfile.assert_has_calls([call(self.schema_zip, "r")])
            mock_filecmp_cmp.assert_not_called()
            mock_os_remove.assert_not_called()

    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.json.dump")
    @patch("cfnlint.schema.manager.REGIONS", ["us-east-1"])
    @patch("cfnlint.schema.manager.load_resource")
    @patch("cfnlint.schema.manager.zipfile.ZipFile")
    @patch("cfnlint.schema.manager.os.listdir")
    @patch("cfnlint.schema.manager.os.path.isfile")
    @patch("cfnlint.schema.manager.os.remove")
    @patch("cfnlint.schema.manager.os.walk")
    @patch("cfnlint.schema.manager.filecmp.cmp")
    @patch("cfnlint.schema.manager.shutil.rmtree")
    def test_update_resource_spec_cache(
        self,
        mock_shutil_rmtree,
        mock_filecmp_cmp,
        mock_os_walk,
        mock_os_remove,
        mock_os_path_isfile,
        mock_os_listdir,
        mock_zipfile,
        mock_load_resource,
        mock_json_dump,
        mock_get_url_retrieve,
        mock_url_newer_version,
    ):
        """Success update resource spec with cache"""
        schema = self.schemas["aws-lambda-codesigningconfig"]
        schema_json = json.loads(schema)

        mock_url_newer_version.return_value = True
        mock_get_url_retrieve.return_value = self.schema_zip
        mock_zipfile.return_value = MagicMock()
        mock_os_listdir.return_value = [
            "aws-lambda-codesigningconfig.json",
            "__init__.py",
        ]
        mock_os_path_isfile.side_effect = [True, True, True, True]
        mock_filecmp_cmp.side_effect = [True]
        mock_load_resource.return_value = self.schema_patch
        mock_os_walk.return_value = iter(
            [("all", [], ["aws_lambda_codesigningconfig.json"])]
        )
        builtin_module_name = "builtins"

        with patch(
            "{}.open".format(builtin_module_name), mock_open(read_data=schema)
        ) as mock_builtin_open:
            self.manager._update_provider_schema("us-west-2", False)
            schema_patched = {**schema_json, **{"cfnSchema": ["test"]}}
            mock_json_dump.assert_called_with(
                schema_patched,
                mock_builtin_open.return_value.__enter__.return_value,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )
            mock_os_listdir.assert_has_calls(
                [
                    call(f"{self.manager._root.path_relative}/us_west_2/"),
                    call(f"{self.manager._root.path_relative}/us_west_2/"),
                ]
            )
            mock_zipfile.assert_has_calls([call(self.schema_zip, "r")])
            mock_filecmp_cmp.assert_called_once()
            mock_os_remove.assert_called_once()

    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.json.dump")
    @patch("cfnlint.schema.manager.ProviderSchemaManager._patch_provider_schema")
    @patch("cfnlint.schema.manager.REGIONS", {"us-east-1": []})
    def test_do_not_update_resource_spec(
        self,
        mock_provider_schema,
        mock_json_dump,
        mock_get_url_retrieve,
        mock_url_newer_version,
    ):
        """Success update resource spec"""

        mock_url_newer_version.return_value = False

        result = self.manager._update_provider_schema("us-east-1", False)
        self.assertIsNone(result)
        mock_get_url_retrieve.assert_not_called()
        mock_provider_schema.assert_not_called()
        mock_json_dump.assert_not_called()

    @patch("cfnlint.schema.manager.multiprocessing.Pool")
    @patch("cfnlint.schema.manager.ProviderSchemaManager._update_provider_schema")
    @patch("cfnlint.schema.manager.REGIONS", {"us-east-1": []})
    def test_update_resource_specs_python(self, mock_update_resource_spec, mock_pool):
        fake_pool = MagicMock()
        mock_pool.return_value.__enter__.return_value = fake_pool

        self.manager.update(True)

        fake_pool.starmap.assert_called_once()


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
                self.manager.patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    def test_patch_file_is_dir(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = IOError()
            err.errno = 21
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                self.manager.patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    def test_patch_permission_error(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = PermissionError()
            err.errno = 13
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                self.manager.patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)

    def test_patch_value_error(self):
        with patch("builtins.open", mock_open()) as mock_builtin_open:
            err = ValueError()
            mock_builtin_open.side_effect = [err]
            with self.assertRaises(SystemExit) as mock_exit:
                self.manager.patch("bad", regions=["us-east-1"])
                self.assertEqual(mock_exit.type, SystemExit)
                self.assertEqual(mock_exit.value.code == 1)


class TestManagerGetResourceSchema(BaseTestCase):
    """Test get resource schema"""

    def setUp(self) -> None:
        super().setUp()

        self.manager = ProviderSchemaManager()

    def test_getting_cached_schema(self):
        rt = "AWS::EC2::VPC"

        self.manager.get_resource_schema("us-east-1", rt)
        schema = self.manager.get_resource_schema("us-east-2", rt)

        self.assertTrue(schema.is_cached)

    def test_removed_types(self):
        rt = "AWS::EC2::VPC"
        region = "us-east-1"
        self.manager._patch(SchemaPatch([], [rt], {}), region)

        with self.assertRaises(ResourceNotFoundError):
            self.manager.get_resource_schema(region, rt)

    def test_type_normalization(self):

        rt = "MyCompany::MODULE"
        schema = self.manager.get_resource_schema("us-east-1", rt)

        assert schema.schema.get("typeName") == "Module"

        self.manager.get_resource_schema.cache_clear()
        self.manager._registry_schemas[rt] = True
        schema = self.manager.get_resource_schema("us-east-1", rt)
        assert schema is True
