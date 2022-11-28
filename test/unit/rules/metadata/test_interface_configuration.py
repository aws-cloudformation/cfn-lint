"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.metadata.InterfaceConfiguration import (
    InterfaceConfiguration,  # pylint: disable=E0401
)


class TestOutputRequired(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestOutputRequired, self).setUp()
        self.collection.register(InterfaceConfiguration())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/metadata_interface.yaml", 2
        )
