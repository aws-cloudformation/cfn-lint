"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.parameters.Cidr import Cidr  # pylint: disable=E0401


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
