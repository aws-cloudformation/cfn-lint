"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.route53.HealthCheck import HealthCheck  # pylint: disable=E0401


class TestRoute53RecordSets(BaseRuleTestCase):
    """Test CloudFront Aliases Configuration"""

    def setUp(self):
        """Setup"""
        super(TestRoute53RecordSets, self).setUp()
        self.collection.register(HealthCheck())
        self.success_templates = [
            'test/fixtures/templates/good/resources/route53/health_check.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/route53/health_check.yaml', 2)
