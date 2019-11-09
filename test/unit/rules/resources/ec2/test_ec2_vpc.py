"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.ectwo.Vpc import Vpc  # pylint: disable=E0401


class TestPropertyEc2Vpc(BaseRuleTestCase):
    """Test Ec2 VPC Resources"""

    def setUp(self):
        """Setup"""
        super(TestPropertyEc2Vpc, self).setUp()
        self.collection.register(Vpc())
        self.success_templates = [
            'test/fixtures/templates/good/properties_ec2_vpc.yaml',
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_ec2_network.yaml', 3)
