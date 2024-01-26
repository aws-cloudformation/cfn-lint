"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.ectwo.RouteTableAssociation import (
    RouteTableAssociation,  # pylint: disable=E0401
)


class TestPropertyRtAssociation(BaseRuleTestCase):
    """Test Route Table Association"""

    def setUp(self):
        """Setup"""
        super(TestPropertyRtAssociation, self).setUp()
        self.collection.register(RouteTableAssociation())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_rt_association.yaml", 5
        )
