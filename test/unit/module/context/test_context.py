"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest
from collections import deque

from cfnlint.context import Context, Path
from cfnlint.context.conditions._conditions import Condition, Conditions
from cfnlint.context.context import Resource


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


class _CountingResources(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items_calls = 0

    def items(self):
        self.items_calls += 1
        return super().items()


class TestModuleNames(unittest.TestCase):
    def test_module_names(self):
        context = Context(
            resources={
                "MyModule": Resource({"Type": "My::Organization::Custom::MODULE"}),
                "MyBucket": Resource({"Type": "AWS::S3::Bucket"}),
            }
        )
        self.assertEqual(context.module_names, ("MyModule",))

    def test_module_names_not_computed_on_evolve(self):
        # evolve() constructs a new Context on nearly every schema-walk
        # descend, so neither construction nor evolution may scan resources;
        # the scan happens lazily on first read and is cached per instance
        resources = _CountingResources(
            {
                "MyModule": Resource({"Type": "My::Organization::Custom::MODULE"}),
                "MyBucket": Resource({"Type": "AWS::S3::Bucket"}),
            }
        )
        context = Context(resources=resources)
        evolved = context.evolve(regions=["us-west-2"]).evolve(path=Path())
        self.assertEqual(resources.items_calls, 0)

        self.assertEqual(evolved.module_names, ("MyModule",))
        self.assertEqual(resources.items_calls, 1)
        self.assertEqual(evolved.module_names, ("MyModule",))
        self.assertEqual(resources.items_calls, 1)
