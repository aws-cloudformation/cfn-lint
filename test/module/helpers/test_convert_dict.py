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
import json
from cfnlint.helpers import convert_dict
from cfnlint.decode.node import dict_node, list_node, str_node
from cfnlint import Runner
import cfnlint.decode.cfn_yaml
from testlib.testcase import BaseTestCase


class TestConvertDict(BaseTestCase):
    """Test Converting regular dicts into CFN Dicts """

    def test_success_run(self):
        """Test success run"""
        obj = {
            'Key': {
                'SubKey': 'Value'
            },
            'List': [
                {'SubKey': 'AnotherValue'}
            ]
        }

        results = convert_dict(obj)
        self.assertTrue(isinstance(results, dict_node))
        self.assertTrue(isinstance(results.get('Key'), dict_node))
        self.assertTrue(isinstance(results.get('List')[0], dict_node))
        self.assertTrue(isinstance(results.get('List'), list_node))
        for k, _ in results.items():
            self.assertTrue(isinstance(k, str_node))
