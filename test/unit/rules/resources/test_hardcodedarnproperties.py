"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint import ConfigMixIn
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
            "test/fixtures/templates/good/resources/properties/hard_coded_arn_properties.yaml",
            "test/fixtures/templates/good/resources/properties/hard_coded_arn_properties_sam.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        # By default, a set of "correct" templates are checked
        self.helper_file_positive()

    def test_file_positive_with_config(self):
        self.helper_file_negative(
            "test/fixtures/templates/good/resources/properties/hard_coded_arn_properties.yaml",
            0,
            ConfigMixIn(
                [],
                include_experimental=True,
                include_checks=[
                    "I",
                ],
                configure_rules={
                    "I3042": {
                        "partition": True,
                        "region": True,
                        "accountId": True,
                    }
                },
            ),
        )

    def test_file_negative_partition(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/hard_coded_arn_properties.yaml",
            2,
            ConfigMixIn(
                [],
                include_experimental=True,
                include_checks=[
                    "I",
                ],
                configure_rules={
                    "I3042": {
                        "partition": True,
                        "region": False,
                        "accountId": False,
                    }
                },
            ),
        )

    def test_file_negative_region(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/hard_coded_arn_properties.yaml",
            4,
            ConfigMixIn(
                [],
                include_experimental=True,
                include_checks=[
                    "I",
                ],
                configure_rules={
                    "I3042": {
                        "partition": False,
                        "region": True,
                        "accountId": False,
                    }
                },
            ),
        )

    def test_file_negative_accountid(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/hard_coded_arn_properties.yaml",
            1,
            ConfigMixIn(
                [],
                include_experimental=True,
                include_checks=[
                    "I",
                ],
                configure_rules={
                    "I3042": {
                        "partition": False,
                        "region": False,
                        "accountId": True,
                    }
                },
            ),
        )
