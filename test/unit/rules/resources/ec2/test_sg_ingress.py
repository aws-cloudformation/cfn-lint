"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.ectwo.SecurityGroupIngress import (
    SecurityGroupIngress,  # pylint: disable=E0401
)


class TestPropertySgIngress(BaseRuleTestCase):
    """Test Ec2 Security Group Ingress Rules"""

    def setUp(self):
        """Setup"""
        super(TestPropertySgIngress, self).setUp()
        self.collection.register(SecurityGroupIngress())
        self.success_templates = [
            "test/fixtures/templates/good/properties_ec2_vpc.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_sg_ingress.yaml", 1
        )
