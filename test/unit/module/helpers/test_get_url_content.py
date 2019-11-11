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
