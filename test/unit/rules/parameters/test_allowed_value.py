"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.AllowedValue import AllowedValue  # pylint: disable=E0401


class TestAllowedValue(BaseRuleTestCase):
    """Test Allowed Value Parameter Configuration"""

    def setUp(self):
        """Setup"""
        super(TestAllowedValue, self).setUp()
        self.collection.register(AllowedValue())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/allowed_values.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/allowed_values.yaml", 2
        )
