"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.outputs.Name import Name  # pylint: disable=E0401


class TestName(BaseRuleTestCase):
    """Test template outputs Names"""

    def setUp(self):
        """Setup"""
        super(TestName, self).setUp()
        self.collection.register(Name())
        self.success_templates = ["test/fixtures/templates/good/outputs/name.yaml"]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/outputs/name.yaml", 1)
