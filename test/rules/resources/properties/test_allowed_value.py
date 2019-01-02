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
from cfnlint.rules.resources.properties.AllowedValue import AllowedValue  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestAllowedValue(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""
    def setUp(self):
        """Setup"""
        super(TestAllowedValue, self).setUp()
        self.collection.register(AllowedValue())
        self.success_templates = [
            'test/fixtures/templates/good/resources_lambda.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_runtime(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources_lambda.yaml', 3)

    def test_file_negative_recordset(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/route53.yaml', 1)

    def test_file_negative_ebsvolume(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_ebs.yaml', 1)

    def test_file_negative_vpctenancy(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_ec2_network.yaml', 2)
