"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import json
import logging
import pkg_resources
from cfnlint.maintenance import patch_spec
from testlib.testcase import BaseTestCase

LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())

class TestPatchJson(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        region = 'us-east-1'
        filename = pkg_resources.resource_filename(
            __name__,
            '../../fixtures/specs/%s.json' % region,
        )
        with open(filename, 'r') as f:
            self.spec = json.loads(f.read())

    def test_success_rds_dbcluster(self):
        """Success test"""
        patched = patch_spec(self.spec, 'us-east-1')
        self.assertTrue(
            patched['PropertyTypes']['AWS::CloudFront::Distribution.DistributionConfig']['Properties']['DefaultCacheBehavior']['Required'])
        self.assertTrue(
            patched['PropertyTypes']['AWS::CloudFront::Distribution.DistributionConfig']['Properties']['Origins']['Required'])
        self.assertIn('VpcEndpointType', patched['ResourceTypes']['AWS::EC2::VPCEndpoint']['Properties'])
        self.assertIn('Tags', patched['PropertyTypes']['AWS::EC2::SpotFleet.SpotFleetTagSpecification']['Properties'])
        self.assertTrue(patched['PropertyTypes']['AWS::Cognito::UserPool.SmsConfiguration']['Properties']['ExternalId']['Required'])
        self.assertIn('AWS::CloudFormation::Macro', patched['ResourceTypes'])
        self.assertTrue(patched['ResourceTypes']['AWS::SNS::Subscription']['Properties']['TopicArn']['Required'])
        self.assertTrue(patched['ResourceTypes']['AWS::SNS::Subscription']['Properties']['Protocol']['Required'])

    def test_success_sbd_domain_removed(self):
        """Success removal of SBD Domain form unsupported regions"""
        patched = patch_spec(self.spec, 'us-east-2')
        self.assertNotIn('AWS::SDB::Domain', patched['ResourceTypes'])

    def test_failure_in_patch_parent(self):
        """
            Doesn't fail when a parent doesn't exist
        """
        spec = self.spec
        del spec['ResourceTypes']['AWS::SNS::Subscription']
        patched = patch_spec(spec, 'us-east-1')
        self.assertNotIn('AWS::SNS::Subscription', patched['ResourceTypes'])

    def test_failure_in_patch_move(self):
        """
            Doesn't fail when final key doesn't match
        """
        spec = self.spec
        del spec['ResourceTypes']['AWS::EC2::VPCEndpoint']['Properties']['VPCEndpointType']
        patched = patch_spec(spec, 'us-east-1')
        self.assertNotIn('VPCEndpointType', patched['ResourceTypes']['AWS::EC2::VPCEndpoint']['Properties'])
