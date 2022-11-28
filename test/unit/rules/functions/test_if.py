"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.If import If  # pylint: disable=E0401


class TestIf(BaseRuleTestCase):
    """Test Rules If conditions exist"""

    def setUp(self):
        """Setup"""
        super(TestIf, self).setUp()
        self.collection.register(If())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/functions/if.yaml", 3)
