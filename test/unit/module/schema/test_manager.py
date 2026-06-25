"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import io
import json
import logging
import zipfile
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, patch

from cfnlint.schema._patch import SchemaPatch
from cfnlint.schema.manager import ProviderSchemaManager, ResourceNotFoundError

_fixtures_dir = Path(__file__).parent.parent.parent.parent / "fixtures" / "schemas"
_default_providers_dir = Path(__file__).parent.parent.parent.parent.parent / (
    "src/cfnlint/data/schemas/providers"
)
_has_full_schemas = _default_providers_dir.exists() and any(
    _default_providers_dir.glob("*.json")
)


def _make_manager() -> ProviderSchemaManager:
    if _has_full_schemas:
        return ProviderSchemaManager()
    return ProviderSchemaManager(
        providers_dir=_fixtures_dir / "providers",
        resources_dir=_fixtures_dir / "resources",
    )


LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


class TestUpdateResourceSchemas(BaseTestCase):
    """Used for Testing Resource Schemas"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = _make_manager()

    @patch("cfnlint.schema.manager.url_has_newer_version")
    def test_no_update_when_cached(self, mock_url_newer):
        """When ETag matches, skip download"""
        mock_url_newer.return_value = False
        result = self.manager.update(force=False)
        self.assertEqual(result, 0)

    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    def test_update_force(self, mock_get_url, mock_url_newer):
        """Force download even if cached"""
        import tempfile
        from pathlib import Path

        mock_url_newer.return_value = False

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr(
                "providers/us-east-1.json",
                json.dumps({"AWS::S3::Bucket": "abc123"}),
            )
            zf.writestr(
                "resources/abc123.json",
                json.dumps({"typeName": "AWS::S3::Bucket", "properties": {}}),
            )
        zip_buffer.seek(0)

        with tempfile.TemporaryDirectory() as tmpdir:
            providers_dir = Path(tmpdir) / "providers"
            resources_dir = Path(tmpdir) / "resources"
            providers_dir.mkdir()
            resources_dir.mkdir()

            self.manager._providers_dir = providers_dir
            self.manager._resources_dir = resources_dir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            mock_get_url.assert_called_once()
            self.assertTrue((providers_dir / "us-east-1.json").exists())
            self.assertTrue((resources_dir / "abc123.json").exists())

    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    def test_update_download_failure(self, mock_get_url, mock_url_newer):
        """Returns 2 on download failure"""
        mock_url_newer.return_value = True
        mock_get_url.side_effect = Exception("Network error")

        result = self.manager.update(force=False)
        self.assertEqual(result, 2)


class TestSamModuleLoading(BaseTestCase):
    """Test SAM schema module loading"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = _make_manager()

    def test_sam_module_missing_file(self):
        """Returns empty dict when sam.json doesn't exist"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            self.manager._providers_dir = Path(tmpdir)
            result = self.manager._load_sam_module()
            self.assertEqual(result, {})

    def test_sam_module_loads(self):
        """Loads SAM types from sam.json"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            providers_dir = Path(tmpdir)
            sam_data = {"AWS::Serverless::Function": "sam123"}
            (providers_dir / "sam.json").write_text(json.dumps(sam_data))

            self.manager._providers_dir = providers_dir
            self.manager._sam_schema_module = None
            result = self.manager._load_sam_module()
            self.assertEqual(result, sam_data)

    def test_sam_types_merged_into_provider(self):
        """SAM types are merged into region provider modules"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            providers_dir = Path(tmpdir)
            resources_dir = Path(tmpdir) / "resources"
            resources_dir.mkdir()

            region_data = {"AWS::S3::Bucket": "abc123"}
            sam_data = {"AWS::Serverless::Function": "sam123"}
            (providers_dir / "us-east-1.json").write_text(json.dumps(region_data))
            (providers_dir / "sam.json").write_text(json.dumps(sam_data))

            self.manager._providers_dir = providers_dir
            self.manager._resources_dir = resources_dir
            self.manager._sam_schema_module = None
            self.manager._provider_schema_modules = {}

            result = self.manager._load_provider_module("us-east-1")
            self.assertIn("AWS::S3::Bucket", result)
            self.assertIn("AWS::Serverless::Function", result)
            self.assertEqual(result["AWS::S3::Bucket"], "abc123")
            self.assertEqual(result["AWS::Serverless::Function"], "sam123")

    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    def test_update_extracts_sam_json(self, mock_get_url, mock_url_newer):
        """Update extracts sam.json from zip into providers dir"""
        import tempfile
        from pathlib import Path

        mock_url_newer.return_value = False

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr(
                "providers/us-east-1.json",
                json.dumps({"AWS::S3::Bucket": "abc123"}),
            )
            zf.writestr(
                "providers/sam.json",
                json.dumps({"AWS::Serverless::Function": "sam123"}),
            )
            zf.writestr(
                "resources/abc123.json",
                json.dumps({"typeName": "AWS::S3::Bucket", "properties": {}}),
            )
            zf.writestr(
                "resources/sam123.json",
                json.dumps({"typeName": "AWS::Serverless::Function", "properties": {}}),
            )
        zip_buffer.seek(0)

        with tempfile.TemporaryDirectory() as tmpdir:
            providers_dir = Path(tmpdir) / "providers"
            resources_dir = Path(tmpdir) / "resources"
            providers_dir.mkdir()
            resources_dir.mkdir()

            self.manager._providers_dir = providers_dir
            self.manager._resources_dir = resources_dir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            self.assertTrue((providers_dir / "sam.json").exists())
            self.assertTrue((resources_dir / "sam123.json").exists())


class TestAutoDownloadOnMissingSchemas(BaseTestCase):
    """Test that schemas are auto-downloaded when provider files are missing"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = _make_manager()

    @patch("cfnlint.schema.manager.ProviderSchemaManager.update")
    def test_auto_downloads_when_no_providers(self, mock_update):
        """When no provider files exist, update is called automatically"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            providers_dir = Path(tmpdir) / "providers"
            providers_dir.mkdir()

            self.manager._providers_dir = providers_dir
            self.manager._provider_schema_modules = {}

            self.manager._load_provider_module("us-east-1")
            mock_update.assert_called_once_with(force=False)

    @patch("cfnlint.schema.manager.ProviderSchemaManager.update")
    def test_no_auto_download_when_providers_exist(self, mock_update):
        """When provider files exist, update is not called"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            providers_dir = Path(tmpdir) / "providers"
            providers_dir.mkdir()
            (providers_dir / "us-east-1.json").write_text(
                json.dumps({"AWS::S3::Bucket": "abc123"})
            )

            self.manager._providers_dir = providers_dir
            self.manager._provider_schema_modules = {}
            self.manager._sam_schema_module = {}

            self.manager._load_provider_module("us-east-1")
            mock_update.assert_not_called()


class TestManagerGetResourceSchema(BaseTestCase):
    """Test get resource schema"""

    def setUp(self) -> None:
        super().setUp()

        self.manager = _make_manager()

    def test_getting_cached_schema(self):
        rt = "AWS::EC2::VPC"

        schema_east_1 = self.manager.get_resource_schema("us-east-1", rt)
        schema_east_2 = self.manager.get_resource_schema("us-east-2", rt)

        # Schemas should be identical (same hash)
        self.assertDictEqual(schema_east_1.schema, schema_east_2.schema)

    def test_removed_types(self):
        rt = "AWS::EC2::VPC"
        region = "us-east-1"
        self.manager.patch(SchemaPatch([], [rt], {}), region)

        with self.assertRaises(ResourceNotFoundError):
            self.manager.get_resource_schema(region, rt)

    def test_getting_us_east_1_schema_in_iso(self):
        rt = "AWS::EC2::VPC"

        schema_us_east_1 = self.manager.get_resource_schema("us-east-1", rt)
        schema_iso = self.manager.get_resource_schema("us-iso-east-1", rt)

        # ISO regions use us-east-1 schemas
        self.assertDictEqual(schema_us_east_1.schema, schema_iso.schema)

    def test_type_normalization(self):
        rt = "MyCompany::MODULE"
        schema = self.manager.get_resource_schema("us-east-1", rt)

        assert schema.schema.get("typeName") == "Module"

        self.manager.get_resource_schema.cache_clear()
        self.manager._registry_schemas[rt] = True
        schema = self.manager.get_resource_schema("us-east-1", rt)
        assert schema is True


class TestManagerPatch(BaseTestCase):
    """Test patching schemas"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = _make_manager()
        self.schema_patch = [{"op": "add", "path": "/cfnSchema", "value": ["test"]}]

    @patch("cfnlint.schema.manager.print")
    @patch("cfnlint.schema.manager.sys.exit")
    def test_patch_failure(self, mock_exit, mock_print):
        """Test when patching a schema fails"""
        mock_schema = MagicMock()
        mock_schema.patch.side_effect = Exception("Invalid patch operation")

        self.manager.get_resource_schema = MagicMock(return_value=mock_schema)

        resource_type = "AWS::EC2::Instance"
        patch = SchemaPatch([], [], {resource_type: self.schema_patch})

        self.manager.patch(patch, "us-east-1")

        mock_print.assert_called_with(
            f"Error applying patch {self.schema_patch} for "
            f"{resource_type}: Invalid patch operation"
        )

        mock_exit.assert_called_with(1)
