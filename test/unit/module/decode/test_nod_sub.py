"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

import cfnlint.decode.node  # pylint: disable=E0401


class TestNodeSub(BaseTestCase):
    def test_success_init(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.sub_node(
            {"Fn::Sub": ["${var}", {"var": {"Ref": "AWS::Region"}}]}, (0, 1), (2, 3)
        )

        self.assertTrue(template.is_valid())
        self.assertEqual(template.get_string_vars(), set(["var"]))
        self.assertEqual(template.get_defined_vars(), {"var": {"Ref": "AWS::Region"}})
        self.assertEqual(template.get_string(), "${var}")

        template = cfnlint.decode.node.sub_node(
            {"Fn::Sub": "${AWS::Region}"}, (0, 1), (2, 3)
        )

        self.assertTrue(template.is_valid())
        self.assertEqual(template.get_string_vars(), set(["AWS::Region"]))
        self.assertEqual(template.get_defined_vars(), {})
        self.assertEqual(template.get_string(), "${AWS::Region}")

    def test_fail_init(self):
        """All the ways I can think of configuring Fn::Sub wrong"""

        # extra element in array
        template = cfnlint.decode.node.sub_node(
            {"Fn::Sub": ["{var}", {"var": {"Ref": "AWS::Region"}}, "extra element"]},
            (0, 1),
            (2, 3),
        )

        self.assertFalse(template.is_valid())

        # first element is a dict and not a string
        template = cfnlint.decode.node.sub_node(
            {
                "Fn::Sub": [
                    {"var": {"Ref": "AWS::Region"}},
                    "string",
                ]
            },
            (0, 1),
            (2, 3),
        )

        self.assertFalse(template.is_valid())

        # second element is a string not a dict
        template = cfnlint.decode.node.sub_node(
            {
                "Fn::Sub": [
                    "string",
                    "string",
                ]
            },
            (0, 1),
            (2, 3),
        )

        self.assertFalse(template.is_valid())

        # multiple elements at the Fn::Sub level
        template = cfnlint.decode.node.sub_node(
            {
                "Fn::Sub": [],
                "Fn::Join": [],
            },
            (0, 1),
            (2, 3),
        )

        self.assertFalse(template.is_valid())

        template = cfnlint.decode.node.sub_node(
            {
                "Fn::Join": [],
            },
            (0, 1),
            (2, 3),
        )

        self.assertFalse(template.is_valid())
        self.assertEqual(template.get_string_vars(), set())
        self.assertEqual(template.get_defined_vars(), {})
        self.assertEqual(template.get_string(), "")
