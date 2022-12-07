"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase

import cfnlint.helpers
from cfnlint.rules import RulesCollection
from cfnlint.rules.resources.Configuration import Configuration  # pylint: disable=E0401
from cfnlint.runner import Runner


class TestExclude(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection()
        self.collection.register(Configuration())

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        cfnlint.helpers.initialize_specs()

    def test_success_run(self):
        """Success test"""
        filename = "test/fixtures/templates/good/generic.yaml"
        template = self.load_template(filename)
        with open("test/fixtures/templates/override_spec/exclude.json") as fp:
            custom_spec = json.load(fp)

        cfnlint.helpers.set_specs(custom_spec)

        good_runner = Runner(self.collection, filename, template, ["us-east-1"], [])
        self.assertEqual([], good_runner.run())

    def test_fail_run(self):
        """Failure test required"""
        filename = "test/fixtures/templates/bad/override/exclude.yaml"
        template = self.load_template(filename)

        with open("test/fixtures/templates/override_spec/exclude.json") as fp:
            custom_spec = json.load(fp)
        cfnlint.helpers.set_specs(custom_spec)

        bad_runner = Runner(self.collection, filename, template, ["us-east-1"], [])
        errs = bad_runner.run()
        self.assertEqual(2, len(errs))
