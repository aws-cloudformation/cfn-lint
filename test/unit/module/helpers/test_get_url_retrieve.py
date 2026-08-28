"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import tempfile
from pathlib import Path
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

    @patch("cfnlint.helpers.get_metadata_filename")
    @patch("cfnlint.helpers.urlopen")
    @patch("cfnlint.helpers.urlretrieve")
    def test_failed_cached_download_does_not_advance_etag(
        self, mocked_urlretrieve, mocked_urlopen, mock_get_metadata_filename
    ):
        """A failed download leaves the prior ETag available for the next update"""
        old_etag = "ETAG_ONE"
        new_etag = "ETAG_TWO"
        url = "http://foo.com"

        cm = MagicMock()
        cm.info.return_value = {"ETag": new_etag}
        cm.__enter__.return_value = cm
        mocked_urlopen.return_value = cm
        mocked_urlretrieve.side_effect = HTTPError(
            url, 403, "Forbidden", hdrs=None, fp=None
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_file = Path(tmpdir) / "metadata.json"
            metadata_file.write_text(json.dumps({"etag": old_etag}))
            mock_get_metadata_filename.return_value = str(metadata_file)

            with self.assertRaises(HTTPError):
                cfnlint.helpers.get_url_retrieve(url, caching=True)

            self.assertEqual(json.loads(metadata_file.read_text()), {"etag": old_etag})
            self.assertTrue(cfnlint.helpers.url_has_newer_version(url))

        mocked_urlretrieve.assert_called_once_with(url)

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
