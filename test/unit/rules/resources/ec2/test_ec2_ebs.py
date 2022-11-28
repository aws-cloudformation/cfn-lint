"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.ectwo.Ebs import Ebs  # pylint: disable=E0401


class TestPropertyEc2Ebs(BaseRuleTestCase):
    """Test Ebs Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyEc2Ebs, self).setUp()
        self.collection.register(Ebs())
        self.success_templates = [
            "test/fixtures/templates/good/resources/ec2/ebs.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/ec2/ebs.yaml", 4
        )
