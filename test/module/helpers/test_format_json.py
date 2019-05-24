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
import json
import datetime
from cfnlint.helpers import format_json_string
from testlib.testcase import BaseTestCase


class TestFormatJson(BaseTestCase):
    """Test Dumping JSON objects """

    def test_success_run(self):
        """Test success run"""
        obj = {
            'Key': {
                'SubKey': 'Value',
                'Date': datetime.datetime(2010, 9, 9)
            },
            'List': [
                {'SubKey': 'AnotherValue'}
            ]
        }
        success = """{
  "Key": {
    "Date": "2010-09-09 00:00:00",
    "SubKey": "Value"
  },
  "List": [
    {
      "SubKey": "AnotherValue"
    }
  ]
}"""
        results = format_json_string(obj)
        self.assertEqual(success, results)
