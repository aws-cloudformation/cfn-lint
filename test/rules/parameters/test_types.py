"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.parameters.Types import Types  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestParameterTypes(BaseRuleTestCase):
    """Test template parameter configurations"""
    def setUp(self):
        """Set up"""
        super(TestParameterTypes, self).setUp()
        self.collection.register(Types())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/parameters.yaml', 1)
