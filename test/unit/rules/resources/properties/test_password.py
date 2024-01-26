"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.Password import (
    Password,  # pylint: disable=E0401
)


class TestPropertyPassword(BaseRuleTestCase):
    """Test Password Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyPassword, self).setUp()
        self.collection.register(Password())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/password.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_password.yaml", 3
        )
