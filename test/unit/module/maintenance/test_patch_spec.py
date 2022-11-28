"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import test.fixtures.specs
from test.testlib.testcase import BaseTestCase

import cfnlint.helpers
from cfnlint.maintenance import patch_spec

LOGGER = logging.getLogger("cfnlint.maintenance")
LOGGER.addHandler(logging.NullHandler())


class TestPatchJson(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        region = "us-east-1"

        self.spec = cfnlint.helpers.load_resource(
            test.fixtures.specs, "%s.json" % region
        )

    def test_success_rds_dbcluster(self):
        """Success test"""
        patched = patch_spec(self.spec, "all")
        self.assertTrue(
            patched["PropertyTypes"][
                "AWS::CloudFront::Distribution.DistributionConfig"
            ]["Properties"]["DefaultCacheBehavior"]["Required"]
        )
        self.assertTrue(
            patched["PropertyTypes"][
                "AWS::CloudFront::Distribution.DistributionConfig"
            ]["Properties"]["Origins"]["Required"]
        )
        self.assertTrue(
            patched["PropertyTypes"]["AWS::Cognito::UserPool.SmsConfiguration"][
                "Properties"
            ]["ExternalId"]["Required"]
        )
        self.assertEqual(
            patched["ResourceTypes"]["AWS::ServiceDiscovery::Instance"]["Properties"][
                "InstanceAttributes"
            ]["Type"],
            "Map",
        )
        self.assertEqual(
            patched["ResourceTypes"]["AWS::ServiceDiscovery::Instance"]["Properties"][
                "InstanceAttributes"
            ]["PrimitiveItemType"],
            "String",
        )

    def test_success_sbd_domain_removed(self):
        """Success removal of SBD Domain form unsupported regions"""
        patched = patch_spec(self.spec, "us-east-2")
        self.assertNotIn("AWS::SDB::Domain", patched["ResourceTypes"])

    def test_failure_in_patch_parent(self):
        """
        Doesn't fail when a parent doesn't exist
        """
        spec = self.spec

    def test_failure_in_patch_move(self):
        """
        Doesn't fail when final key doesn't match
        """
        spec = self.spec
