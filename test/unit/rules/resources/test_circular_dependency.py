"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.CircularDependency import (
    CircularDependency,  # pylint: disable=E0401
)


class TestRulesRefCircular(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesRefCircular, self).setUp()
        self.collection.register(CircularDependency())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        err_count = 6
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_circular_dependency.yaml", err_count
        )

    def test_file_negative_fngetatt(self):
        """Test failure"""
        err_count = 9
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_circular_dependency_2.yaml",
            err_count,
        )

    def test_file_negative_dependson(self):
        """Test failure with DependsOn"""
        err_count = 2
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_circular_dependency_dependson.yaml",
            err_count,
        )
