"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import os
from test.testlib.testcase import BaseTestCase

from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.helpers import load_plugins
from cfnlint.rules import CloudFormationLintRule


class TestLoadPlugins(BaseTestCase):
    """Test loading rules."""

    def testFromDefaultDirectory(self):
        rules = load_plugins(_DEFAULT_RULESDIR)

        self.assertTrue(all(isinstance(r, CloudFormationLintRule) for r in rules))
        # From templates/Base.py
        self.assertTrue("E1001" in (r.id for r in rules))
        # From resources/Name.py
        self.assertTrue("E3006" in (r.id for r in rules))

    def testFromSubDirectory(self):
        path = os.path.join(_DEFAULT_RULESDIR, "templates")
        rules = load_plugins(path)

        self.assertTrue(all(isinstance(r, CloudFormationLintRule) for r in rules))
        self.assertTrue("E1002" in (r.id for r in rules), rules)
        self.assertFalse("E3006" in (r.id for r in rules), rules)
