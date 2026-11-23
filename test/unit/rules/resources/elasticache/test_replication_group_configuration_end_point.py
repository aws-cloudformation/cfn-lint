"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.elasticache.ReplicationGroupConfigurationEndPoint import (  # pylint: disable=E0401
    ReplicationGroupConfigurationEndPoint,
)


class TestReplicationGroupConfigurationEndPoint(BaseRuleTestCase):
    """Test ReplicationGroupConfigurationEndPoint"""

    def setUp(self):
        """Setup"""
        super(TestReplicationGroupConfigurationEndPoint, self).setUp()
        self.collection.register(ReplicationGroupConfigurationEndPoint())
        self.success_templates = [
            "test/fixtures/templates/good/resources/elasticache/replication_group_configuration_end_point.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/elasticache/replication_group_configuration_end_point.yaml",
            4,
        )
