"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.DependsOn import DependsOn  # pylint: disable=E0401


class TestResourceDependsOn(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestResourceDependsOn, self).setUp()
        self.collection.register(DependsOn())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_dependson.yaml", 4
        )
