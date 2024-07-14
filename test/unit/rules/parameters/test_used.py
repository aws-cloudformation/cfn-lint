"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.Used import Used  # pylint: disable=E0401


class TestParameterUsed(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestParameterUsed, self).setUp()
        self.collection.register(Used())
        self.success_templates = [
            "test/fixtures/templates/good/parameters/used_transforms.yaml",
            "test/fixtures/templates/good/parameters/used_transform_removed.yaml",
            "test/fixtures/templates/good/parameters/used_transform_language_extension.json",
            "test/fixtures/templates/good/parameters/not_used_parameters.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/parameters/configuration.yaml", 17
        )
