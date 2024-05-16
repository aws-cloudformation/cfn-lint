"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest
from collections import deque

from cfnlint.context import Context, Path


class TestCfnContext(unittest.TestCase):
    def test_class(self):
        context = Context()
        self.assertEqual(context.regions, ["us-east-1"])
        self.assertEqual(context.conditions, {})
        self.assertEqual(context.path, Path())

        # Test evolve
        evolved = context.evolve(
            regions=["us-west-2"],
            conditions={"Foo": True},
            path=Path(path=deque([1])),
        )
        self.assertListEqual(evolved.regions, ["us-west-2"])
        self.assertDictEqual(evolved.conditions, {"Foo": True})
        self.assertEqual(evolved.path.path, deque([1]))

        evolved_again = evolved.evolve(path=evolved.path.descend(path=2))
        self.assertListEqual(evolved_again.regions, ["us-west-2"])
        self.assertDictEqual(evolved_again.conditions, {"Foo": True})
        self.assertEqual(evolved_again.path.path, deque([1, 2]))
        # no changes to the original
        self.assertListEqual(context.regions, ["us-east-1"])
        self.assertDictEqual(context.conditions, {})
        self.assertEqual(context.path.path, deque())

        no_path = context.evolve(regions=["us-east-2"])
        self.assertListEqual(no_path.regions, ["us-east-2"])
        self.assertDictEqual(no_path.conditions, {})
        self.assertEqual(no_path.path.path, deque())
