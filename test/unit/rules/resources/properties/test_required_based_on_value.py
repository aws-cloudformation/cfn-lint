"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.RequiredBasedOnValue import (
    RequiredBasedOnValue,  # pylint: disable=E0401
)


class TestRequiredBasedOnValue(BaseRuleTestCase):
    def setUp(self):
        """Setup"""
        super(TestRequiredBasedOnValue, self).setUp()
        self.collection.register(RequiredBasedOnValue())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/required_based_on_value.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/required_based_on_value.yaml",
            5,
        )
