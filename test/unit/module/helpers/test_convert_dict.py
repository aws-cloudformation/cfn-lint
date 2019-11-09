"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
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
