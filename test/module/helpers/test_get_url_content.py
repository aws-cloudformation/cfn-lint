"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
import gzip
try:
    import StringIO
except:
    pass
from mock import patch, MagicMock
import cfnlint.helpers
from testlib.testcase import BaseTestCase


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
