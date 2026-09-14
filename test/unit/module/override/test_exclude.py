"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint import ConfigMixIn
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules
from cfnlint.runner import Runner
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, SchemaPatch, reset


class TestExclude(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        self.collection = Rules.create_from_directory(_DEFAULT_RULESDIR)
        self.region = "us-east-1"

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        reset()

    def test_success_run(self):
        """Success test"""
        filename = "test/fixtures/templates/good/generic.yaml"

        PROVIDER_SCHEMA_MANAGER.patch(
            SchemaPatch(
                included_resource_types=[],
                excluded_resource_types=["AWS::GameLift::*", "AWS::S3::Bucket"],
                patches={},
            ),
            region=self.region,
        )

        config = ConfigMixIn(
            regions=[self.region],
            templates=[filename],
        )
        runner = Runner(config)
        runner.rules = self.collection

        self.assertEqual([], list(runner.run()))

    def test_fail_run(self):
        """Failure test required"""
        filename = "test/fixtures/templates/bad/override/exclude.yaml"

        PROVIDER_SCHEMA_MANAGER.patch(
            SchemaPatch(
                included_resource_types=[],
                excluded_resource_types=["AWS::GameLift::*", "AWS::S3::Bucket"],
                patches={},
            ),
            region=self.region,
        )

        config = ConfigMixIn(
            regions=[self.region],
            templates=[filename],
        )
        runner = Runner(config)
        runner.rules = self.collection

        errs = list(runner.run())
        self.assertEqual(2, len(errs))
