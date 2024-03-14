"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import gzip
from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, patch

import cfnlint.helpers


class TestGetUrlContent(BaseTestCase):
    """Test Get URL Content"""

    @patch("cfnlint.helpers.urlopen")
    def test_get_url_content_unzipped(self, mocked_urlopen):
        """Test success run"""

        input_buffer = '{"key": "value"}'

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = input_buffer.encode("utf-8")
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        url = "http://foo.com"
        result = cfnlint.helpers.get_url_content(url)
        mocked_urlopen.assert_called_with(url)
        self.assertEqual(result, '{"key": "value"}')

    @patch("cfnlint.helpers.urlopen")
    def test_get_url_content_zipped(self, mocked_urlopen):
        """Test success run"""
        input_buffer = '{"key": "value"}'
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = gzip.compress(input_buffer.encode("utf-8"))

        cm.info.return_value = {"Content-Encoding": "gzip"}
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        url = "http://foo.com"
        result = cfnlint.helpers.get_url_content(url)
        mocked_urlopen.assert_called_with(url)
        self.assertEqual(result, '{"key": "value"}')

    @patch("cfnlint.helpers.urlopen")
    @patch("cfnlint.helpers.load_metadata")
    @patch("cfnlint.helpers.save_metadata")
    def test_get_url_content_zipped_cache_update(
        self, mock_save_metadata, mock_load_metadata, mocked_urlopen
    ):
        """Test success run"""
        input_buffer = '{"key": "value"}'
        etag = "ETAG_ONE"
        url = "http://foo.com"

        mock_load_metadata.return_value = {}

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.info.return_value = {"Content-Encoding": "gzip", "ETag": etag}

        cm.read.return_value = gzip.compress(input_buffer.encode("utf-8"))

        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        result = cfnlint.helpers.get_url_content(url, caching=True)
        mocked_urlopen.assert_called_with(url)
        mock_load_metadata.assert_called_once()
        mock_save_metadata.assert_called_once()

        self.assertEqual(result, '{"key": "value"}')

    @patch("cfnlint.helpers.urlopen")
    @patch("cfnlint.helpers.load_metadata")
    def test_url_has_newer_version_affirmative(
        self, mock_load_metadata, mocked_urlopen
    ):
        """Test success run"""

        etag = "ETAG_ONE"
        url = "http://foo.com"

        mock_load_metadata.return_value = {"etag": etag}

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.info.return_value = {"Content-Encoding": "gzip", "ETag": etag}

        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        result = cfnlint.helpers.url_has_newer_version(url)

        # Python2 does not support caching, so will always return true
        self.assertFalse(result)

    @patch("cfnlint.helpers.urlopen")
    @patch("cfnlint.helpers.load_metadata")
    def test_url_has_newer_version_negative(self, mock_load_metadata, mocked_urlopen):
        """Test success run"""

        # Generate a random ETag to test with
        etag = "ETAG_ONE"
        etag2 = "ETAG_TWO"

        url = "http://foo.com"
        mock_load_metadata.return_value = {"etag": etag}

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.info.return_value = {"Content-Encoding": "gzip", "ETag": etag2}
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        result = cfnlint.helpers.url_has_newer_version(url)
        self.assertTrue(result)
