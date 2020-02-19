"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.rds.AuroraScalingConfiguration import AuroraScalingConfiguration  # pylint: disable=E0401


class TestAuroraScalingConfiguration(BaseRuleTestCase):
    """Test RDS Auror Auto Scaling Configurartion"""

    def setUp(self):
        """Setup"""
        super(TestAuroraScalingConfiguration, self).setUp()
        self.collection.register(AuroraScalingConfiguration())
        self.success_templates = [
            'test/fixtures/templates/good/resources/rds/aurora_autoscaling.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/rds/aurora_autoscaling.yaml', 1)
