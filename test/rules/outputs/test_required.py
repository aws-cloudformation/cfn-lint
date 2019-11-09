"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.outputs.Required import Required  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestOutputRequired(BaseRuleTestCase):
    """Test template parameter configurations"""
    def setUp(self):
        """Setup"""
        super(TestOutputRequired, self).setUp()
        self.collection.register(Required())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/outputs.yaml', 3)
