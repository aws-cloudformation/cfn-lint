"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.rds.InstanceEngine import InstanceEngine  # pylint: disable=E0401


class TestInstanceEngine(BaseRuleTestCase):
    """Test RDS Instance Size Configuration"""

    def setUp(self):
        """Setup"""
        super(TestInstanceEngine, self).setUp()
        self.collection.register(InstanceEngine())
        self.success_templates = [
            'test/fixtures/templates/good/resources/rds/instance_engine.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/rds/instance_engine.yaml', 3)
