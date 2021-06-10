"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from cfnlint.decode.node import intrinsic_node,  TemplateAttributeError # pylint: disable=E0401


class TestNodeIntrinsic(BaseTestCase):

    def test_success_init(self):
        template = intrinsic_node({
            'Fn::Sub': []
        }, (0, 1), (2, 3))

        self.assertRaises(TemplateAttributeError, template.is_valid)
