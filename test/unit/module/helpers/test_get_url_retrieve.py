"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

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

    @patch("cfnlint.helpers.get_metadata_filename")
    @patch("cfnlint.helpers.load_metadata")
    @patch("cfnlint.helpers.save_metadata")
    @patch("cfnlint.helpers.urlopen")
    def test_get_url_metadata_returns_without_persisting(
        self,
        mocked_urlopen,
        mock_save_metadata,
        mock_load_metadata,
        mock_get_metadata_filename,
    ):
        """get_url_metadata computes updated metadata but does not persist it"""
        url = "http://foo.com"
        mock_load_metadata.return_value = {}
        mock_get_metadata_filename.return_value = "metadata.json"

        cm = MagicMock()
        cm.info.return_value = {"ETag": "ETAG_ONE"}
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        result = cfnlint.helpers.get_url_metadata(url)

        self.assertEqual(result, ({"etag": "ETAG_ONE", "url": url}, "metadata.json"))
        mock_save_metadata.assert_not_called()

    @patch("cfnlint.helpers.urlopen")
    def test_get_url_metadata_returns_none_without_etag(self, mocked_urlopen):
        """get_url_metadata returns None when the response has no ETag"""
        cm = MagicMock()
        cm.info.return_value = {}
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm

        self.assertIsNone(cfnlint.helpers.get_url_metadata("http://foo.com"))

    @patch("cfnlint.helpers.time.sleep")
    @patch("cfnlint.helpers.urlretrieve")
    def test_get_url_retrieve_retries_transient_error(
        self, mocked_urlretrieve, mocked_sleep
    ):
        """A transient connection reset is retried and then succeeds"""
        url = "http://foo.com"
        mocked_urlretrieve.side_effect = [
            URLError("Remote end closed connection without response"),
            ("file/path", None),
        ]

        result = cfnlint.helpers.get_url_retrieve(url)

        self.assertEqual(result, "file/path")
        self.assertEqual(mocked_urlretrieve.call_count, 2)
        mocked_sleep.assert_called_once()

    @patch("cfnlint.helpers.time.sleep")
    @patch("cfnlint.helpers.urlretrieve")
    def test_get_url_retrieve_raises_after_exhausting_retries(
        self, mocked_urlretrieve, mocked_sleep
    ):
        """A persistent transient error is retried up to the limit then raised"""
        url = "http://foo.com"
        mocked_urlretrieve.side_effect = URLError("connection reset")

        with self.assertRaises(URLError):
            cfnlint.helpers.get_url_retrieve(url)

        self.assertEqual(mocked_urlretrieve.call_count, 3)
        self.assertEqual(mocked_sleep.call_count, 2)

    @patch("cfnlint.helpers.time.sleep")
    @patch("cfnlint.helpers.urlretrieve")
    def test_get_url_retrieve_does_not_retry_client_error(
        self, mocked_urlretrieve, mocked_sleep
    ):
        """A deterministic HTTP 404 is not retried"""
        url = "http://foo.com"
        mocked_urlretrieve.side_effect = HTTPError(
            url, 404, "Not Found", hdrs=None, fp=None
        )

        with self.assertRaises(HTTPError):
            cfnlint.helpers.get_url_retrieve(url)

        mocked_urlretrieve.assert_called_once()
        mocked_sleep.assert_not_called()
