"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import os
from test.testlib.testcase import BaseTestCase
from unittest.mock import mock_open, patch

import cfnlint.helpers
from cfnlint.helpers import get_cache_dir


class TestDownloadsMetadata(BaseTestCase):
    """Test Downloads Metadata"""

    @patch("cfnlint.helpers.os.path.exists")
    def test_no_file(self, mock_path_exists):
        """Test success run"""

        mock_path_exists.return_value = False

        filename = "foo.bar"

        result = cfnlint.helpers.load_metadata(filename)

        self.assertEqual(result, {})

    @patch("cfnlint.helpers.os.path.exists")
    def test_load_metadata(self, mock_path_exists):
        """Test success run"""

        mock_path_exists.return_value = True

        filename = "foo.bar"
        file_contents = {"etag": "foo"}

        builtin_module_name = "builtins"

        mo = mock_open(read_data=json.dumps(file_contents))
        with patch("{}.open".format(builtin_module_name), mo):
            result = cfnlint.helpers.load_metadata(filename)

            self.assertEqual(result, file_contents)

    @patch("cfnlint.helpers.os.path.dirname")
    @patch("cfnlint.helpers.os.makedirs")
    @patch("cfnlint.helpers.json.dump")
    def test_save_download_metadata(self, mock_json_dump, mock_makedirs, mock_dirname):
        """Test success run"""

        filename = "foo.bar"
        filedir = "foobardir"
        file_contents = {"etag": "foo"}

        mock_dirname.return_value = filedir

        builtin_module_name = "builtins"

        mo = mock_open()
        with patch("{}.open".format(builtin_module_name), mo):
            cfnlint.helpers.save_metadata(file_contents, filename)
            mock_makedirs.assert_called_with(filedir, exist_ok=True)
            mock_json_dump.assert_called_once


class TestGetCacheDir(BaseTestCase):
    """Test get_cache_dir platform logic"""

    @patch.object(cfnlint.helpers.sys, "platform", "linux")
    @patch.dict(os.environ, {}, clear=True)
    def test_linux_default(self):
        """Linux without XDG_CACHE_HOME uses ~/.cache"""
        result = get_cache_dir()
        expected = os.path.join(
            os.path.expanduser("~/.cache"), "aws", "cfn-lint", "schemas"
        )
        self.assertEqual(result, expected)

    @patch.object(cfnlint.helpers.sys, "platform", "linux")
    @patch.dict(os.environ, {"XDG_CACHE_HOME": "/home/user/.my-cache"}, clear=True)
    def test_linux_xdg(self):
        """Linux with XDG_CACHE_HOME respects it"""
        result = get_cache_dir()
        expected = os.path.join("/home/user/.my-cache", "aws", "cfn-lint", "schemas")
        self.assertEqual(result, expected)

    @patch.object(cfnlint.helpers.sys, "platform", "darwin")
    def test_macos(self):
        """macOS uses ~/Library/Caches"""
        result = get_cache_dir()
        expected = os.path.join(
            os.path.expanduser("~/Library/Caches"), "aws", "cfn-lint", "schemas"
        )
        self.assertEqual(result, expected)

    @patch.object(cfnlint.helpers.sys, "platform", "win32")
    @patch.dict(
        os.environ, {"LOCALAPPDATA": "C:\\Users\\test\\AppData\\Local"}, clear=True
    )
    def test_windows(self):
        """Windows uses LOCALAPPDATA"""
        result = get_cache_dir()
        expected = os.path.join(
            "C:\\Users\\test\\AppData\\Local", "aws", "cfn-lint", "schemas"
        )
        self.assertEqual(result, expected)
