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
from cfnlint.rules.resources.properties.ValuePrimitiveType import ValuePrimitiveType  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestResourceValuePrimitiveType(BaseRuleTestCase):
    """Test Primitive Value Types"""
    def setUp(self):
        """Setup"""
        super(TestResourceValuePrimitiveType, self).setUp()
        self.collection.register(ValuePrimitiveType())

    success_templates = [
        'templates/good/generic.yaml',
        'templates/quickstart/nist_iam.yaml',
        'templates/quickstart/openshift_master.yaml',
        'templates/good/properties_ec2_vpc.yaml',
        'templates/good/minimal.yaml',
        'templates/good/transform.yaml',
        'templates/good/conditions.yaml',
        'templates/good/properties_elb.yaml',
        'templates/good/functions_sub.yaml',
        'templates/good/functions_cidr.yaml',
        'templates/good/functions_findinmap.yaml',
        'templates/good/resources_lambda.yaml',
        'templates/good/resources_codepipeline.yaml',
        'templates/good/transform_serverless_api.yaml',
        'templates/good/transform_serverless_function.yaml',
        'templates/good/transform_serverless_globals.yaml',
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_nist_high_master(self):
        """Generic Test failure"""
        self.helper_file_negative('templates/quickstart/nist_high_master.yaml', 6)

    def test_file_negative_nist_high_app(self):
        """Generic Test failure"""
        self.helper_file_negative('templates/quickstart/nist_application.yaml', 53)

    def test_file_negative_nist_config_rules(self):
        """Generic Test failure"""
        self.helper_file_negative('templates/quickstart/nist_config_rules.yaml', 2)

    def test_file_negative_generic(self):
        """Generic Test failure"""
        self.helper_file_negative('templates/bad/generic.yaml', 3)

    def test_file_positive_resource_properties(self):
        """Good template"""
        self.helper_file_positive_template('templates/good/resource_properties.yaml')
