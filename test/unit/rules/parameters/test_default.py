"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.Default import Default  # pylint: disable=E0401


class TestDefault(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestDefault, self).setUp()
        self.collection.register(Default())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_parameters_success(self):
        self.helper_file_positive_template(
            "test/fixtures/templates/good/parameters/default.yaml"
        )

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/parameters/default.yaml", 9
        )
