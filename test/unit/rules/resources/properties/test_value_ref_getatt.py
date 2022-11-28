"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ValueRefGetAtt import (
    ValueRefGetAtt,  # pylint: disable=E0401
)


class TestValueRefGetAtt(BaseRuleTestCase):
    """Test Password Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestValueRefGetAtt, self).setUp()
        self.collection.register(ValueRefGetAtt())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/value.yaml",
            "test/fixtures/templates/good/properties_ec2_vpc.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/generic.yaml", 2)

    def test_file_negative_value(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/value.yaml", 8
        )

    def test_file_negative_vpc_id_value(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_vpcid.yaml", 1
        )

    def test_file_negative_az(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/parameters/az.yaml", 3)
