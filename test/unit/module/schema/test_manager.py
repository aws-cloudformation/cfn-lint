"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import io
import json
import logging
import shutil
import zipfile
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, patch

from cfnlint.helpers import get_cache_dir
from cfnlint.schema._patch import SchemaPatch
from cfnlint.schema.manager import ProviderSchemaManager, ResourceNotFoundError

_fixtures_dir = Path(__file__).parent.parent.parent.parent / "fixtures" / "schemas"
_default_providers_dir = Path(get_cache_dir()) / "providers"
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


class TestInitWithExplicitDirs(BaseTestCase):
    """Test __init__ with explicit providers_dir/resources_dir"""

    def test_explicit_providers_dir(self):
        """Explicit providers_dir is used directly"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            providers = Path(tmpdir) / "p"
            providers.mkdir()
            (providers / "us-east-1.json").write_text(
                json.dumps({"AWS::S3::Bucket": "abc123"})
            )
            resources = Path(tmpdir) / "r"
            resources.mkdir()
            mgr = ProviderSchemaManager(
                providers_dir=providers, resources_dir=resources
            )
            self.assertEqual(mgr._providers_dir, providers)
            self.assertEqual(mgr._resources_dir, resources)


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
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_force(self, mock_cache_dir, mock_get_url, mock_url_newer):
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
            mock_cache_dir.return_value = tmpdir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            mock_get_url.assert_called_once()
            self.assertTrue((Path(tmpdir) / "providers" / "us-east-1.json").exists())
            self.assertTrue((Path(tmpdir) / "resources" / "abc123.json").exists())

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
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_extracts_sam_json(
        self, mock_cache_dir, mock_get_url, mock_url_newer
    ):
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
            mock_cache_dir.return_value = tmpdir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            self.assertTrue((Path(tmpdir) / "providers" / "sam.json").exists())
            self.assertTrue((Path(tmpdir) / "resources" / "sam123.json").exists())


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


class TestReadSchemaDate(BaseTestCase):
    """Test _read_schema_date"""

    def test_reads_valid_version_json(self):
        """Returns schema_date from a valid version.json"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            version_file = Path(tmpdir) / "version.json"
            version_file.write_text(json.dumps({"schema_date": "2026-07-07T14:23:15Z"}))
            result = ProviderSchemaManager._read_schema_date(Path(tmpdir))
            self.assertEqual(result, "2026-07-07T14:23:15Z")

    def test_returns_empty_when_missing(self):
        """Returns empty string when version.json doesn't exist"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            result = ProviderSchemaManager._read_schema_date(Path(tmpdir))
            self.assertEqual(result, "")

    def test_returns_empty_on_invalid_json(self):
        """Returns empty string on malformed JSON"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            version_file = Path(tmpdir) / "version.json"
            version_file.write_text("not valid json{{{")
            result = ProviderSchemaManager._read_schema_date(Path(tmpdir))
            self.assertEqual(result, "")

    def test_returns_empty_when_field_missing(self):
        """Returns empty string when schema_date field is absent"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            version_file = Path(tmpdir) / "version.json"
            version_file.write_text(json.dumps({"other": "data"}))
            result = ProviderSchemaManager._read_schema_date(Path(tmpdir))
            self.assertEqual(result, "")


class TestResolveSchemaDirs(BaseTestCase):
    """Test _resolve_schema_dirs"""

    @patch("cfnlint.schema.manager.get_cache_dir")
    @patch("cfnlint.schema.manager.os.path.dirname")
    def test_cache_only(self, mock_dirname, mock_cache_dir):
        """When no bundled schemas exist, returns cache dirs"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir
            mock_dirname.return_value = str(Path(tmpdir) / "nonexistent")
            providers, resources = ProviderSchemaManager._resolve_schema_dirs()
            self.assertEqual(providers, Path(tmpdir) / "providers")
            self.assertEqual(resources, Path(tmpdir) / "resources")

    @patch("cfnlint.schema.manager.get_cache_dir")
    @patch("cfnlint.schema.manager.os.path.dirname")
    def test_cache_wins_when_newer(self, mock_dirname, mock_cache_dir):
        """Cache wins when its schema_date is newer than bundled"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_schema_dir = Path(tmpdir) / "pkg" / "schema"
            pkg_schema_dir.mkdir(parents=True)
            pkg_data = pkg_schema_dir / ".." / "data" / "schemas"
            pkg_providers = pkg_data / "providers"
            pkg_providers.mkdir(parents=True)
            (pkg_providers / "us-east-1.json").write_text("{}")
            (pkg_data / "version.json").write_text(
                json.dumps({"schema_date": "2026-07-01T00:00:00Z"})
            )

            cache_dir = Path(tmpdir) / "cache"
            cache_dir.mkdir()
            cache_providers = cache_dir / "providers"
            cache_providers.mkdir()
            (cache_providers / "us-east-1.json").write_text("{}")
            (cache_dir / "version.json").write_text(
                json.dumps({"schema_date": "2026-07-07T14:00:00Z"})
            )

            mock_dirname.return_value = str(pkg_schema_dir)
            mock_cache_dir.return_value = str(cache_dir)

            providers, resources = ProviderSchemaManager._resolve_schema_dirs()

            self.assertEqual(providers, cache_providers)

    @patch("cfnlint.schema.manager.get_cache_dir")
    @patch("cfnlint.schema.manager.os.path.dirname")
    def test_bundled_wins_when_newer(self, mock_dirname, mock_cache_dir):
        """Bundled wins when its schema_date is newer than cache"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_schema_dir = Path(tmpdir) / "pkg" / "schema"
            pkg_schema_dir.mkdir(parents=True)
            pkg_data = pkg_schema_dir / ".." / "data" / "schemas"
            pkg_providers = pkg_data / "providers"
            pkg_providers.mkdir(parents=True)
            (pkg_providers / "us-east-1.json").write_text("{}")
            (pkg_data / "version.json").write_text(
                json.dumps({"schema_date": "2026-07-07T14:00:00Z"})
            )

            cache_dir = Path(tmpdir) / "cache"
            cache_dir.mkdir()
            cache_providers = cache_dir / "providers"
            cache_providers.mkdir()
            (cache_providers / "us-east-1.json").write_text("{}")
            (cache_dir / "version.json").write_text(
                json.dumps({"schema_date": "2026-07-01T00:00:00Z"})
            )

            mock_dirname.return_value = str(pkg_schema_dir)
            mock_cache_dir.return_value = str(cache_dir)

            providers, resources = ProviderSchemaManager._resolve_schema_dirs()

            self.assertEqual(providers, pkg_providers)

    @patch("cfnlint.schema.manager.get_cache_dir")
    @patch("cfnlint.schema.manager.os.path.dirname")
    def test_bundled_only_no_cache(self, mock_dirname, mock_cache_dir):
        """Bundled schemas used when cache is empty"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_schema_dir = Path(tmpdir) / "pkg" / "schema"
            pkg_schema_dir.mkdir(parents=True)
            pkg_data = pkg_schema_dir / ".." / "data" / "schemas"
            pkg_providers = pkg_data / "providers"
            pkg_providers.mkdir(parents=True)
            (pkg_providers / "us-east-1.json").write_text("{}")

            cache_dir = Path(tmpdir) / "cache"
            cache_dir.mkdir()

            mock_dirname.return_value = str(pkg_schema_dir)
            mock_cache_dir.return_value = str(cache_dir)

            providers, resources = ProviderSchemaManager._resolve_schema_dirs()

            self.assertEqual(providers, pkg_providers)


class TestUpdateDownloadsVersionJson(BaseTestCase):
    """Test that update() fetches version.json"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = _make_manager()

    @patch("cfnlint.schema.manager.get_url_content")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_version_json_saved(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_get_content
    ):
        """update() saves version.json to cache"""
        import tempfile
        from pathlib import Path

        mock_url_newer.return_value = False
        mock_get_content.return_value = '{"schema_date": "2026-07-07T14:23:15Z"}'

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
            mock_cache_dir.return_value = tmpdir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            version_file = Path(tmpdir) / "version.json"
            self.assertTrue(version_file.exists())
            with open(version_file) as f:
                data = json.load(f)
            self.assertEqual(data["schema_date"], "2026-07-07T14:23:15Z")

    @patch("cfnlint.schema.manager.get_url_content")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_version_json_failure_non_fatal(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_get_content
    ):
        """update() succeeds even if version.json download fails"""
        import tempfile
        from pathlib import Path

        mock_url_newer.return_value = False
        mock_get_content.side_effect = Exception("Network error")

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
            mock_cache_dir.return_value = tmpdir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            self.assertFalse((Path(tmpdir) / "version.json").exists())


class TestAtomicDirectoryReplace(BaseTestCase):
    """Test _atomic_replace_dir method"""

    def test_replaces_existing_dir(self):
        """Atomically replaces existing directory"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            dst = Path(tmpdir) / "dst"

            src.mkdir()
            (src / "new.txt").write_text("new content")

            dst.mkdir()
            (dst / "old.txt").write_text("old content")

            ProviderSchemaManager._atomic_replace_dir(src, dst)

            self.assertTrue(dst.exists())
            self.assertFalse(src.exists())
            self.assertTrue((dst / "new.txt").exists())
            self.assertFalse((dst / "old.txt").exists())
            self.assertEqual((dst / "new.txt").read_text(), "new content")

    def test_creates_dst_when_missing(self):
        """Creates destination when it doesn't exist"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            dst = Path(tmpdir) / "dst"

            src.mkdir()
            (src / "file.txt").write_text("content")

            ProviderSchemaManager._atomic_replace_dir(src, dst)

            self.assertTrue(dst.exists())
            self.assertTrue((dst / "file.txt").exists())

    def test_cleans_stale_backup(self):
        """Removes stale .bak directory from previous failed update"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            dst = Path(tmpdir) / "dst"
            backup = Path(tmpdir) / "dst.bak"

            src.mkdir()
            (src / "new.txt").write_text("new")

            dst.mkdir()
            (dst / "current.txt").write_text("current")

            backup.mkdir()
            (backup / "stale.txt").write_text("stale")

            ProviderSchemaManager._atomic_replace_dir(src, dst)

            self.assertFalse(backup.exists())
            self.assertTrue(dst.exists())
            self.assertTrue((dst / "new.txt").exists())

    @patch("cfnlint.schema.manager.shutil.move")
    def test_falls_back_to_shutil_on_rename_failure(self, mock_shutil_move):
        """Falls back to shutil.move when rename fails (e.g., cross-device)"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            dst = Path(tmpdir) / "dst"

            src.mkdir()
            (src / "file.txt").write_text("content")

            # Make the first rename fail but shutil.move succeed
            original_rename = Path.rename

            def failing_rename(self, target):
                raise OSError("Cross-device link")

            with patch.object(Path, "rename", failing_rename):
                # shutil.move will actually be called
                mock_shutil_move.side_effect = lambda s, d: original_rename(
                    Path(s), Path(d)
                )
                ProviderSchemaManager._atomic_replace_dir(src, dst)

            # shutil.move should have been called for src -> dst
            self.assertTrue(mock_shutil_move.called)
            self.assertTrue(dst.exists())

    def test_handles_both_renames_failing(self):
        """Handles case where both dst->backup and src->dst need shutil"""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src"
            dst = Path(tmpdir) / "dst"

            src.mkdir()
            (src / "new.txt").write_text("new")

            dst.mkdir()
            (dst / "old.txt").write_text("old")

            # Track shutil.move calls
            move_calls = []
            original_move = shutil.move

            def tracking_move(s, d):
                move_calls.append((s, d))
                return original_move(s, d)

            # Force all renames to fail
            with patch.object(Path, "rename", side_effect=OSError("Cross-device")):
                with patch(
                    "cfnlint.schema.manager.shutil.move", side_effect=tracking_move
                ):
                    ProviderSchemaManager._atomic_replace_dir(src, dst)

            # Both moves should have been called via shutil
            self.assertEqual(len(move_calls), 2)
            self.assertTrue(dst.exists())
            self.assertTrue((dst / "new.txt").exists())


class TestUpdateWithLocking(BaseTestCase):
    """Test update() with file locking"""

    def setUp(self) -> None:
        super().setUp()
        self.manager = _make_manager()

    @patch("cfnlint.schema.manager.file_lock")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_acquires_lock(self, mock_cache_dir, mock_url_newer, mock_file_lock):
        """update() acquires file lock before modifying cache"""
        import tempfile
        from pathlib import Path
        from unittest.mock import MagicMock

        mock_url_newer.return_value = True
        mock_lock_context = MagicMock()
        mock_file_lock.return_value.__enter__ = MagicMock(
            return_value=mock_lock_context
        )
        mock_file_lock.return_value.__exit__ = MagicMock(return_value=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir

            with patch.object(
                self.manager, "_update_locked", return_value=0
            ) as mock_update_locked:
                result = self.manager.update(force=True)

            self.assertEqual(result, 0)
            mock_file_lock.assert_called_once()
            lock_path = mock_file_lock.call_args[0][0]
            self.assertEqual(lock_path, Path(tmpdir) / ".update.lock")
            mock_update_locked.assert_called_once()

    @patch("cfnlint.schema.manager.LOGGER")
    @patch("cfnlint.schema.manager.file_lock")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_handles_lock_timeout(
        self, mock_cache_dir, mock_url_newer, mock_file_lock, mock_logger
    ):
        """update() returns 2 and logs a timeout-specific message on lock timeout"""
        import tempfile

        mock_url_newer.return_value = True
        mock_file_lock.side_effect = TimeoutError("Lock timeout")

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir
            result = self.manager.update(force=True)

        self.assertEqual(result, 2)
        logged = " ".join(str(c) for c in mock_logger.error.call_args_list)
        self.assertIn("Timed out waiting", logged)

    @patch("cfnlint.schema.manager.LOGGER")
    @patch("cfnlint.schema.manager.file_lock")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_handles_lock_oserror(
        self, mock_cache_dir, mock_url_newer, mock_file_lock, mock_logger
    ):
        """update() returns 2 and logs a lock-acquisition message on OSError"""
        import tempfile

        mock_url_newer.return_value = True
        mock_file_lock.side_effect = OSError("Permission denied")

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir
            result = self.manager.update(force=True)

        self.assertEqual(result, 2)
        logged = " ".join(str(c) for c in mock_logger.error.call_args_list)
        self.assertIn("Failed to acquire schema cache lock", logged)

    @patch("cfnlint.schema.manager.LOGGER")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_extract_failure_not_labeled_as_lock_error(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_logger
    ):
        """A corrupt download (BadZipFile) logs an extraction error, not a lock error"""
        import tempfile
        from pathlib import Path

        mock_url_newer.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir

            # Write a non-zip file to trigger BadZipFile during extraction
            bad_file = Path(tmpdir) / "corrupt.zip"
            bad_file.write_text("this is not a zip file")
            mock_get_url.return_value = str(bad_file)

            result = self.manager.update(force=True)

        self.assertEqual(result, 2)
        logged = " ".join(str(c) for c in mock_logger.error.call_args_list)
        # Must NOT be mislabeled as a lock failure
        self.assertNotIn("lock", logged.lower())
        self.assertIn("extract and install", logged)

    @patch("cfnlint.schema.manager.LOGGER")
    @patch("cfnlint.schema.manager.ProviderSchemaManager._atomic_replace_dir")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_atomic_replace_failure_not_labeled_as_lock_error(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_replace, mock_logger
    ):
        """An OSError during atomic replace logs an install error, not a lock error"""
        import tempfile

        mock_url_newer.return_value = True
        mock_replace.side_effect = OSError("Disk full")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr(
                "providers/us-east-1.json",
                json.dumps({"AWS::S3::Bucket": "abc123"}),
            )
        zip_buffer.seek(0)

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

        self.assertEqual(result, 2)
        logged = " ".join(str(c) for c in mock_logger.error.call_args_list)
        self.assertNotIn("lock", logged.lower())
        self.assertIn("extract and install", logged)

    @patch("cfnlint.schema.manager.get_url_content")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_rechecks_version_under_lock(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_get_content
    ):
        """update() re-checks version under lock (another process may have updated)"""
        import tempfile

        # First check returns True (needs update), second check under lock returns False
        mock_url_newer.side_effect = [True, False]

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir
            result = self.manager.update(force=False)

        self.assertEqual(result, 0)
        # Should not have tried to download
        mock_get_url.assert_not_called()

    @patch("cfnlint.schema.manager.LOGGER")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_initial_version_check_network_error(
        self, mock_cache_dir, mock_url_newer, mock_logger
    ):
        """A network error on the initial version check is not a lock error"""
        import tempfile
        import urllib.error

        mock_url_newer.side_effect = urllib.error.URLError("network down")

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir
            result = self.manager.update(force=False)

        self.assertEqual(result, 2)
        logged = " ".join(str(c) for c in mock_logger.error.call_args_list)
        self.assertNotIn("lock", logged.lower())
        self.assertIn("Failed to check schema version", logged)

    @patch("cfnlint.schema.manager.get_url_content")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_force_bypasses_version_check(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_get_content
    ):
        """force=True downloads without calling the version check at all"""
        import tempfile
        import urllib.error

        # Any version-check call would fail; force must bypass it entirely
        mock_url_newer.side_effect = urllib.error.URLError("network down")
        mock_get_content.side_effect = urllib.error.URLError("network down")

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
            mock_cache_dir.return_value = tmpdir

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                result = self.manager.update(force=True)

        self.assertEqual(result, 0)
        # force must short-circuit — the version check is never invoked
        mock_url_newer.assert_not_called()

    @patch("cfnlint.schema.manager.LOGGER")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_update_recheck_version_network_error_not_labeled_as_lock(
        self, mock_cache_dir, mock_url_newer, mock_logger
    ):
        """A network error on the under-lock version re-check is not a lock error"""
        import tempfile
        import urllib.error

        # First check (pre-lock) succeeds; re-check under lock raises URLError
        mock_url_newer.side_effect = [True, urllib.error.URLError("network down")]

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir
            result = self.manager.update(force=False)

        self.assertEqual(result, 2)
        logged = " ".join(str(c) for c in mock_logger.error.call_args_list)
        self.assertNotIn("lock", logged.lower())
        self.assertIn("Failed to check schema version", logged)


class TestConcurrentUpdate(BaseTestCase):
    """Test concurrent update() calls don't corrupt the cache"""

    @patch("cfnlint.schema.manager.get_url_content")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_concurrent_updates_serialize(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_get_content
    ):
        """Multiple concurrent update() calls serialize via lock"""
        import tempfile
        import threading
        from pathlib import Path

        # Always report newer version available (simulates cold cache)
        mock_url_newer.return_value = True
        mock_get_content.return_value = '{"schema_date": "2026-07-27"}'

        # Create a test zip file
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

        results = []
        errors = []

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir

            # Write the zip to a temp file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                def worker(worker_id):
                    try:
                        manager = ProviderSchemaManager()
                        result = manager.update(force=True)
                        results.append((worker_id, result))
                    except Exception as e:
                        errors.append((worker_id, str(e)))

                # Start 4 concurrent updates
                threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

            # All should succeed
            self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
            self.assertEqual(len(results), 4)
            for worker_id, result in results:
                self.assertEqual(result, 0, f"Worker {worker_id} failed with {result}")

            # Cache should be valid
            providers_dir = Path(tmpdir) / "providers"
            resources_dir = Path(tmpdir) / "resources"
            self.assertTrue(providers_dir.exists())
            self.assertTrue(resources_dir.exists())
            self.assertTrue((providers_dir / "us-east-1.json").exists())
            self.assertTrue((resources_dir / "abc123.json").exists())

    @patch("cfnlint.schema.manager.get_url_content")
    @patch("cfnlint.schema.manager.url_has_newer_version")
    @patch("cfnlint.schema.manager.get_url_retrieve")
    @patch("cfnlint.schema.manager.get_cache_dir")
    def test_concurrent_reads_during_update(
        self, mock_cache_dir, mock_get_url, mock_url_newer, mock_get_content
    ):
        """Readers see consistent state during concurrent update"""
        import tempfile
        import threading
        import time
        from pathlib import Path

        mock_url_newer.return_value = True
        mock_get_content.return_value = '{"schema_date": "2026-07-27"}'

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

        read_results = []
        read_errors = []

        with tempfile.TemporaryDirectory() as tmpdir:
            mock_cache_dir.return_value = tmpdir

            # Pre-populate cache with initial data
            providers_dir = Path(tmpdir) / "providers"
            resources_dir = Path(tmpdir) / "resources"
            providers_dir.mkdir()
            resources_dir.mkdir()
            (providers_dir / "us-east-1.json").write_text(
                json.dumps({"AWS::EC2::VPC": "old123"})
            )
            (resources_dir / "old123.json").write_text(
                json.dumps({"typeName": "AWS::EC2::VPC", "properties": {}})
            )

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(zip_buffer.getvalue())
                tmp.flush()
                mock_get_url.return_value = tmp.name

                update_started = threading.Event()
                update_done = threading.Event()

                def updater():
                    update_started.set()
                    manager = ProviderSchemaManager()
                    manager.update(force=True)
                    update_done.set()

                def reader(reader_id):
                    update_started.wait()
                    try:
                        # Try to read while update might be in progress
                        for _ in range(5):
                            provider_file = providers_dir / "us-east-1.json"
                            if provider_file.exists():
                                content = provider_file.read_text()
                                # Content should be valid JSON (not partial)
                                data = json.loads(content)
                                read_results.append(
                                    (reader_id, "ok", list(data.keys()))
                                )
                            time.sleep(0.01)
                    except json.JSONDecodeError as e:
                        read_errors.append((reader_id, "json_error", str(e)))
                    except FileNotFoundError:
                        # This is acceptable during atomic swap
                        read_results.append((reader_id, "not_found", None))
                    except Exception as e:
                        read_errors.append((reader_id, "error", str(e)))

                threads = [threading.Thread(target=updater)]
                threads += [
                    threading.Thread(target=reader, args=(i,)) for i in range(3)
                ]

                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

            # No JSON decode errors (would indicate partial write)
            json_errors = [e for e in read_errors if e[1] == "json_error"]
            self.assertEqual(
                len(json_errors), 0, f"Partial writes detected: {json_errors}"
            )
