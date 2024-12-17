"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase
from typing import List

from cfnlint import ConfigMixIn, Rules
from cfnlint.config import ManualArgs
from cfnlint.runner.template.runner import _run_template


class BaseRuleTestCase(BaseTestCase):
    """Used for Testing Rules"""

    success_templates: List[str] = []

    def setUp(self):
        """Setup"""
        self.collection = Rules()
        self.config = ConfigMixIn(
            include_experimental=True,
            include_checks=["I"],
        )

    def helper_file_positive(self, config=None):
        """Success test"""
        config = config or self.config
        for filename in self.success_templates:
            template = self.load_template(filename)
            failures = list(_run_template(filename, template, config, self.collection))
            self.assertEqual(
                [], failures, "Got failures {} on {}".format(failures, filename)
            )

    def helper_file_positive_template(self, filename, config=None):
        """Success test with template parameter"""
        config = config or self.config
        template = self.load_template(filename)
        failures = list(_run_template(filename, template, config, self.collection))
        self.assertEqual(
            [],
            failures,
            "Expected {} failures but got {} on {}".format(0, failures, filename),
        )

    def helper_file_negative(self, filename, err_count, config=None):
        """Failure test"""
        config = config or self.config
        template = self.load_template(filename)
        failures = list(_run_template(filename, template, config, self.collection))
        self.assertEqual(
            err_count,
            len(failures),
            "Expected {} failures but got {} on {}".format(
                err_count, failures, filename
            ),
        )
