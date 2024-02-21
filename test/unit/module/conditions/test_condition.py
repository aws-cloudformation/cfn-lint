"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.conditions._condition import (
    ConditionAnd,
    ConditionNot,
    ConditionOr,
    ConditionUnnammed,
)
from cfnlint.conditions._utils import get_hash


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

    def test_not_a_list(self):
        """Test condition failures"""

        with self.assertRaises(ValueError):
            ConditionUnnammed({"Fn::And": {}}, {})

        with self.assertRaises(ValueError):
            ConditionUnnammed({"Condition": {}}, {})

        with self.assertRaises(ValueError):
            ConditionUnnammed({"BadKey": {}}, {})

    def test_condition_test(self):
        equals = {"Ref": "AWS::Region"}
        h = get_hash(equals)
        self.assertTrue(
            ConditionNot(
                [
                    {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                ],
                {},
            )._test(
                {h: "us-west-2"},
            )
        )
        self.assertFalse(
            ConditionNot(
                [
                    {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                ],
                {},
            )._test(
                {h: "us-east-1"},
            )
        )
        self.assertFalse(
            ConditionAnd(
                [
                    {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                    {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
                ],
                {},
            )._test(
                {h: "us-east-1"},
            )
        )
        self.assertTrue(
            ConditionOr(
                [
                    {"Fn::Equals": ["us-east-1", {"Ref": "AWS::Region"}]},
                    {"Fn::Equals": ["us-west-2", {"Ref": "AWS::Region"}]},
                ],
                {},
            )._test(
                {h: "us-east-1"},
            )
        )
