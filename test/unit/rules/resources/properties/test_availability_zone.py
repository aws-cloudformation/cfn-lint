"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.AvailabilityZone import (
    AvailabilityZone,  # pylint: disable=E0401
)


class TestPropertyAvailabilityZone(BaseRuleTestCase):
    """Test Password Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyAvailabilityZone, self).setUp()
        self.collection.register(AvailabilityZone())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/az.yaml"
        ]

    def test_file_positive(self):
        """Success test"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Failure test"""
        self.helper_file_negative("test/fixtures/templates/bad/properties_az.yaml", 3)
