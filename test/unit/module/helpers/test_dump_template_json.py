"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import datetime
from test.testlib.testcase import BaseTestCase

from cfnlint.helpers import dump_template_json


class TestDumpTemplateJson(BaseTestCase):
    """Test serializing a template as JSON"""

    def test_success_run(self):
        """Key order is kept and dates are written back out as strings"""
        obj = {
            "Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}},
            "Parameters": {"Name": {"Type": "String"}},
            "Dates": [
                datetime.date(2010, 9, 9),
                datetime.datetime(2010, 9, 9, 1, 2, 3),
            ],
        }
        success = """{
  "Resources": {
    "Bucket": {
      "Type": "AWS::S3::Bucket"
    }
  },
  "Parameters": {
    "Name": {
      "Type": "String"
    }
  },
  "Dates": [
    "2010-09-09",
    "2010-09-09T01:02:03"
  ]
}"""

        self.assertEqual(success, dump_template_json(obj))

    def test_no_indent(self):
        """Test the most compact form"""
        self.assertEqual(
            '{"Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}}}',
            dump_template_json(
                {"Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}}}, indent=None
            ),
        )

    def test_unsupported_type(self):
        """A type JSON has no equivalent for is an error, not a silent null"""
        with self.assertRaises(TypeError) as e:
            dump_template_json({"Key": {"a", "b"}})

        self.assertIn("set", str(e.exception))

    def test_out_of_range_float(self):
        """NaN and Infinity are not valid JSON"""
        with self.assertRaises(ValueError):
            dump_template_json({"Key": float("nan")})
