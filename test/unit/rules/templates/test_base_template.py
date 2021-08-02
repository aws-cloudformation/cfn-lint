"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.templates.Base import Base  # pylint: disable=E0401


class TestBaseTemplate(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestBaseTemplate, self).setUp()
        self.collection.register(Base())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_positive_configured(self):
        self.helper_file_rule_config(
            'test/fixtures/templates/bad/generic.yaml',
            {
                'sections': 'Errors',
            }, 0
        )

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/generic.yaml', 1)
