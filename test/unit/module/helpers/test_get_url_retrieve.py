"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, patch

import cfnlint.helpers


class TestGetUrlRetrieve(BaseTestCase):
    """Test Get URL Retrieve"""

    @patch("cfnlint.helpers.urlretrieve")
    def test_get_url_retrieve(self, mocked_urlretrieve):
        """Test the basics of URL retrieve"""

        mocked_urlretrieve.return_value = ("file/path", None)

        url = "http://foo.com"
        result = cfnlint.helpers.get_url_retrieve(url)
        mocked_urlretrieve.assert_called_with(url)
        self.assertEqual(result, "file/path")

    @patch("cfnlint.helpers.urlopen")
    @patch("cfnlint.helpers.load_metadata")
    @patch("cfnlint.helpers.save_metadata")
    @patch("cfnlint.helpers.urlretrieve")
    def test_get_url_retrieve_cached(
        self, mocked_urlretrieve, mock_save_metadata, mock_load_metadata, mocked_urlopen
    ):
        """Test the basics of URL retrieve"""
        etag = "ETAG_ONE"
        url = "http://foo.com"

        mock_load_metadata.return_value = {}

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.info.return_value = {"Content-Encoding": "gzip", "ETag": etag}
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        mocked_urlretrieve.return_value = ("file/path", None)

        result = cfnlint.helpers.get_url_retrieve(url, caching=True)
        mocked_urlretrieve.assert_called_with(url)
        mock_load_metadata.assert_called_once()
        mock_save_metadata.assert_called_once()
        self.assertEqual(result, "file/path")
