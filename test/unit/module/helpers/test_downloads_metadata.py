"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from test.testlib.testcase import BaseTestCase
from unittest.mock import mock_open, patch

import cfnlint.helpers


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
