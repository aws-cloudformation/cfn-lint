"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.StringSize import (
    StringSize,  # pylint: disable=E0401
)


class TestStringSize(BaseRuleTestCase):
    """Test List Size Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestStringSize, self).setUp()
        self.collection.register(StringSize())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_string_size(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/string_size.yaml", 3
        )
