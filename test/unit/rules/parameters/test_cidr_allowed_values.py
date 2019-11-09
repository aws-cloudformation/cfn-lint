"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.parameters.CidrAllowedValues import CidrAllowedValues  # pylint: disable=E0401


class TestParameterCidrAllowedValues(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestParameterCidrAllowedValues, self).setUp()
        self.collection.register(CidrAllowedValues())

    success_templates = [
        'test/fixtures/templates/good/properties_ec2_vpc.yaml',
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_ec2_network.yaml', 3)
