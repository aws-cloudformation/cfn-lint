"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.elasticache.CacheClusterFailover import (
    CacheClusterFailover,  # pylint: disable=E0401
)


class TestElasticCacheClusterFailover(BaseRuleTestCase):
    """Test ElasticCache CacheClusterFailover"""

    def setUp(self):
        """Setup"""
        super(TestElasticCacheClusterFailover, self).setUp()
        self.collection.register(CacheClusterFailover())
        self.success_templates = [
            "test/fixtures/templates/good/resources/elasticache/cache_cluster_failover.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_artifact_failure(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/elasticache/cache_cluster_failover.yaml",
            5,
        )
