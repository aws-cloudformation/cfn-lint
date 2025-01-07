"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import os
from test.testlib.testcase import BaseTestCase

from cfnlint.config import ConfigMixIn
from cfnlint.exceptions import UnexpectedRuleException
from cfnlint.runner import Runner


class TestGetRules(BaseTestCase):
    """Test Run Checks"""

    def test_invalid_rule(self):
        """test invalid rules"""
        err = None
        config = ConfigMixIn(
            append_rules=["invalid"],
        )

        try:
            Runner(config)
        except UnexpectedRuleException as e:
            err = e
        self.assertIsInstance(err, UnexpectedRuleException)

    def test_append_module(self):
        """test appending rules from a module"""
        config = ConfigMixIn(
            append_rules=["test.fixtures.rules.custom1"],
        )
        runner = Runner(config)
        self.assertIn("E9001", runner.rules)
        # Make sure the default rules are there too.
        self.assertIn("E1001", runner.rules)

    def test_append_directory(self):
        """test appending rules from a directory"""
        import test.fixtures.rules

        path = os.path.dirname(test.fixtures.rules.__file__)
        config = ConfigMixIn(
            append_rules=[path],
        )
        runner = Runner(config)
        self.assertIn("E9001", runner.rules)
        # Make sure the default rules are there too.
        self.assertIn("E1001", runner.rules)
