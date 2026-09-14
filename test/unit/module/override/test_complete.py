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


class TestComplete(BaseTestCase):
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
        filename = "test/fixtures/templates/good/override/complete.yaml"

        PROVIDER_SCHEMA_MANAGER.patch(
            SchemaPatch(
                included_resource_types=["AWS::EC2::*", "AWS::S3::*"],
                excluded_resource_types=["AWS::EC2::SpotFleet"],
                patches={
                    "AWS::S3::Bucket": [
                        {"op": "add", "path": "/required", "value": ["BucketName"]}
                    ]
                },
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
        filename = "test/fixtures/templates/bad/override/complete.yaml"

        PROVIDER_SCHEMA_MANAGER.patch(
            SchemaPatch(
                included_resource_types=["AWS::EC2::*", "AWS::S3::*"],
                excluded_resource_types=["AWS::EC2::SpotFleet"],
                patches={
                    "AWS::S3::Bucket": [
                        {"op": "add", "path": "/required", "value": ["BucketName"]}
                    ]
                },
            ),
            region=self.region,
        )

        config = ConfigMixIn(
            regions=[self.region],
            templates=[filename],
            ignore_checks=["I", "W", "E"],
            mandatory_checks=["E3001", "E3003", "E3006"],
        )
        runner = Runner(config)
        runner.rules = self.collection

        errs = list(runner.run())
        self.assertEqual(3, len(errs), errs)
