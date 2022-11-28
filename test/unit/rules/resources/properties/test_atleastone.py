"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.AtLeastOne import (
    AtLeastOne,  # pylint: disable=E0401
)


class TestPropertyAtLeastOne(BaseRuleTestCase):
    """Test AtLeastOne Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyAtLeastOne, self).setUp()
        self.collection.register(AtLeastOne())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/atleastone.yaml", 2
        )
