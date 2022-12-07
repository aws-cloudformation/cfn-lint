"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.route53.RecordSetName import (
    RecordSetName,  # pylint: disable=E0401
)


class TestRoute53RecordSetName(BaseRuleTestCase):
    """Test CloudFront Aliases Configuration"""

    def setUp(self):
        """Setup"""
        super(TestRoute53RecordSetName, self).setUp()
        self.collection.register(RecordSetName())
        self.success_templates = [
            "test/fixtures/templates/good/resources/route53/recordset_name.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/route53/recordset_name.yaml", 4
        )
