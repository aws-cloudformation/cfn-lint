"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

import pytest

from cfnlint.jsonschema._utils import equal, find_additional_properties, uniq, uniq_keys


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


@pytest.mark.parametrize(
    "instance,schema,functions,expected",
    [
        # No additional properties
        (
            {"foo": "bar"},
            {"properties": {"foo": {}}},
            [],
            [],
        ),
        # Additional property found
        (
            {"foo": "bar", "baz": "qux"},
            {"properties": {"foo": {}}},
            [],
            ["baz"],
        ),
        # Pattern property matches
        (
            {"foo": "bar", "test123": "value"},
            {"properties": {"foo": {}}, "patternProperties": {"test[0-9]+": {}}},
            [],
            [],
        ),
        # Fn::Transform excluded when in functions
        (
            {"foo": "bar", "Fn::Transform": {"Name": "AWS::Include"}},
            {"properties": {"foo": {}}},
            ["Fn::Transform"],
            [],
        ),
        # Fn::Transform not excluded when not in functions
        (
            {"foo": "bar", "Fn::Transform": {"Name": "AWS::Include"}},
            {"properties": {"foo": {}}},
            [],
            ["Fn::Transform"],
        ),
        # Fn::Transform with other additional properties
        (
            {"foo": "bar", "Fn::Transform": {"Name": "AWS::Include"}, "extra": "val"},
            {"properties": {"foo": {}}},
            ["Fn::Transform"],
            ["extra"],
        ),
    ],
)
def test_find_additional_properties(instance, schema, functions, expected, validator):
    validator = validator.evolve(context=validator.context.evolve(functions=functions))
    result = list(find_additional_properties(validator, instance, schema))
    assert result == expected
