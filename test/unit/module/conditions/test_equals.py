"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.conditions._equals import Equal
from cfnlint.conditions._utils import get_hash


class TestEquals(TestCase):
    """Test Equals"""

    def setUp(self) -> None:
        self.equals = {"Ref": "AWS::Region"}
        self.equals_h = get_hash(self.equals)

        self.parameter_region = {"Ref": "Region"}
        self.parameter_region_h = get_hash(self.parameter_region)

        self.parameter_env = {"Ref": "Environment"}
        self.parameter_env_h = get_hash(self.parameter_env)

        return super().setUp()

    def test_equals_error_test(self):
        """Test equals scenarios condition"""
        equal = Equal([self.equals, "us-east-1"])

        with self.assertRaises(ValueError):
            equal.test({"foo": "bar"})

    def test_equals_left_test(self):
        """Test equals scenarios condition"""
        equal = Equal([self.equals, "us-east-1"])

        self.assertTrue(equal.test({self.equals_h: "us-east-1"}))
        self.assertFalse(equal.test({self.equals_h: "us-west-2"}))

        equal = Equal([self.equals, self.parameter_region])
        self.assertTrue(
            equal.test(
                {
                    self.equals_h: self.parameter_region_h,
                    self.parameter_region_h: self.equals_h,
                }
            )
        )
        self.assertFalse(equal.test({self.equals_h: self.parameter_env_h}))

    def test_equals_left_right(self):
        """Test equals scenarios condition"""
        equal = Equal(["us-east-1", self.equals])

        self.assertTrue(equal.test({self.equals_h: "us-east-1"}))
        self.assertFalse(equal.test({self.equals_h: "us-west-2"}))

        equal = Equal([self.parameter_region, self.equals])
        self.assertTrue(
            equal.test(
                {
                    self.equals_h: self.parameter_region_h,
                    self.parameter_region_h: self.equals_h,
                }
            )
        )
        self.assertFalse(equal.test({self.equals_h: self.parameter_env_h}))

    def test_equal_string_test(self):
        """Test equals scenarios condition"""
        equal = Equal(["us-west-2", "us-east-1"])

        self.assertFalse(equal.test({"foo": "bar"}))
