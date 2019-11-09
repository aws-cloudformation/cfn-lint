"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import logging
import test.fixtures.specs
from test.testlib.testcase import BaseTestCase
import cfnlint.helpers
from cfnlint.maintenance import patch_spec


LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())


class TestPatchJson(BaseTestCase):
    """Used for Testing Rules"""

    def setUp(self):
        """Setup"""
        region = 'us-east-1'

        self.spec = cfnlint.helpers.load_resource(test.fixtures.specs, '%s.json' % region)

    def test_success_rds_dbcluster(self):
        """Success test"""
        patched = patch_spec(self.spec, 'all')
        self.assertTrue(
            patched['PropertyTypes']['AWS::CloudFront::Distribution.DistributionConfig']['Properties']['DefaultCacheBehavior']['Required'])
        self.assertTrue(
            patched['PropertyTypes']['AWS::CloudFront::Distribution.DistributionConfig']['Properties']['Origins']['Required'])
        self.assertTrue(patched['PropertyTypes']['AWS::Cognito::UserPool.SmsConfiguration']
                        ['Properties']['ExternalId']['Required'])
        self.assertEqual(patched['ResourceTypes']['AWS::ServiceDiscovery::Instance']
                         ['Properties']['InstanceAttributes']['Type'], 'Map')
        self.assertEqual(patched['ResourceTypes']['AWS::ServiceDiscovery::Instance']
                         ['Properties']['InstanceAttributes']['PrimitiveItemType'], 'String')

    def test_success_sbd_domain_removed(self):
        """Success removal of SBD Domain form unsupported regions"""
        patched = patch_spec(self.spec, 'us-east-2')
        self.assertNotIn('AWS::SDB::Domain', patched['ResourceTypes'])

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
