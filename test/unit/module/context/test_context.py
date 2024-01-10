"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest
from collections import deque

from cfnlint.context import Context


class TestCfnContext(unittest.TestCase):
    def test_class(self):
        context = Context()
        self.assertEqual(context.regions, ["us-east-1"])
        self.assertEqual(context.conditions, {})
        self.assertEqual(context.path, deque())

        # Test evolve
        evolved = context.evolve(
            regions=["us-west-2"],
            conditions={"Foo": True},
            path=1,
        )
        self.assertListEqual(evolved.regions, ["us-west-2"])
        self.assertDictEqual(evolved.conditions, {"Foo": True})
        self.assertEqual(evolved.path, deque([1]))

        evolved_again = evolved.evolve(path=2)
        self.assertListEqual(evolved_again.regions, ["us-west-2"])
        self.assertDictEqual(evolved_again.conditions, {"Foo": True})
        self.assertEqual(evolved_again.path, deque([1, 2]))
        # no changes to the original
        self.assertListEqual(context.regions, ["us-east-1"])
        self.assertDictEqual(context.conditions, {})
        self.assertEqual(context.path, deque())

        no_path = context.evolve(regions=["us-east-2"])
        self.assertListEqual(no_path.regions, ["us-east-2"])
        self.assertDictEqual(no_path.conditions, {})
        self.assertEqual(no_path.path, deque())
