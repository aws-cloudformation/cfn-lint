"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.HardCodedArnProperties import (
    HardCodedArnProperties,  # pylint: disable=E0401
)


class TestHardCodedArnProperties(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestHardCodedArnProperties, self).setUp()
        self.collection.register(HardCodedArnProperties())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/hard_coded_arn_properties_sam.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()  # By default, a set of "correct" templates are checked

    def test_file_negative_partition(self):
        self.helper_file_rule_config(
            "test/fixtures/templates/bad/hard_coded_arn_properties.yaml",
            {
                "partition": True,
                "region": False,
                "accountId": False,
            },
            2,
        )

    def test_file_negative_region(self):
        self.helper_file_rule_config(
            "test/fixtures/templates/bad/hard_coded_arn_properties.yaml",
            {
                "partition": False,
                "region": True,
                "accountId": False,
            },
            4,
        )

    def test_file_negative_accountid(self):
        self.helper_file_rule_config(
            "test/fixtures/templates/bad/hard_coded_arn_properties.yaml",
            {
                "partition": False,
                "region": False,
                "accountId": True,
            },
            1,
        )
