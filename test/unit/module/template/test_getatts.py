"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

from cfnlint.template.getatts import GetAtt, GetAtts, GetAttType


class TestGetAtts(BaseTestCase):
    """Test GetAtts Class in template"""

    def test_getatt(self):
        getatts = GetAtts(["us-east-1", "us-west-2"])
        getatts.add("Module", "Organization::Resource::Type::MODULE")
        results = getatts.match("us-east-1", "ModuleResource.Module")
        self.assertIsNone(results.type)
        self.assertEqual(results.getatt_type, GetAttType.ReadOnly)

    def test_many_modules(self):
        getatts = GetAtts(["us-east-1", "us-west-2"])
        getatts.add("Module", "Organization::Resource::Type::MODULE")
        getatts.add("Module1", "Organization::Resource::Type::MODULE")
        results = getatts.match("us-east-1", "ModuleResource.Module")
        self.assertIsNone(results.type)
        self.assertEqual(results.getatt_type, GetAttType.ReadOnly)

        results = getatts.match("us-east-1", "Module1Resource.Module")
        self.assertIsNone(results.type)
        self.assertEqual(results.getatt_type, GetAttType.ReadOnly)

    def test_getatt_resource_and_modules(self):
        getatts = GetAtts(["us-east-1", "us-west-2"])
        getatts.add("Resource", "Organization::Resource::Type::MODULE")
        getatts.add("Resource1", "Organization::Resource::Type")
        results = getatts.match("us-east-1", "ResourceOne.Module")
        self.assertIsNone(results.type)
        self.assertEqual(results.getatt_type, GetAttType.ReadOnly)

        with self.assertRaises(ValueError):
            getatts.match("us-east-1", "NoMatch.Attribute")
