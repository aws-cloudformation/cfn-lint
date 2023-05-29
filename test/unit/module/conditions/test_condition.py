"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from unittest import TestCase

from cfnlint.conditions.condition import ConditionNot, ConditionUnnammed


class TestCondition(TestCase):
    """Test Condition"""

    def test_not_condition(self):
        """Test not condition"""

        with self.assertRaises(ValueError):
            ConditionNot(
                [
                    {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                    {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
                ],
                {},
            )

    def test_unnamed_condition(self):
        """Test unnamed condition"""

        with self.assertRaises(ValueError):
            ConditionUnnammed(
                "equals",  # not a string
                {},
            )
