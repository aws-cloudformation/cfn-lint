"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.route53.RecordSet import RecordSet  # pylint: disable=E0401


class TestRoute53RecordSets(BaseRuleTestCase):
    """Test CloudFront Aliases Configuration"""

    def setUp(self):
        """Setup"""
        super(TestRoute53RecordSets, self).setUp()
        self.collection.register(RecordSet())
        self.success_templates = ["test/fixtures/templates/good/route53.yaml"]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/route53.yaml", 31)
