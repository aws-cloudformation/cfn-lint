"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.Configuration import Configuration  # pylint: disable=E0401


class TestResourceConfiguration(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestResourceConfiguration, self).setUp()
        self.collection.register(Configuration())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/generic.yaml", 2)
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/configuration.yaml", 3
        )
