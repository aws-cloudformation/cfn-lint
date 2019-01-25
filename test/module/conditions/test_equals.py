"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint import conditions
from testlib.testcase import BaseTestCase


class TestEquals(BaseTestCase):
    """ Test Equals Logic """
    def test_equals(self):
        """ Test equals setup """
        template = [{'Ref': 'AWS::Region'}, 'us-east-1']
        result = conditions.Equals(template)
        self.assertTrue(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertFalse(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-2'}))
