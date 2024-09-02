"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest
from collections import deque

from cfnlint.context import Context, Path
from cfnlint.context.conditions._conditions import Condition, Conditions


class TestCfnContext(unittest.TestCase):
    def test_class(self):
        context = Context(
            conditions=Conditions.create_from_instance(
                conditions={
                    "Foo": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                    "Bar": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
                },
                rules={},
                parameters={},
            ),
        )
        self.assertEqual(context.regions, ["us-east-1"])
        self.assertEqual(
            context.conditions,
            Conditions(
                {
                    "Foo": Condition.create_from_instance(
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}, {}
                    ),
                    "Bar": Condition.create_from_instance(
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]}, {}
                    ),
                },
            ),
        )
        self.assertEqual(context.path, Path())

        # Test evolve
        evolved = context.evolve(
            regions=["us-west-2"],
            conditions=context.conditions.evolve(
                {"Foo": False},
            ),
            path=Path(path=deque([1])),
        )
        self.assertListEqual(evolved.regions, ["us-west-2"])
        self.assertDictEqual(
            evolved.conditions.status,
            {
                "Foo": False,
            },
        )
        self.assertEqual(evolved.path.path, deque([1]))

        evolved_again = evolved.evolve(
            path=evolved.path.descend(path=2),
            conditions=evolved.conditions.evolve(
                {"Bar": True},
            ),
        )
        self.assertListEqual(evolved_again.regions, ["us-west-2"])
        self.assertDictEqual(
            evolved_again.conditions.status, {"Foo": False, "Bar": True}
        )
        self.assertEqual(evolved_again.path.path, deque([1, 2]))
        # no changes to the original
        self.assertListEqual(context.regions, ["us-east-1"])
        self.assertEqual(
            context.conditions,
            Conditions(
                {
                    "Foo": Condition.create_from_instance(
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}, {}
                    ),
                    "Bar": Condition.create_from_instance(
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]}, {}
                    ),
                }
            ),
        )
        self.assertEqual(context.path.path, deque())

        no_path = context.evolve(regions=["us-east-2"])
        self.assertListEqual(no_path.regions, ["us-east-2"])
        self.assertEqual(
            no_path.conditions,
            Conditions(
                {
                    "Foo": Condition.create_from_instance(
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}, {}
                    ),
                    "Bar": Condition.create_from_instance(
                        {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]}, {}
                    ),
                }
            ),
        )
        self.assertEqual(no_path.path.path, deque())

        with self.assertRaises(ValueError):
            evolved_again.evolve(
                conditions=evolved_again.conditions.evolve(
                    {"Foo": True},
                ),
            )
