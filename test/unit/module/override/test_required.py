"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase

import cfnlint.helpers
from cfnlint.rules import RulesCollection
from cfnlint.rules.resources.properties.JsonSchema import (
    JsonSchema,  # pylint: disable=E0401
)
from cfnlint.rules.resources.properties.Required import (
    Required,  # pylint: disable=E0401
)
from cfnlint.runner import Runner
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER
from cfnlint.schema.patch import SchemaPatch


class TestOverrideRequired(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection()
        self.collection.register(JsonSchema())
        self.collection.register(Required())
        self.region = "us-east-1"

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        PROVIDER_SCHEMA_MANAGER.reset()

    def test_success_run(self):
        """Success test"""
        filename = "test/fixtures/templates/good/override/required.yaml"
        template = self.load_template(filename)

        PROVIDER_SCHEMA_MANAGER.patch(
            "test/fixtures/templates/override_spec/required.json", regions=[self.region]
        )

        good_runner = Runner(self.collection, filename, template, [self.region], [])
        self.assertEqual([], good_runner.run())

    def test_fail_run(self):
        """Failure test required"""
        filename = "test/fixtures/templates/bad/override/required.yaml"
        template = self.load_template(filename)

        PROVIDER_SCHEMA_MANAGER.patch(
            "test/fixtures/templates/override_spec/required.json", regions=[self.region]
        )

        bad_runner = Runner(self.collection, filename, template, [self.region], [])
        errs = bad_runner.run()
        self.assertEqual(1, len(errs))
