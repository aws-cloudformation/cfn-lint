"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import datetime
from test.testlib.testcase import BaseTestCase

from cfnlint.helpers import format_json_string


class TestFormatJson(BaseTestCase):
    """Test Dumping JSON objects"""

    def test_success_run(self):
        """Test success run"""
        obj = {
            "Key": {"SubKey": "Value", "Date": datetime.datetime(2010, 9, 9)},
            "List": [{"SubKey": "AnotherValue"}],
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
