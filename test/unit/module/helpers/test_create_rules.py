"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.helpers import create_rules
from cfnlint.rules import CloudFormationLintRule


class TestCreateRules(BaseTestCase):
    """Test creating rules from a module."""

    def testBase(self):
        from cfnlint.rules.jsonschema import JsonSchema

        rules = create_rules(JsonSchema)
        self.assertTrue(all(isinstance(r, CloudFormationLintRule) for r in rules))
        self.assertTrue("E1001" in (r.id for r in rules))
