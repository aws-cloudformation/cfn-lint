"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint import conditions


class TestHash(BaseTestCase):
    """ Test gethash """

    def test_get_hash(self):
        """ Test get hash """
        self.assertEqual(
            conditions.get_hash({'Ref': 'AWS::NoValue'}),
            'f59194a5833190961f28f921cedf05825d749193')

        self.assertEqual(
            conditions.get_hash({'Fn::FindInMap': ['MapName', {'Ref': 'AWS::Region'}, 'AmiId']}),
            '21f3e3d3b41d4ddbd3a6af7b29c107e6ccbe84e7'
        )
