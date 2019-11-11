"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.lmbd.FunctionMemorySize import FunctionMemorySize  # pylint: disable=E0401


class TestFunctionMemorySize(BaseRuleTestCase):
    """Test Lambda Memory Size Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestFunctionMemorySize, self).setUp()
        self.collection.register(FunctionMemorySize())
        self.success_templates = [
            'test/fixtures/templates/good/resources_lambda.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources_lambda.yaml', 3)
