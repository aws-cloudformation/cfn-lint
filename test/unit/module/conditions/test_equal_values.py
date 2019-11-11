"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import conditions


class TestEquals(BaseTestCase):
    """ Test Equals Logic """

    def test_equal_value_string(self):
        """ Test equals setup """
        template = 'us-east-1'
        result = conditions.EqualsValue(template)
        self.assertTrue(result == 'us-east-1')
        self.assertFalse(result == 'us-west-2')
