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


class TestInclude(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        self.collection = Rules.create_from_directory(_DEFAULT_RULESDIR)
        self.region = "us-east-1"

    def tearDown(self):
        """Tear Down"""
        # Reset the Spec override to prevent other tests to fail
        reset()

    def test_fail_run(self):
        """Failure test required"""
        filename = "test/fixtures/templates/bad/override/include.yaml"

        PROVIDER_SCHEMA_MANAGER.patch(
            SchemaPatch(
                excluded_resource_types=[],
                included_resource_types=["AWS::EC2::*", "AWS::S3::Bucket"],
                patches={},
            ),
            region=self.region,
        )

        config = ConfigMixIn(
            regions=[self.region],
            templates=[filename],
            ignore_checks=["I", "W", "E"],
            mandatory_checks=["E3006"],
        )
        runner = Runner(config)
        runner.rules = self.collection

        errs = list(runner.run())
        self.assertEqual(2, len(errs))
