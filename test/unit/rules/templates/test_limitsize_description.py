"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.templates.LimitDescription import LimitDescription  # pylint: disable=E0401
from test.unit.rules.templates.test_limitsize_template import write_limit_test_templates


class TestTemplateLimitDescription(BaseRuleTestCase):
    """Test template limit size"""

    def setUp(self):
        """Setup"""
        super(TestTemplateLimitDescription, self).setUp()
        self.collection.register(LimitDescription())
        write_limit_test_templates()

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/limit_size.yaml', 1)
