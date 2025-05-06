import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import mock_open, patch

from cfnlint.schema._patch import patch as schema_patch
from cfnlint.schema.manager import ProviderSchemaManager

LOGGER = logging.getLogger("cfnlint.schema.manager")
LOGGER.disabled = True


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
