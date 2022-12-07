"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.rds.InstanceSize import (
    InstanceSize,  # pylint: disable=E0401
)


class TestInstanceSize(BaseRuleTestCase):
    """Test RDS Instance Size Configuration"""

    def setUp(self):
        """Setup"""
        super(TestInstanceSize, self).setUp()
        self.collection.register(InstanceSize())
        self.success_templates = [
            "test/fixtures/templates/good/resources/rds/instance_sizes.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/rds/instance_sizes.yaml",
            7,
            ["us-east-1", "eu-west-3"],
        )
