"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

from cfnlint.jsonschema._utils import equal, uniq, uniq_keys


class TestUtils(unittest.TestCase):
    def test_equal(self):
        self.assertTrue(equal("foo", "foo"))
        self.assertFalse(equal("foo", "bar"))
        self.assertTrue(equal(["foo"], ["foo"]))
        self.assertFalse(equal(["foo"], ["bar"]))
        self.assertFalse(equal(["foo"], ["foo", "bar"]))
        self.assertTrue(equal({"foo": "bar"}, {"foo": "bar"}))
        self.assertFalse(equal({"foo": "bar"}, {"bar": "foo"}))
        self.assertFalse(equal({"foo": "bar"}, {"foo": "bar", "bar": "foo"}))
        self.assertTrue(equal(True, True))
        self.assertFalse(equal(True, False))
        self.assertTrue(equal(1, 1))
        self.assertFalse(equal(1, 2))

        self.assertTrue(equal(1, "1"))
        self.assertFalse(equal({"foo": "bar"}, "1"))

    def test_uniq(self):
        self.assertTrue(uniq(["foo", "bar"]))
        self.assertFalse(uniq(["foo", "foo"]))
        self.assertFalse(uniq([{"foo": "bar"}, {"foo": "bar"}]))
        self.assertTrue(uniq([{"foo": "bar"}, ["foo", "bar"]]))
        self.assertTrue(uniq([{"foo": "bar"}, {"bar": "foo"}]))

        self.assertFalse(uniq(["1", 1]))

    def test_uniq_keys(self):
        # Bad structure
        self.assertTrue(uniq_keys(["foo", "bar"], ["foo"]))

        # Unknown keys
        self.assertTrue(uniq_keys([{"foo": "foo"}, {"bar": "bar"}], ["key"]))

        # Valid and invalid configuration
        self.assertTrue(uniq_keys([{"foo": "foo"}, {"foo": "bar"}], ["foo"]))
        self.assertFalse(uniq_keys([{"foo": "foo"}, {"foo": "foo"}], ["foo"]))
        self.assertFalse(
            uniq_keys([{"foo": "foo"}, {"bar": "bar"}, {"foo": "foo"}], ["foo"])
        )
