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
from cfnlint.rules.mappings.Used import Used  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestUsedMappings(BaseRuleTestCase):
    """Test template mapping configurations"""
    def setUp(self):
        """Setup"""
        super(TestUsedMappings, self).setUp()
        self.collection.register(Used())

    success_templates = [
        'templates/good/generic.yaml',
        'templates/quickstart/nist_high_master.yaml',
        'templates/quickstart/nist_application.yaml',
        'templates/quickstart/nist_config_rules.yaml',
        'templates/quickstart/nist_iam.yaml',
        'templates/quickstart/nist_logging.yaml',
        'templates/quickstart/nist_vpc_production.yaml',
        'templates/quickstart/openshift_master.yaml',
        'templates/quickstart/cis_benchmark.yaml',
        'templates/good/properties_ec2_vpc.yaml',
        'templates/good/minimal.yaml',
        'templates/good/transform.yaml',
        'templates/good/conditions.yaml',
        'templates/good/properties_elb.yaml',
        'templates/good/functions_sub.yaml',
        'templates/good/functions_cidr.yaml',
        'templates/good/functions_findinmap.yaml',
        'templates/good/resources_lambda.yaml',
        'templates/good/transform_serverless_api.yaml',
        'templates/good/transform_serverless_function.yaml',
        'templates/good/transform_serverless_globals.yaml',
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    # Some QuickStarts contain this warning, so we move them to negative tests
    def test_file_negative_nist_mgmt(self):
        """Test failure: nist_vpc_management.yaml"""
        self.helper_file_negative('templates/quickstart/nist_vpc_management.yaml', 1)

    def test_file_negative_openshift(self):
        """Test failure: openshift.yaml"""
        self.helper_file_negative('templates/quickstart/openshift.yaml', 1)

    def helper_file_positive_exception_template(self):
        """Test success file complex situation"""
        self.helper_file_positive_template('templates/good/mappings/used.yaml')

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('templates/bad/mappings/used.yaml', 1)
