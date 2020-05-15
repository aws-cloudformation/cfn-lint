"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.HardCodedArnProperties import HardCodedArnProperties  # pylint: disable=E0401



class TestHardCodedArnProperties(BaseRuleTestCase):
    """Test template parameter configurations"""
    def setUp(self):
        """Setup"""
        super(TestHardCodedArnProperties, self).setUp()
        self.collection.register(HardCodedArnProperties())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive() # By default, a set of "correct" templates are checked

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/hard_coded_arn_properties.yaml', 5) # Amount of expected matches