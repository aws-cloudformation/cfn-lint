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
from cfnlint.rules.parameters.Cidr import Cidr  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestParameterCidr(BaseRuleTestCase):
    """Test template parameter configurations"""
    def setUp(self):
        """Setup"""
        super(TestParameterCidr, self).setUp()
        self.collection.register(Cidr())

    success_templates = [
        'test/fixtures/templates/good/functions_cidr.yaml',
        'test/fixtures/templates/good/properties_ec2_vpc.yaml',
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_nist_app(self):
        """Failure test"""
        self.helper_file_negative('test/fixtures/templates/quickstart/nist_application.yaml', 2)

    def test_file_negative_nist_mgmt(self):
        """Failure test"""
        self.helper_file_negative('test/fixtures/templates/quickstart/nist_vpc_management.yaml', 7)

    def test_file_negative_nist_prod(self):
        """Failure test"""
        self.helper_file_negative('test/fixtures/templates/quickstart/nist_vpc_production.yaml', 9)

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_ec2_network.yaml', 1)
