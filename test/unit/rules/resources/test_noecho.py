"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.NoEcho import NoEcho  # pylint: disable=E0401


class TestNoEcho(BaseRuleTestCase):
    def setUp(self):
        """Setup"""
        super(TestNoEcho, self).setUp()
        self.collection.register(NoEcho())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/noecho.yaml", 2)
