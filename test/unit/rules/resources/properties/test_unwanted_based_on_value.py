"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.UnwantedBasedOnValue import (
    UnwantedBasedOnValue,  # pylint: disable=E0401
)


class TestUnwantedBasedOnValue(BaseRuleTestCase):
    def setUp(self):
        """Setup"""
        super(TestUnwantedBasedOnValue, self).setUp()
        self.collection.register(UnwantedBasedOnValue())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/unwanted_based_on_value.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/unwanted_based_on_value.yaml",
            3,
        )
