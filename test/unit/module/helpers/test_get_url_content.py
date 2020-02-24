"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import gzip
try:
    import StringIO
except:
    pass
from test.testlib.testcase import BaseTestCase
from mock import patch, MagicMock
import cfnlint.helpers
import random
import string
import hashlib


class TestGetUrlContent(BaseTestCase):
    """Test Get URL Content """
    @patch('cfnlint.helpers.urlopen')
    def test_get_url_content_unzipped(self, mocked_urlopen):
        """Test success run"""

        input_buffer = '{"key": "value"}'

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = input_buffer.encode('utf-8')
        mocked_urlopen.return_value = cm

        url = 'http://foo.com'
        result = cfnlint.helpers.get_url_content(url)
        mocked_urlopen.assert_called_with(url)
        self.assertEqual(result, '{"key": "value"}')

    @patch('cfnlint.helpers.urlopen')
    def test_get_url_content_zipped(self, mocked_urlopen):
        """Test success run"""
        input_buffer = '{"key": "value"}'
        cm = MagicMock()
        cm.getcode.return_value = 200
        if sys.version_info.major == 3:
            cm.read.return_value = gzip.compress(input_buffer.encode('utf-8'))
        else:
            string_buffer = StringIO.StringIO()
            gzip_file = gzip.GzipFile(fileobj=string_buffer, mode='w', compresslevel=6)
            gzip_file.write(input_buffer)
            gzip_file.close()
            cm.read.return_value = string_buffer.getvalue()

        cm.info.return_value = {
            'Content-Encoding': 'gzip'
        }
        mocked_urlopen.return_value = cm

        url = 'http://foo.com'
        result = cfnlint.helpers.get_url_content(url)
        mocked_urlopen.assert_called_with(url)
        self.assertEqual(result, '{"key": "value"}')

    @patch('cfnlint.helpers.urlopen')
    @patch('cfnlint.helpers.get_download_metadata')
    @patch('cfnlint.helpers.save_download_metadata')
    def test_get_url_content_with_caching_zipped(self, mocked_savedowloadmetadata, mocked_getdowloadmetadata, mocked_urlopen):
        """Test success run"""

        input_buffer = '{"key": "value"}'
        # Generate a random ETag to test with
        etag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))

        url = 'http://foo.com'
        mocked_getdowloadmetadata.return_value = {
            'urls': {
                hashlib.sha256(url.encode()).hexdigest(): {
                    'etag': etag
                }
            }
        }

        cm = MagicMock()
        cm.getcode.return_value = 200
        if sys.version_info.major == 3:
            cm.read.return_value = gzip.compress(input_buffer.encode('utf-8'))
        else:
            string_buffer = StringIO.StringIO()
            gzip_file = gzip.GzipFile(fileobj=string_buffer, mode='w', compresslevel=6)
            gzip_file.write(input_buffer)
            gzip_file.close()
            cm.read.return_value = string_buffer.getvalue()

        cm.info.return_value = {
            'Content-Encoding': 'gzip',
            'ETag': etag
        }
        mocked_urlopen.return_value = cm

        result = cfnlint.helpers.get_url_content(url, caching=True)
        mocked_urlopen.assert_called_with(url)
        mocked_savedowloadmetadata.assert_not_called()
        self.assertIsNone(result)

    @patch('cfnlint.helpers.urlopen')
    @patch('cfnlint.helpers.get_download_metadata')
    @patch('cfnlint.helpers.save_download_metadata')
    def test_get_url_content_without_caching_zipped(self, mocked_savedowloadmetadata, mocked_getdowloadmetadata, mocked_urlopen):
        """Test success run"""

        input_buffer = '{"key": "value"}'
        # Generate a random ETag to test with
        etag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))
        etag2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))

        url = 'http://foo.com'
        mocked_getdowloadmetadata.return_value = {
            'urls': {
                hashlib.sha256(url.encode()).hexdigest(): {
                    'etag': etag
                }
            }
        }

        cm = MagicMock()
        cm.getcode.return_value = 200
        if sys.version_info.major == 3:
            cm.read.return_value = gzip.compress(input_buffer.encode('utf-8'))
        else:
            string_buffer = StringIO.StringIO()
            gzip_file = gzip.GzipFile(fileobj=string_buffer, mode='w', compresslevel=6)
            gzip_file.write(input_buffer)
            gzip_file.close()
            cm.read.return_value = string_buffer.getvalue()

        cm.info.return_value = {
            'Content-Encoding': 'gzip',
            'ETag': etag2
        }
        mocked_urlopen.return_value = cm

        result = cfnlint.helpers.get_url_content(url, caching=True)
        mocked_urlopen.assert_called_with(url)
        mocked_savedowloadmetadata.assert_called_once()
        self.assertEqual(result, '{"key": "value"}')