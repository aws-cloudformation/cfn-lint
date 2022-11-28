"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.updatepolicy.Configuration import (
    Configuration,  # pylint: disable=E0401
)


class TestConfiguration(BaseRuleTestCase):
    """Test Update Policy Configuration"""

    def setUp(self):
        """Setup"""
        super(TestConfiguration, self).setUp()
        self.collection.register(Configuration())
        self.success_templates = [
            "test/fixtures/templates/good/resources/updatepolicy/config.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/updatepolicy/config.yaml", 13
        )
