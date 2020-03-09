"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.rds.AuroraDBInstanceProperties import AuroraDBInstanceProperties  # pylint: disable=E0401


class TestAuroraDBInstanceProperties(BaseRuleTestCase):
    """Test RDS Auror Auto Scaling Configurartion"""

    def setUp(self):
        """Setup"""
        super(TestAuroraDBInstanceProperties, self).setUp()
        self.collection.register(AuroraDBInstanceProperties())
        self.success_templates = [
            'test/fixtures/templates/good/resources/rds/aurora_dbinstance_properties.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/rds/aurora_dbinstance_properties.yaml', 3)
