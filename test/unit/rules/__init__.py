"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

import cfnlint.config
from cfnlint.rules import RulesCollection
from cfnlint.runner import Runner


class BaseRuleTestCase(BaseTestCase):
    """Used for Testing Rules"""

    success_templates = []

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection(
            include_rules=["I"], include_experimental=True
        )

    def helper_file_positive(self):
        """Success test"""
        for filename in self.success_templates:
            template = self.load_template(filename)
            good_runner = Runner(self.collection, filename, template, ["us-east-1"], [])
            good_runner.transform()
            failures = good_runner.run()
            assert [] == failures, "Got failures {} on {}".format(failures, filename)

    def helper_file_rule_config(self, filename, config, err_count):
        """Success test with rule config included"""
        template = self.load_template(filename)
        rule_id = list(self.collection.rules.keys())[0]
        self.collection.rules[rule_id].configure(config)
        good_runner = Runner(self.collection, filename, template, ["us-east-1"], [])
        good_runner.transform()
        failures = good_runner.run()
        self.assertEqual(
            err_count,
            len(failures),
            "Expected {} failures but got {} on {}".format(
                err_count, failures, filename
            ),
        )
        self.collection.rules[rule_id].configure(config)

    def helper_file_positive_template(self, filename):
        """Success test with template parameter"""
        template = self.load_template(filename)
        good_runner = Runner(self.collection, filename, template, ["us-east-1"], [])
        good_runner.transform()
        self.assertEqual([], good_runner.run())

    def helper_file_negative(self, filename, err_count, regions=None):
        """Failure test"""
        regions = regions or ["us-east-1"]
        template = self.load_template(filename)
        bad_runner = Runner(self.collection, filename, template, regions, [])
        bad_runner.transform()
        errs = bad_runner.run()
        self.assertEqual(err_count, len(errs))
