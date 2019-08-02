"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase
from cfnlint import Runner
from cfnlint.rules import RulesCollection
from cfnlint.rules.resources.Configuration import Configuration  # pylint: disable=E0401
from cfnlint.rules.resources.properties.Required import Required  # pylint: disable=E0401
import cfnlint.helpers


class TestComplete(BaseTestCase):
    """Used for Testing Rules"""

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        cfnlint.helpers.initialize_specs()

    def test_success_run(self):
        """Success test"""
        filename = 'test/fixtures/templates/good/override/complete.yaml'

        linter = cfnlint.Linter()
        linter.config.override_spec = 'test/fixtures/templates/override_spec/complete.json'
        linter.config.templates = [filename]
        linter.lint()
        self.assertEqual(0, len(linter.matches))

    def test_fail_run(self):
        """Failure test required"""
        filename = 'test/fixtures/templates/bad/override/complete.yaml'

        linter = cfnlint.Linter()
        linter.config.override_spec = 'test/fixtures/templates/override_spec/complete.json'
        linter.config.templates = [filename]
        linter.lint()
        self.assertEqual(3, len(linter.matches))
