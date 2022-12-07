"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
from test.testlib.testcase import BaseTestCase

import cfnlint.core
import cfnlint.helpers  # pylint: disable=E0401


class TestGetRules(BaseTestCase):
    """Test Run Checks"""

    def test_invalid_rule(self):
        """test invalid rules"""
        err = None
        try:
            cfnlint.core.get_rules(["invalid"], [], [], [], False, [])
        except cfnlint.core.UnexpectedRuleException as e:
            err = e
        assert type(err) == cfnlint.core.UnexpectedRuleException

    def test_append_module(self):
        """test appending rules from a module"""
        rules = cfnlint.core.get_rules(["test.fixtures.rules.custom1"], [], [], [])
        self.assertIn("E9001", (r.id for r in rules))
        # Make sure the default rules are there too.
        self.assertIn("E1001", (r.id for r in rules))

    def test_append_directory(self):
        """test appending rules from a directory"""
        import test.fixtures.rules

        path = os.path.dirname(test.fixtures.rules.__file__)
        rules = cfnlint.core.get_rules([path], [], [], [])
        self.assertIn("E9001", (r.id for r in rules))
        # Make sure the default rules are there too.
        self.assertIn("E1001", (r.id for r in rules))
