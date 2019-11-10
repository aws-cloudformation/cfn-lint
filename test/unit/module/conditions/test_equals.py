"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import conditions


class TestEquals(BaseTestCase):
    """ Test Equals Logic """

    def test_equals(self):
        """ Test equals setup """
        template = [{'Ref': 'AWS::Region'}, 'us-east-1']
        result = conditions.Equals(template)
        self.assertTrue(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-east-1'}))
        self.assertFalse(result.test({'36305712594f5e76fbcbbe2f82cd3f850f6018e9': 'us-west-2'}))
