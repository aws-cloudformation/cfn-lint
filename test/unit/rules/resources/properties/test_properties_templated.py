"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.PropertiesTemplated import (
    PropertiesTemplated,  # pylint: disable=E0401
)


class TestPropertiesTemplated(BaseRuleTestCase):
    """Test Resource Properties"""

    def setUp(self):
        """Setup"""
        super(TestPropertiesTemplated, self).setUp()
        self.collection.register(PropertiesTemplated())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/templated_code.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_4(self):
        """Failure test"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/templated_code.yaml", 1
        )
